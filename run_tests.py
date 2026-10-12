"""Single entry point to run the automation suites for any registered system.

Examples (from the repository root):

    python run_tests.py --system meditik --suite bdd --tags smoke --user 4444401 --env test
    python run_tests.py --system meditik --user 4444405 --allure-dir auto
    python run_tests.py --system all --tags smoke --user 4444411
    python run_tests.py --list-systems

Anything after ``--`` (or any unknown option) is passed to pytest unchanged.
The system and the user are explicit per-run parameters: one invocation targets one
system and exactly one user.
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from refua_tests.systems import ALL, SYSTEMS, resolve_system, system_names

REPO_ROOT = Path(__file__).resolve().parent
ALLURE_ROOT = REPO_ROOT / "allure"
DEFAULT_ALLURE_DIR = ALLURE_ROOT / "results"
SUITE_PATHS = {"bdd": ["refua_tests/bdd"], "pytest": ["refua_tests/tests"], "all": []}


def _interpreter() -> str:
    """Prefer the repository's virtual environment so the wrapper works from any Python."""
    for relative in ("venv/Scripts/python.exe", "venv/bin/python"):
        candidate = REPO_ROOT / relative
        if candidate.exists():
            return str(candidate)
    return sys.executable


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--system", help=f"System under test: {', '.join(system_names() + [ALL])}")
    parser.add_argument("--user", help="Personal number of the test user (exactly one per run)")
    parser.add_argument("--env", default="test", choices=("test", "preprod", "prod"),
                        help="Target environment (default: test)")
    parser.add_argument("--suite", default="all", choices=sorted(SUITE_PATHS),
                        help="bdd = Gherkin scenarios, pytest = page-object tests (default: all)")
    parser.add_argument("--tags", help='pytest marker expression, e.g. smoke or "smoke and not known_issue"')
    parser.add_argument("--allure-dir", default=None,
                        help="Allure results directory; 'auto' = allure/results/<system>_<user>_<timestamp> "
                             "(default: allure/results)")
    parser.add_argument("--clean", action="store_true", help="Empty the Allure results directory first")
    parser.add_argument("--dry-run", action="store_true", help="Print the pytest command without running it")
    parser.add_argument("--list-systems", action="store_true", help="List the registered systems and exit")
    return parser


def list_systems() -> str:
    lines = ["Registered systems:"]
    for name in system_names():
        spec = SYSTEMS[name]
        user = "requires --user" if spec.requires_user else "no user needed"
        aliases = f" (aliases: {', '.join(spec.aliases)})" if spec.aliases else ""
        lines.append(f"  {name:<10} {spec.description}; marker @{spec.marker}; {user}{aliases}")
    lines.append(f"  {ALL:<10} every registered system")
    return "\n".join(lines)


def resolve_allure_dir(value: Optional[str], system: str, user: Optional[str]) -> Path:
    if value is None:
        return DEFAULT_ALLURE_DIR
    if value.lower() == "auto":
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return ALLURE_ROOT / "results" / f"{system.lower()}_{user or 'nouser'}_{stamp}"
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def validate(args: argparse.Namespace) -> None:
    if not args.system:
        raise SystemExit(
            "--system is required. Choose one of: " + ", ".join(system_names() + [ALL]))
    try:
        spec = resolve_system(args.system)
    except ValueError as error:
        raise SystemExit(str(error))
    needs_user = spec.requires_user if spec else any(s.requires_user for s in SYSTEMS.values())
    if needs_user and not args.user:
        raise SystemExit(
            "--user is required for this selection: pass exactly one personal number, e.g. --user 4444401")
    if args.user and not (args.user.isascii() and args.user.isdigit()):
        raise SystemExit(f"--user must contain digits only, got '{args.user}'")


def build_command(args: argparse.Namespace, extra: List[str], allure_dir: Path) -> List[str]:
    command = [_interpreter(), "-m", "pytest", *SUITE_PATHS[args.suite], "--system", args.system]
    if args.user:
        command += ["--personal-number", args.user]
    if args.tags:
        command += ["-m", args.tags]
    command += ["--alluredir", str(allure_dir)]
    return command + extra


def clean_directory(path: Path) -> None:
    resolved = path.resolve()
    if ALLURE_ROOT.resolve() not in resolved.parents and resolved != ALLURE_ROOT.resolve():
        raise SystemExit(f"--clean refuses to empty a directory outside {ALLURE_ROOT}: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def main(argv: Optional[List[str]] = None) -> int:
    args, extra = build_parser().parse_known_args(argv)
    extra = [item for item in extra if item != "--"]
    if args.list_systems:
        print(list_systems())
        return 0
    validate(args)

    allure_dir = resolve_allure_dir(args.allure_dir, args.system, args.user)
    if args.clean:
        clean_directory(allure_dir)
    command = build_command(args, extra, allure_dir)
    print(f"[run_tests] system={args.system} user={args.user or '-'} env={args.env} "
          f"suite={args.suite} tags={args.tags or '-'}")
    print("[run_tests] " + subprocess.list2cmdline(command))
    if args.dry_run:
        return 0
    environment = dict(os.environ, TEST_ENV=args.env)
    return subprocess.run(command, cwd=REPO_ROOT, env=environment).returncode


if __name__ == "__main__":
    sys.exit(main())
