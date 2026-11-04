"""Off-pod archive of finished runs: console log, raw Allure results and a manifest.

Layout (same for S3 and for a local folder)::

    <prefix>/YYYY/MM/DD/<run_id>/run.json            final run record (parameters, status, counts, build info)
    <prefix>/YYYY/MM/DD/<run_id>/console.log         pytest console output
    <prefix>/YYYY/MM/DD/<run_id>/allure-results/...  raw Allure results (the HTML report is not archived: it can be regenerated)
    <prefix>/YYYY/MM/DD/<run_id>/manifest.json       written last; its presence means the archive of that run is complete

The date is the run's creation date in UTC. Listing ``<prefix>/YYYY/MM/DD/`` finds every run of a day.

Uploading never affects a run's result. A finished run gets a marker file in ``archive_pending/`` first; the marker is
removed only after the manifest is stored, so a failed upload is retried (at service start and after every run) and
``reports.prune`` does not delete a run that is still waiting for its upload.

Enable with ``ARCHIVE_S3_BUCKET`` (S3, credentials from the standard AWS chain, e.g. IRSA) or ``ARCHIVE_DIR`` (folder).
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .settings import Settings

SCHEMA_VERSION = 1
HISTORY_DIR = "history"  # Allure trend data copied from the previous report; already in older archives
logger = logging.getLogger("refua_service.archive")


class LocalDirBackend:
    """Writes the archive into a folder (tests, local runs, or a mounted share)."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    def _target(self, key: str) -> Path:
        target = (self.root / key).resolve()
        if self.root != target and self.root not in target.parents:
            raise ValueError(f"archive key escapes the archive folder: {key}")
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def put_file(self, key: str, path: Path) -> None:
        self._target(key).write_bytes(Path(path).read_bytes())

    def put_bytes(self, key: str, data: bytes) -> None:
        self._target(key).write_bytes(data)


class S3Backend:
    """Writes the archive to an S3 bucket. Encryption and expiry come from the bucket configuration."""

    def __init__(self, bucket: str, client=None):
        self.bucket = bucket
        if client is None:
            import boto3  # imported here so the service runs without boto3 when S3 is not used
            client = boto3.client("s3")
        self._client = client

    def put_file(self, key: str, path: Path) -> None:
        self._client.upload_file(str(path), self.bucket, key)

    def put_bytes(self, key: str, data: bytes) -> None:
        self._client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType="application/json")


def backend_from_settings(settings: Settings):
    if settings.archive_bucket:
        return S3Backend(settings.archive_bucket)
    if settings.archive_dir:
        return LocalDirBackend(settings.archive_dir)
    return None


def _created(run: dict) -> datetime:
    try:
        created = datetime.fromisoformat(run["created_at"])
    except (KeyError, TypeError, ValueError):
        created = datetime.now(timezone.utc)
    return created if created.tzinfo else created.replace(tzinfo=timezone.utc)


class Archiver:
    def __init__(self, settings: Settings, backend=None):
        self.settings = settings
        self.backend = backend if backend is not None else backend_from_settings(settings)

    @property
    def enabled(self) -> bool:
        return self.backend is not None

    def key_prefix(self, run: dict) -> str:
        day = _created(run).astimezone(timezone.utc)
        return f"{self.settings.archive_prefix}/{day:%Y/%m/%d}/{run['id']}"

    def _marker(self, run_id: str) -> Path:
        return self.settings.pending_dir / run_id

    def mark_pending(self, run_id: str) -> None:
        self.settings.pending_dir.mkdir(parents=True, exist_ok=True)
        self._marker(run_id).touch()

    def is_pending(self, run_id: str) -> bool:
        return self._marker(run_id).exists()

    def _files(self, run: dict) -> List[tuple]:
        """(archive-relative name, local path) for everything that belongs to the run."""
        files = []
        log = self.settings.runs_dir / f"{run['id']}.log"
        if log.is_file():
            files.append(("console.log", log))
        results = self.settings.results_dir / run["id"]
        if results.is_dir():
            for path in sorted(results.rglob("*")):
                relative = path.relative_to(results)
                if path.is_file() and not path.is_symlink() and relative.parts[0] != HISTORY_DIR:
                    files.append((f"allure-results/{relative.as_posix()}", path))
        return files

    def archive_run(self, run: dict) -> bool:
        """Copy one finished run; returns False (and keeps the pending marker) when anything fails."""
        if not self.enabled:
            return False
        prefix = self.key_prefix(run)
        try:
            stored: List[Dict[str, object]] = []
            for name, path in self._files(run):
                self.backend.put_file(f"{prefix}/{name}", path)
                stored.append({"name": name, "bytes": path.stat().st_size})
            self.backend.put_bytes(f"{prefix}/run.json", json.dumps(run, indent=2).encode("utf-8"))
            stored.append({"name": "run.json"})
            manifest = {"schema_version": SCHEMA_VERSION, "run_id": run["id"], "status": run.get("status"),
                        "archived_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "files": stored}
            self.backend.put_bytes(f"{prefix}/manifest.json", json.dumps(manifest, indent=2).encode("utf-8"))
        except Exception as error:  # noqa: BLE001 - a failed upload must never break the service; it is retried later
            logger.warning("archive of run %s failed, will retry: %s", run.get("id"), error)
            return False
        self._marker(run["id"]).unlink(missing_ok=True)
        logger.info("run %s archived under %s/", run["id"], prefix)
        return True

    def retry_pending(self, load_run: Callable[[str], Optional[dict]]) -> int:
        """Archive every run that still has a marker; returns how many succeeded."""
        if not self.enabled or not self.settings.pending_dir.exists():
            return 0
        done = 0
        for marker in sorted(self.settings.pending_dir.iterdir()):
            run = load_run(marker.name)
            if run is None:  # the run record is gone (pruned or removed by hand): nothing left to archive
                marker.unlink(missing_ok=True)
            elif self.archive_run(run):
                done += 1
        return done
