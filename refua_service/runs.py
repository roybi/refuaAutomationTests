"""Run lifecycle: queue, execute ``run_tests.py`` as a subprocess, persist state, build the report."""

import json
import logging
import os
import secrets
import shlex
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Dict, List, Optional

from . import buildinfo, reports
from .archive import Archiver
from .settings import REPO_ROOT, Settings

ACTIVE = ("queued", "running")
logger = logging.getLogger("refua_service.runs")
LOG_CHUNK_BYTES = 64 * 1024


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class DuplicateRunError(Exception):
    """The same user/environment already has a queued or running run (the DB seed holds a per-user lock)."""


class RunManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        settings.ensure_directories()
        self._lock = threading.RLock()
        self._processes: Dict[str, subprocess.Popen] = {}
        self._cancelled: set = set()
        self._closing = False
        self._live: Dict[str, dict] = {}  # queued/running runs: the source of truth until they finish
        self._report_locks: Dict[str, threading.Lock] = {}  # one report rebuild per run at a time
        self._executor = ThreadPoolExecutor(max_workers=settings.max_concurrent_runs, thread_name_prefix="run")
        self.archiver = Archiver(settings)
        # One archive worker, separate from the run workers, so an upload never delays the next run.
        self._archive_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="archive")
        self._mark_interrupted()
        reports.prune(settings, set())
        if self.archiver.enabled:
            self._archive_executor.submit(self._restore_archived)  # history lost with the local volume (pod restart)
            self._archive_executor.submit(self._archive_pending)  # uploads that failed before a restart

    # ---- persistence -------------------------------------------------------------------------

    def _meta_path(self, run_id: str):
        return self.settings.runs_dir / f"{run_id}.json"

    def _log_path(self, run_id: str):
        return self.settings.runs_dir / f"{run_id}.log"

    def _write(self, run: dict) -> None:
        path = self._meta_path(run["id"])
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(run, indent=2), encoding="utf-8")
        os.replace(temporary, path)

    def get(self, run_id: str) -> Optional[dict]:
        if not run_id.replace("-", "").isalnum():
            return None
        with self._lock:
            live = self._live.get(run_id)
            if live is not None:
                return dict(live)
        for attempt in range(5):  # Windows can briefly refuse a read while the file is being replaced
            try:
                return json.loads(self._meta_path(run_id).read_text(encoding="utf-8"))
            except FileNotFoundError:
                return None
            except (OSError, ValueError):
                time.sleep(0.02 * (attempt + 1))
        return None

    def list(self, limit: int = 100, offset: int = 0, status: Optional[str] = None, system: Optional[str] = None,
             date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[dict]:
        """Newest first. Filters match status, system and the UTC creation date (YYYY-MM-DD, inclusive);
        ``offset`` counts matching runs, so paging through a filtered list is stable."""
        runs, skipped = [], 0
        for path in sorted(self.settings.runs_dir.glob("*.json"), reverse=True):
            run = self.get(path.stem)
            if not run:
                continue
            created = (run.get("created_at") or "")[:10]
            if ((status and run["status"] != status) or (system and run["system"] != system)
                    or (date_from and created < date_from) or (date_to and created > date_to)):
                continue
            if skipped < offset:
                skipped += 1
                continue
            runs.append(run)
            if len(runs) >= limit:
                break
        return runs

    def _update(self, run_id: str, **fields) -> dict:
        with self._lock:
            run = self._live.get(run_id) or self.get(run_id)
            run.update(fields)
            self._write(run)
            if run["status"] in ACTIVE:
                self._live[run_id] = run
            else:
                self._live.pop(run_id, None)
            return dict(run)

    def _mark_interrupted(self) -> None:
        """A restart kills in-flight runs; record that instead of leaving them 'running' forever."""
        for run in self.list(limit=10_000):
            if run["status"] in ACTIVE:
                run.update(status="interrupted", finished_at=_now())
                self._write(run)

    def _append_log(self, run_id: str, line: str) -> None:
        with open(self._log_path(run_id), "a", encoding="utf-8") as handle:
            handle.write(line.rstrip("\n") + "\n")

    # ---- public API --------------------------------------------------------------------------

    def submit(self, system: str, suite: str, tags: Optional[str], user: str, env: str, clean: bool) -> dict:
        with self._lock:
            for other in self.list(limit=200):
                if other["status"] in ACTIVE and other["user"] == user and other["env"] == env:
                    raise DuplicateRunError(
                        f"Run {other['id']} for user {user} on {env} is still {other['status']}; "
                        "wait for it or cancel it first.")
            run_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(3)}"
            run = {
                "id": run_id, "status": "queued", "system": system, "suite": suite, "tags": tags or None,
                "user": user, "env": env, "clean": clean, "created_at": _now(), "started_at": None,
                "finished_at": None, "exit_code": None, "command": None, "report_url": None, "summary": None,
                "build": buildinfo.collect(),
            }
            self._write(run)
            self._live[run_id] = run
        self._executor.submit(self._execute, run_id)
        return dict(run)

    def ensure_report(self, run_id: str) -> bool:
        """Make sure the HTML report of a finished run exists, rebuilding it from its raw Allure results.

        The report folder lives in the pod's temporary storage and is lost on every restart, while the raw results
        are kept in the archive. Returns True when the report is available afterwards.
        """
        index = self.settings.reports_dir / run_id / "index.html"
        if index.is_file():
            return True
        run = self.get(run_id)
        if run is None or run["status"] in ACTIVE:
            return False
        with self._lock:
            lock = self._report_locks.setdefault(run_id, threading.Lock())
        with lock:
            if index.is_file():  # another request built it while this one waited
                return True
            results = self.settings.results_dir / run_id
            if not (results.is_dir() and any(results.iterdir())):
                try:
                    results = self.archiver.fetch_results(run)
                except Exception:  # noqa: BLE001 - an unreachable archive means "no report", not a server error
                    logger.exception("fetching the archived results of run %s failed", run_id)
                    return False
                if results is None:
                    return False
            summary = reports.generate_report(self.settings, run_id, lambda line: logger.info("%s: %s", run_id, line))
            return summary is not None and index.is_file()

    def cancel(self, run_id: str) -> Optional[dict]:
        run = self.get(run_id)
        if run is None or run["status"] not in ACTIVE:
            return run
        with self._lock:
            self._cancelled.add(run_id)
            process = self._processes.get(run_id)
        if process is not None:
            self._terminate(process)
        elif run["status"] == "queued":
            return self._update(run_id, status="cancelled", finished_at=_now())
        return self.get(run_id)

    def read_log(self, run_id: str, offset: int) -> Optional[dict]:
        run = self.get(run_id)
        if run is None:
            return None
        finished = run["status"] not in ACTIVE
        path = self._log_path(run_id)
        if not path.exists():
            return {"offset": offset, "next_offset": offset, "text": "", "finished": finished}
        with open(path, "rb") as handle:
            handle.seek(max(0, offset))
            chunk = handle.read(LOG_CHUNK_BYTES)
            more_to_read = bool(handle.read(1))
        if not finished or more_to_read:
            # Serve whole lines only (so a multi-byte character is never cut); a short unfinished line waits.
            cut = chunk.rfind(b"\n")
            if cut != -1:
                chunk = chunk[:cut + 1]
            elif len(chunk) < LOG_CHUNK_BYTES:
                chunk = b""
        return {"offset": offset, "next_offset": offset + len(chunk),
                "text": chunk.decode("utf-8", errors="replace"), "finished": finished and not more_to_read}

    def shutdown(self) -> None:
        self._closing = True  # running loops keep terminating their process; queued runs never start
        for process in list(self._processes.values()):
            self._terminate(process)
        self._executor.shutdown(wait=False, cancel_futures=True)
        self._archive_executor.shutdown(wait=False, cancel_futures=True)  # markers survive; retried at next start

    # ---- execution ---------------------------------------------------------------------------

    def _command(self, run: dict) -> List[str]:
        command = [sys.executable, str(REPO_ROOT / "run_tests.py"),
                   "--system", run["system"], "--suite", run["suite"], "--user", run["user"],
                   "--env", run["env"], "--allure-dir", str(self.settings.results_dir / run["id"])]
        if run["tags"]:
            command += ["--tags", run["tags"]]
        if run["clean"]:
            command.append("--clean")
        return command + ["--headless"]

    def _environment(self, run_id: str = "run") -> dict:
        data = self.settings.data_dir
        # pytest.ini points log_file at the repo root and pytest caches there too; the image's root filesystem is
        # read-only, so both are redirected to the data volume (the ini's log_file would otherwise abort every run).
        pytest_files = data / "pytest"
        addopts = " ".join(filter(None, [os.environ.get("PYTEST_ADDOPTS"),
                                         f"-o log_file={shlex.quote(str(pytest_files / f'{run_id}.log'))}",
                                         f"-o cache_dir={shlex.quote(str(pytest_files / 'cache'))}"]))
        return dict(os.environ, PYTHONUNBUFFERED="1", AUTH_CHECK_HEADLESS="true", PYTEST_ADDOPTS=addopts,
                    REFUA_ALLURE_ROOT=str(self.settings.allure_root),
                    MEDITIK_SEED_MANIFEST_DIR=str(data / "seeds"), HOME=str(data / "home"))

    @staticmethod
    def _terminate(process: subprocess.Popen) -> None:
        try:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
        except (ProcessLookupError, PermissionError, OSError):
            pass

    def _execute(self, run_id: str) -> None:
        run = self.get(run_id)
        if self._closing or run is None or run["status"] != "queued" or run_id in self._cancelled:
            return
        command = self._command(run)
        run = self._update(run_id, status="running", started_at=_now(), command=" ".join(command[1:]))
        status, exit_code = "error", None
        try:
            with open(self._log_path(run_id), "ab") as log:
                process = subprocess.Popen(
                    command, cwd=REPO_ROOT, env=self._environment(run_id), stdin=subprocess.DEVNULL,
                    stdout=log, stderr=subprocess.STDOUT, start_new_session=(os.name == "posix"))
                with self._lock:
                    self._processes[run_id] = process
                if self._closing or run_id in self._cancelled:  # cancelled between "running" and the process starting
                    self._terminate(process)
                deadline = time.monotonic() + self.settings.run_timeout_minutes * 60
                timed_out = False
                while True:
                    try:
                        exit_code = process.wait(timeout=1)
                        break
                    except subprocess.TimeoutExpired:
                        # Re-send until the process is gone: a terminate right after start can fail transiently.
                        if self._closing or run_id in self._cancelled:
                            self._terminate(process)
                        elif time.monotonic() > deadline:
                            timed_out = True
                            self._terminate(process)
                status = ("timed_out" if timed_out else "passed" if exit_code == 0
                          else "failed" if exit_code == 1 else "error")
        except OSError as error:
            self._append_log(run_id, f"[service] could not start the run: {error}")
        finally:
            with self._lock:
                self._processes.pop(run_id, None)
        if run_id in self._cancelled:
            status = "cancelled"
        summary = reports.generate_report(self.settings, run_id, lambda line: self._append_log(run_id, line))
        self._update(run_id, status=status, exit_code=exit_code, finished_at=_now(), summary=summary,
                     report_url=f"/reports/{run_id}/" if summary is not None else None)
        if self.archiver.enabled:
            self.archiver.mark_pending(run_id)  # before prune, so the run is not deleted before it is uploaded
            self._archive_executor.submit(self._archive_pending)
        reports.prune(self.settings, {r["id"] for r in self.list(limit=200) if r["status"] in ACTIVE})

    def _restore_archived(self) -> None:
        try:
            self.archiver.restore()
        except Exception:  # noqa: BLE001 - the worker must survive; history just stays as it is
            logger.exception("restoring runs from the archive failed")

    def _archive_pending(self) -> None:
        try:
            self.archiver.retry_pending(self.get)
        except Exception:  # noqa: BLE001 - the worker must survive; the markers stay and the next call retries
            logger.exception("archiving pending runs failed")
