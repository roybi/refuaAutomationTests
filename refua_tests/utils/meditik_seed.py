"""Direct-DB seeding of Meditik user requests for UI tests (TEST only until PREPROD is verified).

Verified relationships (TEST, schema public, 2026-09-27, see tools/db_discover_schema.py):
    request_type / request_state + child reference rows (never modified)
        -> user_request (patient_military_id = personal number, patient_person_id = create_user)
            -> referral_request               types 1-4 (unique request_id)
            -> prescription_request           type 5 (N per request)
            -> (no child)                     types 6, 7 refunds (attachments need Hatch, not seeded)
            -> insoles_request -> insoles_chain                          type 8
            -> retroactive_commitment_request -> er_facility/reason/source type 9
            -> sick_days_request              type 10
            -> optic_request -> optic_chain                              type 11
Medicines/prescription catalog data is NOT stored in this DB (it comes from external systems),
so only request entities can be seeded here.

No table in this graph has a soft-delete column. Cleanup is therefore "report" by default;
"delete-owned" removes only this run's exact IDs (AFTER DELETE triggers archive them to history.*).
"""

from __future__ import annotations

import calendar
import json
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo

from dotenv import dotenv_values

REPO_ROOT = Path(__file__).resolve().parents[2]
TZ = ZoneInfo("Asia/Jerusalem")
MANIFEST_DIR = Path(os.getenv("MEDITIK_SEED_MANIFEST_DIR", Path.home() / ".refua_seeds"))

# Server-side identity required per environment; PREPROD stays blocked until its DB is verified.
VERIFIED_TARGETS = {"test": {"database": "meditik", "schema": "public"}}
ALLOWED_ENVS = ("test", "preprod")

REQUEST_STATE_SAVED = 1  # INITIAL_REQUEST_STATE; shown in the lobby "new requests" tab
PRESCRIPTION_TYPE_OTHER = 3
INSOLES_CHAIN_TEST = 2  # "בדיקה"
OPTIC_CHAIN_TEST = 2  # "אופטיקה בדיקה"

# dataset -> (request_type_id, child table or None)
REQUEST_KINDS: dict[str, tuple[int, Optional[str]]] = {
    "referral_extend": (1, "referral_request"),
    "referral_change_provider": (2, "referral_request"),
    "referral_cancel": (3, "referral_request"),
    "referral_new": (4, "referral_request"),
    "prescriptions": (5, "prescription_request"),
    "referral_answer_refund": (6, None),
    "refund": (7, None),
    "insoles": (8, "insoles_request"),
    "retroactive_er": (9, "retroactive_commitment_request"),
    "sick_days": (10, "sick_days_request"),
    "optics": (11, "optic_request"),
}
CHILD_TABLES = tuple(sorted({t for _, t in REQUEST_KINDS.values() if t}))
DEPENDENT_TABLES = CHILD_TABLES + ("attachment", "message_sent", "request_in_file", "request_error_in_file")

TAG_PREFIX = "AUTO-SEED"
TAG_RE = re.compile(rf"^\[{TAG_PREFIX}:([0-9a-f]{{12}})\]")
DATASETS = tuple(REQUEST_KINDS) + ("all",)
CLEANUP_MODES = ("report", "delete-owned")


def dataset_kinds(dataset: str) -> list[str]:
    if dataset == "all":
        return list(REQUEST_KINDS)
    if dataset not in REQUEST_KINDS:
        raise SeedGuardError(f"Unknown dataset '{dataset}', expected one of {DATASETS}.")
    return [dataset]


class SeedGuardError(RuntimeError):
    """Raised when the environment, identity, or ownership contract is not satisfied."""


@dataclass
class SeedDate:
    label: str
    nominal: date
    adjusted: date


@dataclass
class SeedEntity:
    kind: str
    request_id: int
    request_type_id: int
    child_table: Optional[str]
    child_ids: list[int]
    label: str
    display_text: str
    target_date: Optional[str] = None


