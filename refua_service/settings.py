"""Service configuration, read once from environment variables.

Everything the service persists lives under ``DATA_DIR`` (mount a volume there):

    <DATA_DIR>/runs/<run_id>.json            run metadata (status, parameters, exit code)
    <DATA_DIR>/runs/<run_id>.log             pytest console output
    <DATA_DIR>/allure/results/<run_id>/      raw Allure results (input of the report)
    <DATA_DIR>/allure/reports/<run_id>/      generated Allure HTML report
    <DATA_DIR>/seeds/                        DB seed manifests (MEDITIK_SEED_MANIFEST_DIR)
    <DATA_DIR>/home/                         HOME of the test process (session files)
"""

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def parse_user_spec(spec: str) -> List[Tuple[int, int]]:
    """'4444401,4444400-4444499' -> [(4444401, 4444401), (4444400, 4444499)] (same grammar as the DB seed guard)."""
    ranges = []
    for part in (p.strip() for p in spec.split(",") if p.strip()):
        low, _, high = part.partition("-")
        if low.isdigit() and (high or low).isdigit():
            ranges.append((int(low), int(high or low)))
    return ranges


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    allure_bin: Optional[str]
    max_concurrent_runs: int
    retention_days: int
    api_token: Optional[str]
    allowed_envs: Tuple[str, ...]
    user_ranges: Tuple[Tuple[int, int], ...]
    run_timeout_minutes: int

    @property
    def runs_dir(self) -> Path:
        return self.data_dir / "runs"

    @property
    def allure_root(self) -> Path:
        return self.data_dir / "allure"

    @property
    def results_dir(self) -> Path:
        return self.allure_root / "results"

    @property
    def reports_dir(self) -> Path:
        return self.allure_root / "reports"

    def is_user_allowed(self, user: str) -> bool:
        if not self.user_ranges:
            return True
        return any(low <= int(user) <= high for low, high in self.user_ranges)

    def selectable_users(self, limit: int = 500) -> List[str]:
        """Users offered in the UI dropdown (capped so a huge range does not bloat the page)."""
        users: List[str] = []
        for low, high in self.user_ranges:
            for number in range(low, high + 1):
                if len(users) >= limit:
                    return users
                users.append(str(number))
        return users

    def ensure_directories(self) -> None:
        for directory in (self.runs_dir, self.results_dir, self.reports_dir,
                          self.data_dir / "seeds", self.data_dir / "home"):
            directory.mkdir(parents=True, exist_ok=True)


def _users_from_env_file() -> str:
    """Local runs: take the approved users from .env.test (only this key; the pod gets it as an env var)."""
    try:
        from dotenv import dotenv_values
        return dotenv_values(REPO_ROOT / ".env.test").get("SEED_ALLOWED_PERSONAL_NUMBERS") or ""
    except ImportError:
        return ""


def load_settings() -> Settings:
    data_dir = Path(os.getenv("DATA_DIR") or REPO_ROOT / ".service_data").resolve()
    users = (os.getenv("SERVICE_ALLOWED_USERS") or os.getenv("SEED_ALLOWED_PERSONAL_NUMBERS")
             or _users_from_env_file())
    envs = tuple(e.strip().lower() for e in os.getenv("SERVICE_ALLOWED_ENVS", "test,preprod").split(",") if e.strip())
    return Settings(
        data_dir=data_dir,
        allure_bin=os.getenv("ALLURE_BIN") or shutil.which("allure"),
        max_concurrent_runs=max(1, _int("MAX_CONCURRENT_RUNS", 1)),
        retention_days=max(0, _int("RETENTION_DAYS", 30)),
        api_token=os.getenv("SERVICE_API_TOKEN") or None,
        allowed_envs=envs,
        user_ranges=tuple(parse_user_spec(users)),
        run_timeout_minutes=max(1, _int("RUN_TIMEOUT_MINUTES", 180)),
    )
