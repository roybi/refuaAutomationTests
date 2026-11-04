"""Allure report generation and retention for the persistent report volume."""

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable, Dict, Optional

from .settings import Settings

GENERATE_TIMEOUT_SECONDS = 600


def latest_report_id(settings: Settings) -> Optional[str]:
    """Newest generated report (run ids sort chronologically)."""
    if not settings.reports_dir.exists():
        return None
    ids = sorted((p.name for p in settings.reports_dir.iterdir() if (p / "index.html").exists()), reverse=True)
    return ids[0] if ids else None


def _carry_history(settings: Settings, results: Path) -> None:
    """Copy the previous report's history into the new results so Allure draws trends across runs."""
    previous = latest_report_id(settings)
    history = settings.reports_dir / previous / "history" if previous else None
    if history and history.exists():
        shutil.copytree(history, results / "history", dirs_exist_ok=True)


def _summary(report: Path) -> Dict[str, int]:
    try:
        statistic = json.loads((report / "widgets" / "summary.json").read_text(encoding="utf-8"))["statistic"]
    except (OSError, ValueError, KeyError):
        return {}
    return {key: int(statistic.get(key, 0)) for key in ("passed", "failed", "broken", "skipped", "unknown", "total")}


def generate_report(settings: Settings, run_id: str, log: Callable[[str], None]) -> Optional[Dict[str, int]]:
    """Build the HTML report for a run; returns its statistic, or None when no report could be made."""
    results = settings.results_dir / run_id
    if not results.exists() or not any(results.iterdir()):
        log("[service] no Allure results were produced; no report generated")
        return None
    if not settings.allure_bin:
        log("[service] Allure CLI not found (set ALLURE_BIN); results kept, report not generated")
        return None
    _carry_history(settings, results)
    report = settings.reports_dir / run_id
    command = [settings.allure_bin, "generate", str(results), "-o", str(report), "--clean"]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=GENERATE_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired) as error:
        log(f"[service] allure generate failed: {error}")
        return None
    if completed.returncode != 0 or not (report / "index.html").exists():
        log(f"[service] allure generate exited {completed.returncode}: {(completed.stderr or completed.stdout).strip()[-800:]}")
        return None
    log(f"[service] Allure report ready: /reports/{run_id}/")
    return _summary(report)


def prune(settings: Settings, active_ids: set) -> int:
    """Delete runs older than RETENTION_DAYS (0 keeps everything); returns how many were removed.

    Runs queued, running, or still waiting for their archive upload are never deleted.
    """
    if not settings.retention_days:
        return 0
    cutoff = time.time() - settings.retention_days * 86400
    pending = ({marker.name for marker in settings.pending_dir.iterdir()}
               if settings.archive_enabled and settings.pending_dir.exists() else set())
    removed = 0
    for meta in settings.runs_dir.glob("*.json"):
        run_id = meta.stem
        if run_id in active_ids or run_id in pending or meta.stat().st_mtime >= cutoff:
            continue
        shutil.rmtree(settings.results_dir / run_id, ignore_errors=True)
        shutil.rmtree(settings.reports_dir / run_id, ignore_errors=True)
        (settings.runs_dir / f"{run_id}.log").unlink(missing_ok=True)
        meta.unlink(missing_ok=True)
        removed += 1
    return removed