@dataclass
class SeedManifest:
    run_id: str
    env: str
    dataset: str
    personal_number: str
    created_at: str
    status: str = "planned"  # planned -> pending -> committed -> cleaned | cleanup_failed
    dates: list[dict] = field(default_factory=list)
    entities: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def tag(self) -> str:
        return f"[{TAG_PREFIX}:{self.run_id}]"

    @property
    def path(self) -> Path:
        return MANIFEST_DIR / f"meditik_{self.env}_{self.run_id}.json"

    def save(self) -> None:
        MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    @classmethod
    def load(cls, env: str, run_id: str) -> "SeedManifest":
        path = MANIFEST_DIR / f"meditik_{env}_{run_id}.json"
        if not path.exists():
            raise SeedGuardError(f"No manifest for run {run_id} in {MANIFEST_DIR}")
        return cls(**json.loads(path.read_text(encoding="utf-8")))


# ---------------------------------------------------------------- dates

def _israel_holidays(years: range):
    try:
        import holidays
    except ImportError as exc:
        raise SeedGuardError("Install 'holidays' (pip install holidays) for the Israeli calendar.") from exc
    return holidays.country_holidays("IL", years=list(years))


def add_calendar_month(d: date) -> date:
    year, month = (d.year + 1, 1) if d.month == 12 else (d.year, d.month + 1)
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


def next_working_day(d: date, il_holidays) -> date:
    while d.weekday() in (4, 5) or d in il_holidays:  # Friday, Saturday
        d += timedelta(days=1)
    return d


def seed_dates(reference: date) -> list[SeedDate]:
    """+2 days, +1 week, +1 calendar month, each moved forward to a distinct Israeli working day."""
    il = _israel_holidays(range(reference.year, reference.year + 2))
    nominal = [("plus_2_days", reference + timedelta(days=2)),
               ("plus_1_week", reference + timedelta(weeks=1)),
               ("plus_1_month", add_calendar_month(reference))]
    result: list[SeedDate] = []
    for label, day in nominal:
        adjusted = next_working_day(day, il)
        while any(r.adjusted == adjusted for r in result):
            adjusted = next_working_day(adjusted + timedelta(days=1), il)
        result.append(SeedDate(label, day, adjusted))
    return result


# ---------------------------------------------------------------- guards

def load_env(env: str) -> None:
    from dotenv import load_dotenv

    if env not in ALLOWED_ENVS:
        raise SeedGuardError(f"Seeding is allowed only on {ALLOWED_ENVS}, got '{env}'.")
    env_file = REPO_ROOT / f".env.{env}"
    if not env_file.exists():
        raise SeedGuardError(f"Missing {env_file.name}; no fallback to another environment.")
    load_dotenv(env_file, override=False)  # execution settings take precedence
    prod = dotenv_values(REPO_ROOT / ".env.prod")
    prod_target = (prod.get("ORM_DB_HOST"), prod.get("ORM_DB_DATABASE"))
    if all(prod_target) and prod_target == (os.getenv("ORM_DB_HOST"), os.getenv("ORM_DB_DATABASE")):
        raise SeedGuardError(f"'{env}' DB configuration points to the PROD database.")


def _is_allowed(pn: str, spec: str) -> bool:
    """spec: comma list of numbers and inclusive ranges, e.g. '4444401,4444400-4444499'."""
    for part in (p.strip() for p in spec.split(",") if p.strip()):
        low, _, high = part.partition("-")
        if low.isdigit() and (high or low).isdigit() and int(low) <= int(pn) <= int(high or low):
            return True
    return False


def validate_personal_number(personal_number: str) -> str:
    pn = (personal_number or "").strip()
    if not (pn.isascii() and pn.isdigit() and 5 <= len(pn) <= 9):
        raise SeedGuardError("A numeric personal number is required for every seeding run.")
    if not _is_allowed(pn, os.getenv("SEED_ALLOWED_PERSONAL_NUMBERS", "")):
        raise SeedGuardError("Personal number is not in SEED_ALLOWED_PERSONAL_NUMBERS for this environment.")
    ui_user = os.getenv("TEST_PERSONAL_NUMBER", "").strip()
    if ui_user and ui_user != pn:
        raise SeedGuardError("Seed user differs from TEST_PERSONAL_NUMBER used for UI login.")
    return pn


