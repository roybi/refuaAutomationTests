"""Read-only schema discovery for the Meditik DB: tables, columns, keys, FKs, triggers.

Outputs catalog metadata only (never row data) so relationships and insert order
can be learned before any seeding.

    venv\\Scripts\\python.exe tools\\db_discover_schema.py --env test
    venv\\Scripts\\python.exe tools\\db_discover_schema.py --env test --tables medicine,prescription
    venv\\Scripts\\python.exe tools\\db_discover_schema.py --env test --json docs/db/meditik_schema_test.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ENVS = ("test", "preprod")
SOFT_DELETE_HINTS = ("deleted", "is_deleted", "deleted_at", "is_active", "active", "status", "removed")

COLUMNS_SQL = """
SELECT c.table_schema, c.table_name, c.column_name, c.data_type, c.is_nullable,
       c.column_default, c.is_identity, c.is_generated, c.ordinal_position
FROM information_schema.columns c
JOIN information_schema.tables t
  ON t.table_schema = c.table_schema AND t.table_name = c.table_name
WHERE c.table_schema = ANY(%s) AND t.table_type = 'BASE TABLE'
ORDER BY c.table_schema, c.table_name, c.ordinal_position
"""

CONSTRAINTS_SQL = """
SELECT n.nspname AS table_schema, cl.relname AS table_name, con.conname AS name,
       con.contype AS type, pg_get_constraintdef(con.oid) AS definition,
       fn.nspname AS ref_schema, fcl.relname AS ref_table,
       ARRAY(SELECT a.attname FROM unnest(con.conkey) k
             JOIN pg_attribute a ON a.attrelid = con.conrelid AND a.attnum = k) AS columns,
       ARRAY(SELECT a.attname FROM unnest(con.confkey) k
             JOIN pg_attribute a ON a.attrelid = con.confrelid AND a.attnum = k) AS ref_columns
FROM pg_constraint con
JOIN pg_class cl ON cl.oid = con.conrelid
JOIN pg_namespace n ON n.oid = cl.relnamespace
LEFT JOIN pg_class fcl ON fcl.oid = con.confrelid
LEFT JOIN pg_namespace fn ON fn.oid = fcl.relnamespace
WHERE n.nspname = ANY(%s) AND con.contype IN ('p', 'f', 'u', 'c')
ORDER BY 1, 2, 3
"""

TRIGGERS_SQL = """
SELECT n.nspname AS table_schema, c.relname AS table_name, t.tgname AS name,
       pg_get_triggerdef(t.oid) AS definition
