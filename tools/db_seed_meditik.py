"""CLI for Meditik direct-DB test data: plan (read-only, default), seed, cleanup, leftovers.

    venv\\Scripts\\python.exe tools\\db_seed_meditik.py plan      --env test --user 4444401 --dataset prescriptions
    venv\\Scripts\\python.exe tools\\db_seed_meditik.py seed      --env test --user 4444401 --dataset all
    venv\\Scripts\\python.exe tools\\db_seed_meditik.py verify    --env test --run-id <id>
    venv\\Scripts\\python.exe tools\\db_seed_meditik.py cleanup   --env test --run-id <id> [--mode delete-owned]
    venv\\Scripts\\python.exe tools\\db_seed_meditik.py leftovers --env test --user 4444401

A committed seed keeps the per-user lock until 'cleanup' runs (either mode).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from refua_tests.utils import meditik_seed as ms  # noqa: E402


def _print_manifest(manifest: ms.SeedManifest) -> None:
    data = asdict(manifest)
    data["personal_number"] = "***" + manifest.personal_number[-2:]
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "seed"):
        p = sub.add_parser(name)
        p.add_argument("--env", required=True, choices=ms.ALLOWED_ENVS)
        p.add_argument("--user", required=True, help="Personal number of the approved automation user")
        p.add_argument("--dataset", required=True, choices=ms.DATASETS)
    p = sub.add_parser("cleanup")
    p.add_argument("--env", required=True, choices=ms.ALLOWED_ENVS)
    p.add_argument("--run-id", required=True)
    p.add_argument("--mode", default="report", choices=ms.CLEANUP_MODES)
    p = sub.add_parser("verify")
    p.add_argument("--env", required=True, choices=ms.ALLOWED_ENVS)
    p.add_argument("--run-id", required=True)
    p = sub.add_parser("leftovers")
    p.add_argument("--env", required=True, choices=ms.ALLOWED_ENVS)
    p.add_argument("--user", required=True)
    args = parser.parse_args()

    try:
        if args.command == "plan":
            _print_manifest(ms.plan(args.env, args.user, args.dataset))
        elif args.command == "seed":
            _print_manifest(ms.seed(args.env, args.user, args.dataset))
        elif args.command == "cleanup":
            ms.load_env(args.env)
            manifest = ms.SeedManifest.load(args.env, args.run_id)
            warnings = ms.cleanup(manifest, args.mode)
            print(f"status={manifest.status}")
            for w in warnings:
                print("WARNING:", w)
            return 1 if manifest.status == "cleanup_failed" else 0
        elif args.command == "verify":
            ms.load_env(args.env)
            rows = ms.verify(ms.SeedManifest.load(args.env, args.run_id))
            for row in rows:
                print(f"  {'OK  ' if row['ok'] else 'FAIL'} {row['kind']:<25} request {row['request_id']} "
                      f"type={row['type']} state={row['state']} {row['child_table']}={row['children']}")
            print(f"{sum(r['ok'] for r in rows)}/{len(rows)} verified")
            return 0 if rows and all(r["ok"] for r in rows) else 1
        else:
            rows = ms.list_leftovers(args.env, args.user)
            print(f"{len(rows)} seeded request(s) remain")
            for row in rows:
                print(f"  request {row['id']} type {row['request_type_id']} run {row['run_id']}")
    except ms.SeedGuardError as exc:
        print("BLOCKED:", exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