def _fetch(cur, sql: str, params=None) -> list[dict]:
    cur.execute(sql, params)
    cols = [c.name for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def verify_server(cur, env: str) -> list[str]:
    target = VERIFIED_TARGETS.get(env)
    if target is None:
        raise SeedGuardError(f"'{env}' DB target is not verified yet; run discovery and add it to VERIFIED_TARGETS.")
    info = _fetch(cur, "SELECT current_database() AS db, current_schema() AS schema, "
                       "pg_is_in_recovery() AS replica")[0]
    if info["db"] != target["database"] or info["schema"] != target["schema"]:
        raise SeedGuardError(f"Connected to {info['db']}/{info['schema']}, expected "
                             f"{target['database']}/{target['schema']} for '{env}'.")
    if info["db"] != os.getenv("ORM_DB_DATABASE"):
        raise SeedGuardError("Server database does not match ORM_DB_DATABASE.")
    if info["replica"]:
        raise SeedGuardError("Connected to a read-only replica.")
    warnings = []
    if os.getenv("DISABLE_SSL", "").strip().lower() in ("true", "1", "yes"):
        warnings.append("DISABLE_SSL=true: DB traffic is not TLS-protected for this environment.")
    return warnings


def resolve_person_id(cur, personal_number: str) -> str:
    """Map personal number -> patient_person_id from the user's own existing requests."""
    rows = _fetch(cur, "SELECT DISTINCT patient_person_id FROM public.user_request "
                       "WHERE patient_military_id = %s LIMIT 2", (int(personal_number),))
    if len(rows) != 1:
        raise SeedGuardError(f"Cannot resolve a single patient_person_id for the seed user (found {len(rows)}); "
                             "the user needs exactly one identity in earlier requests.")
    return rows[0]["patient_person_id"]


def verify_reference_rows(cur, dataset: str) -> dict[str, int]:
    """Check fixed reference IDs are active and resolve the ER reference IDs. Returns resolved refs."""
    kinds = dataset_kinds(dataset)
    checks = [("request_state", REQUEST_STATE_SAVED)] + [("request_type", REQUEST_KINDS[k][0]) for k in kinds]
    if "prescriptions" in kinds:
        checks.append(("prescription_type", PRESCRIPTION_TYPE_OTHER))
    if "insoles" in kinds:
        checks.append(("insoles_chain", INSOLES_CHAIN_TEST))
    if "optics" in kinds:
        checks.append(("optic_chain", OPTIC_CHAIN_TEST))
    for table, ref_id in checks:
        row = _fetch(cur, f"SELECT is_active FROM public.{table} WHERE id = %s", (ref_id,))
        if not row or not row[0]["is_active"]:
            raise SeedGuardError(f"Reference row public.{table}.id={ref_id} is missing or inactive.")
    refs: dict[str, int] = {}
    if "retroactive_er" in kinds:
        for table in ("er_facility", "er_referral_reason", "er_referral_source"):
            row = _fetch(cur, f"SELECT min(id) AS id FROM public.{table} WHERE is_active")
            if not row or row[0]["id"] is None:
                raise SeedGuardError(f"No active reference row in public.{table}.")
            refs[table] = row[0]["id"]
    return refs


def find_leftovers(cur, personal_number: str) -> list[dict]:
    return _fetch(cur, "SELECT id, request_type_id, request_text FROM public.user_request "
                       "WHERE patient_military_id = %s AND request_text LIKE %s ORDER BY id",
                  (int(personal_number), f"[{TAG_PREFIX}:%"))


# ---------------------------------------------------------------- lock

class _UserLock:
    """Per env+user lock file: rejects parallel seeding runs (incl. xdist workers)."""

    def __init__(self, env: str, personal_number: str):
        self.path = MANIFEST_DIR / f"meditik_{env}_{personal_number}.lock"

    def acquire(self, run_id: str) -> None:
        MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("x", encoding="utf-8") as fh:
                fh.write(run_id)
        except FileExistsError as exc:
            raise SeedGuardError(f"Another seeding run holds {self.path.name}. Parallel seeding is not "
                                 "supported; remove the lock only if that run is dead.") from exc

    def release(self) -> None:
        self.path.unlink(missing_ok=True)


# ---------------------------------------------------------------- seed / cleanup

def _connect():
    from refua_core.config.database import DatabaseManager
    return DatabaseManager().get_connection()


def _prepare(cur) -> None:
    cur.execute("SET LOCAL statement_timeout = '30s'")
    cur.execute("SET LOCAL lock_timeout = '5s'")


def plan(env: str, personal_number: str, dataset: str) -> SeedManifest:
    """Read-only: validate everything a seed would need and return the would-be manifest."""
    load_env(env)
    pn = validate_personal_number(personal_number)
    dataset_kinds(dataset)
    manifest = SeedManifest(run_id=uuid.uuid4().hex[:12], env=env, dataset=dataset, personal_number=pn,
                            created_at=datetime.now(TZ).isoformat())
    manifest.dates = [asdict(d) for d in seed_dates(datetime.now(TZ).date())]
    with _connect() as conn:
        conn.set_session(readonly=True)
        with conn.cursor() as cur:
            _prepare(cur)
            manifest.warnings += verify_server(cur, env)
            resolve_person_id(cur, pn)
            verify_reference_rows(cur, dataset)
            leftovers = find_leftovers(cur, pn)
        conn.rollback()
    if leftovers:
        manifest.warnings.append(f"{len(leftovers)} leftover seeded request(s) from earlier runs exist for "
                                 "this user; run the 'leftovers' command before relying on counts/empty states.")
    return manifest


def seed(env: str, personal_number: str, dataset: str) -> SeedManifest:
    """Insert the dataset in one transaction, commit, and return the manifest with real IDs."""
    manifest = plan(env, personal_number, dataset)
    lock = _UserLock(env, manifest.personal_number)
    lock.acquire(manifest.run_id)
    try:
        with _connect() as conn:
            try:
                with conn.cursor() as cur:
                    _prepare(cur)
                    verify_server(cur, env)
                    person_id = resolve_person_id(cur, manifest.personal_number)
                    refs = verify_reference_rows(cur, dataset)
                    now = datetime.now(TZ)
                    for kind in dataset_kinds(dataset):
                        for i, sd in enumerate(manifest.dates, start=1):
                            manifest.entities.append(asdict(_insert_entity(
                                cur, manifest, kind, refs, person_id, now, i, SeedDate(**sd))))
                manifest.status = "pending"
                manifest.save()  # IDs recorded before commit for crash recovery
                conn.commit()
            except Exception:
                conn.rollback()
                manifest.status = "rolled_back"
                manifest.save()
                raise
        manifest.status = "committed"
        manifest.save()
        missing = [row for row in verify(manifest) if not row["ok"]]
        if missing:
            raise SeedGuardError(f"Read-back failed for {len(missing)} seeded request(s): {missing}")
        return manifest
    except Exception:
        lock.release()
        raise


def _insert_entity(cur, manifest: SeedManifest, kind: str, refs: dict[str, int], person_id: str,
                   now: datetime, index: int, sd: SeedDate) -> SeedEntity:
    request_type, child_table = REQUEST_KINDS[kind]
    display = f"AUTO {kind} {manifest.run_id[:6]} {index}"
    cur.execute(
        "INSERT INTO public.user_request (create_user, patient_person_id, patient_military_id, request_text, "
        "request_type_id, request_state_id, request_time, hatch_upload_counter) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, 0) RETURNING id",
        (person_id, person_id, int(manifest.personal_number), f"{manifest.tag} {display}",
         request_type, REQUEST_STATE_SAVED, now))
    request_id = cur.fetchone()[0]
    target = None
    if child_table == "referral_request":
        cur.execute("INSERT INTO public.referral_request (create_user, required_service, required_medical_facility, "
                    "request_id) VALUES (%s, %s, %s, %s) RETURNING id", (person_id, display, display, request_id))
    elif child_table == "prescription_request":
        cur.execute("INSERT INTO public.prescription_request (create_user, prescription_name, request_id, "
                    "prescription_type_id) VALUES (%s, %s, %s, %s) RETURNING id",
                    (person_id, display, request_id, PRESCRIPTION_TYPE_OTHER))
    elif child_table == "insoles_request":
        cur.execute("INSERT INTO public.insoles_request (create_user, request_id, insoles_chain_id) "
                    "VALUES (%s, %s, %s) RETURNING id", (person_id, request_id, INSOLES_CHAIN_TEST))
    elif child_table == "optic_request":
        cur.execute("INSERT INTO public.optic_request (create_user, request_id, optic_chain_id) "
                    "VALUES (%s, %s, %s) RETURNING id", (person_id, request_id, OPTIC_CHAIN_TEST))
    elif child_table == "retroactive_commitment_request":
        # Retroactive ER commitment covers a past visit: yesterday 10:00 Israel time.
        visit = datetime.combine(now.date() - timedelta(days=1), datetime.min.time(), TZ).replace(hour=10)
        target = visit.isoformat()
        cur.execute("INSERT INTO public.retroactive_commitment_request (create_user, referral_number, visit_time, "
                    "request_id, facility_id, referral_reason_id, referral_source_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (person_id, 900000000 + request_id, visit, request_id, refs["er_facility"],
                     refs["er_referral_reason"], refs["er_referral_source"]))
    elif child_table == "sick_days_request":
        target = sd.adjusted.isoformat()
        cur.execute("INSERT INTO public.sick_days_request (create_user, start_date, end_date, request_id) "
                    "VALUES (%s, %s, %s, %s) RETURNING id", (person_id, sd.adjusted, sd.adjusted, request_id))
    child_ids = [cur.fetchone()[0]] if child_table else []
    return SeedEntity(kind, request_id, request_type, child_table, child_ids, sd.label, display, target)