FROM pg_trigger t
JOIN pg_class c ON c.oid = t.tgrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = ANY(%s) AND NOT t.tgisinternal
ORDER BY 1, 2, 3
"""

ROWCOUNT_SQL = """
SELECT n.nspname AS table_schema, c.relname AS table_name, c.reltuples::bigint AS approx_rows
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = ANY(%s) AND c.relkind = 'r'
"""

SERVER_IDENTITY_SQL = (
    "SELECT current_database() AS db, current_user AS usr, "
    "current_setting('server_version') AS version, inet_server_port() AS port"
)


def _fetch(cur, sql: str, params=None) -> list[dict]:
    cur.execute(sql, params)
    cols = [c.name for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def discover(schemas: list[str]) -> dict:
    from refua_core.config.database import DatabaseManager

    with DatabaseManager().get_connection() as conn:
        conn.set_session(readonly=True, autocommit=False)
        with conn.cursor() as cur:
            cur.execute("SET LOCAL statement_timeout = '30s'")
            cur.execute("SET LOCAL lock_timeout = '5s'")
            identity = _fetch(cur, SERVER_IDENTITY_SQL)[0]
            columns = _fetch(cur, COLUMNS_SQL, (schemas,))
            constraints = _fetch(cur, CONSTRAINTS_SQL, (schemas,))
            triggers = _fetch(cur, TRIGGERS_SQL, (schemas,))
            rowcounts = _fetch(cur, ROWCOUNT_SQL, (schemas,))
        conn.rollback()

    tables: dict[str, dict] = {}
    for col in columns:
        key = f"{col['table_schema']}.{col['table_name']}"
        tbl = tables.setdefault(key, {"columns": [], "pk": [], "fks": [], "unique": [], "checks": [],
                                      "triggers": [], "soft_delete_candidates": [], "approx_rows": None})
        tbl["columns"].append({
            "name": col["column_name"],
            "type": col["data_type"],
            "nullable": col["is_nullable"] == "YES",
            "default": col["column_default"],
            "identity": col["is_identity"] == "YES",
            "generated": col["is_generated"] == "ALWAYS",
        })
        if col["column_name"].lower() in SOFT_DELETE_HINTS:
            tbl["soft_delete_candidates"].append(col["column_name"])

    for con in constraints:
        tbl = tables.get(f"{con['table_schema']}.{con['table_name']}")
        if tbl is None:
            continue
        if con["type"] == "p":
            tbl["pk"] = list(con["columns"])
        elif con["type"] == "f":
            tbl["fks"].append({
                "name": con["name"],
                "columns": list(con["columns"]),
                "ref_table": f"{con['ref_schema']}.{con['ref_table']}",
                "ref_columns": list(con["ref_columns"]),
                "definition": con["definition"],
            })
        elif con["type"] == "u":
            tbl["unique"].append(list(con["columns"]))
        elif con["type"] == "c":
            tbl["checks"].append(con["definition"])

    for trg in triggers:
        tbl = tables.get(f"{trg['table_schema']}.{trg['table_name']}")
        if tbl is not None:
            tbl["triggers"].append(trg["definition"])

    for rc in rowcounts:
        tbl = tables.get(f"{rc['table_schema']}.{rc['table_name']}")
        if tbl is not None:
            tbl["approx_rows"] = rc["approx_rows"]

    return {"server": identity, "schemas": schemas, "tables": tables, "insert_order": insert_order(tables)}


def insert_order(tables: dict[str, dict]) -> list[str]:
    """Topological order: parents before children (self-references ignored)."""
    deps: dict[str, set[str]] = {t: set() for t in tables}
    children: dict[str, set[str]] = defaultdict(set)
    for name, tbl in tables.items():
        for fk in tbl["fks"]:
            parent = fk["ref_table"]
            if parent != name and parent in tables:
                deps[name].add(parent)
                children[parent].add(name)
    queue = deque(sorted(t for t, d in deps.items() if not d))
    order: list[str] = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for child in sorted(children[node]):
            deps[child].discard(node)
            if not deps[child]:
                queue.append(child)
    order.extend(sorted(t for t in tables if t not in order))  # cycles, if any
    return order


def related_closure(tables: dict[str, dict], seeds: list[str]) -> set[str]:
    """Selected tables plus all ancestors (required parents) and direct children."""
    result = set(seeds)
    stack = list(seeds)
    while stack:
        name = stack.pop()
        for fk in tables.get(name, {}).get("fks", []):
            if fk["ref_table"] not in result:
                result.add(fk["ref_table"])
                stack.append(fk["ref_table"])
    for name, tbl in tables.items():
        if any(fk["ref_table"] in seeds for fk in tbl["fks"]):
            result.add(name)
    return result


def print_report(data: dict, only: set[str] | None) -> None:
    srv = data["server"]
    print(f"# DB {srv['db']} | user {srv['usr']} | PostgreSQL {srv['version']} | schemas {data['schemas']}\n")
    for name in data["insert_order"]:
        if only and name not in only:
            continue
        tbl = data["tables"][name]
        print(f"## {name}  (~{tbl['approx_rows']} rows)  PK={tbl['pk']}")
        for col in tbl["columns"]:
            flags = []
            if not col["nullable"]:
                flags.append("NOT NULL")
            if col["identity"]:
                flags.append("IDENTITY")
            if col["default"]:
                flags.append(f"default={col['default']}")
            print(f"    {col['name']}: {col['type']} {' '.join(flags)}")
        for fk in tbl["fks"]:
            print(f"    FK {fk['columns']} -> {fk['ref_table']}{fk['ref_columns']}")
        for uq in tbl["unique"]:
            print(f"    UNIQUE {uq}")
        for chk in tbl["checks"]:
            print(f"    {chk}")
        for trg in tbl["triggers"]:
            print(f"    TRIGGER {trg}")
        if tbl["soft_delete_candidates"]:
            print(f"    soft-delete candidates: {tbl['soft_delete_candidates']}")
        print()
    print("# Insert order (parents first):")
    print("  " + " -> ".join(n for n in data["insert_order"] if not only or n in only))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env", required=True, choices=ALLOWED_ENVS)
    parser.add_argument("--schemas", default="public,history")
    parser.add_argument("--tables", default="", help="Comma list of table names (schema optional) to focus on")
    parser.add_argument("--json", default="", help="Write the full metadata map to this path")
    args = parser.parse_args()

    env_file = REPO_ROOT / f".env.{args.env}"
    if not env_file.exists():
        print(f"Missing {env_file.name}", file=sys.stderr)
        return 2
    load_dotenv(env_file, override=True)

    schemas = [s.strip() for s in args.schemas.split(",") if s.strip()]
    data = discover(schemas)

    only = None
    if args.tables:
        wanted = []
        for t in (x.strip() for x in args.tables.split(",") if x.strip()):
            wanted.extend(n for n in data["tables"] if n == t or n.split(".", 1)[1] == t)
        only = related_closure(data["tables"], wanted)

    print_report(data, only)
    if args.json:
        out = REPO_ROOT / args.json
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, default=str, ensure_ascii=False), encoding="utf-8")
        print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