def verify(manifest: SeedManifest) -> list[dict[str, Any]]:
    """Read-only check that every manifest entity exists, is owned, and has its child row."""
    results = []
    with _connect() as conn:
        conn.set_session(readonly=True)
        with conn.cursor() as cur:
            _prepare(cur)
            for e in manifest.entities:
                parent = _fetch(cur, "SELECT ur.request_type_id, rt.description AS type_name, rs.user_text AS state "
                                     "FROM public.user_request ur "
                                     "JOIN public.request_type rt ON rt.id = ur.request_type_id "
                                     "JOIN public.request_state rs ON rs.id = ur.request_state_id "
                                     "WHERE ur.id = %s AND ur.patient_military_id = %s AND ur.request_text LIKE %s",
                                (e["request_id"], int(manifest.personal_number), f"{manifest.tag}%"))
                children = 0
                if parent and e["child_table"]:
                    if e["child_table"] not in CHILD_TABLES:
                        raise SeedGuardError(f"Unexpected child table {e['child_table']} in manifest.")
                    children = _fetch(cur, f"SELECT count(*) AS n FROM public.{e['child_table']} "
                                           "WHERE id = ANY(%s) AND request_id = %s",
                                      (e["child_ids"], e["request_id"]))[0]["n"]
                ok = bool(parent) and parent[0]["request_type_id"] == e["request_type_id"] and \
                    children == len(e["child_ids"])
                results.append({"kind": e["kind"], "request_id": e["request_id"],
                                "type": parent[0]["type_name"] if parent else None,
                                "state": parent[0]["state"] if parent else None,
                                "child_table": e["child_table"], "children": children, "ok": ok})
        conn.rollback()
    return results


def cleanup(manifest: SeedManifest, mode: str = "report") -> list[str]:
    """Best-effort, non-raising cleanup of exactly this run's rows. Returns warnings."""
    warnings: list[str] = []
    lock = _UserLock(manifest.env, manifest.personal_number)
    try:
        if mode not in CLEANUP_MODES:
            raise SeedGuardError(f"Unknown cleanup mode '{mode}'.")
        if not manifest.entities:
            manifest.status = "cleaned"
            return warnings
        if mode == "report":
            warnings.append(f"Seed run {manifest.run_id}: {len(manifest.entities)} request(s) left in "
                            f"{manifest.env} (no soft-delete column exists). Manifest: {manifest.path}")
            return warnings
        deleted = _delete_owned(manifest)
        manifest.status = "cleaned"
        if deleted != len(manifest.entities):
            warnings.append(f"Seed run {manifest.run_id}: removed {deleted}/{len(manifest.entities)} "
                            "requests (others already absent).")
    except Exception as exc:  # noqa: BLE001 - cleanup must not change the test result
        manifest.status = "cleanup_failed"
        warnings.append(f"Seed run {manifest.run_id} cleanup failed ({type(exc).__name__}: {exc}). "
                        f"Recover with: tools/db_seed_meditik.py cleanup --env {manifest.env} "
                        f"--run-id {manifest.run_id} --mode delete-owned")
    finally:
        manifest.warnings += warnings
        manifest.save()
        lock.release()
    return warnings


def _delete_owned(manifest: SeedManifest) -> int:
    load_env(manifest.env)
    pn = int(manifest.personal_number)
    request_ids = [e["request_id"] for e in manifest.entities]
    with _connect() as conn:
        try:
            with conn.cursor() as cur:
                _prepare(cur)
                verify_server(cur, manifest.env)
                owned = [r["id"] for r in _fetch(
                    cur, "SELECT id FROM public.user_request WHERE id = ANY(%s) AND patient_military_id = %s "
                         "AND request_text LIKE %s FOR UPDATE", (request_ids, pn, f"{manifest.tag}%"))]
                for table in {e["child_table"] for e in manifest.entities if e["child_table"]}:
                    if table not in CHILD_TABLES:
                        raise SeedGuardError(f"Unexpected child table {table} in manifest.")
                    child_ids = [c for e in manifest.entities if e["child_table"] == table for c in e["child_ids"]]
                    cur.execute(f"DELETE FROM public.{table} WHERE id = ANY(%s) AND request_id = ANY(%s)",
                                (child_ids, owned))
                dependents = " OR ".join(
                    f"EXISTS (SELECT 1 FROM public.{t} c WHERE c.request_id = ur.id)" for t in DEPENDENT_TABLES)
                cur.execute(f"SELECT count(*) FROM public.user_request ur WHERE ur.id = ANY(%s) AND ({dependents})",
                            (owned,))
                if cur.fetchone()[0]:
                    raise SeedGuardError("Seeded requests gained dependent rows (sync/attachment); left untouched.")
                cur.execute("DELETE FROM public.user_request WHERE id = ANY(%s) AND patient_military_id = %s "
                            "AND request_text LIKE %s", (owned, pn, f"{manifest.tag}%"))
                deleted = cur.rowcount
            conn.commit()
            return deleted
        except Exception:
            conn.rollback()
            raise


def list_leftovers(env: str, personal_number: str) -> list[dict[str, Any]]:
    load_env(env)
    pn = validate_personal_number(personal_number)
    with _connect() as conn:
        conn.set_session(readonly=True)
        with conn.cursor() as cur:
            _prepare(cur)
            verify_server(cur, env)
            rows = find_leftovers(cur, pn)
        conn.rollback()
    for row in rows:
        match = TAG_RE.match(row["request_text"] or "")
        row["run_id"] = match.group(1) if match else None
    return rows
