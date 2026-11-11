"""Tests for the run archive (refua_service.archive), retention default, prune guard and build info."""

import json
import os
import sys
import time

import pytest

from refua_service import archive, buildinfo, reports, runs, settings as service_settings
from refua_service.settings import Settings

RUN_ID = "20261104-093700-abc123"
CREATED = "2026-11-04T09:37:00+00:00"


def make_settings(tmp_path, **overrides) -> Settings:
    values = dict(data_dir=tmp_path / "data", allure_bin=None, max_concurrent_runs=1, retention_days=60,
                  api_token=None, allowed_envs=("test",), user_ranges=(), run_timeout_minutes=1,
                  archive_dir=tmp_path / "archive")
    values.update(overrides)
    settings = Settings(**values)
    settings.ensure_directories()
    return settings


def make_run(settings: Settings, run_id: str = RUN_ID, created_at: str = CREATED, status: str = "failed") -> dict:
    run = {"id": run_id, "status": status, "created_at": created_at, "system": "meditik", "build": {"git_sha": "abc"}}
    (settings.runs_dir / f"{run_id}.json").write_text(json.dumps(run), encoding="utf-8")
    (settings.runs_dir / f"{run_id}.log").write_text("line one\nline two\n", encoding="utf-8")
    results = settings.results_dir / run_id
    (results / "history").mkdir(parents=True)
    (results / "history" / "history.json").write_text("{}", encoding="utf-8")
    (results / "a-result.json").write_text('{"name": "t"}', encoding="utf-8")
    (results / "attachments").mkdir()
    (results / "attachments" / "shot.png").write_bytes(b"png")
    report = settings.reports_dir / run_id
    report.mkdir(parents=True)
    (report / "index.html").write_text("<html/>", encoding="utf-8")
    return run


def archived(settings: Settings, name: str):
    return settings.archive_dir / "runs" / "2026" / "11" / "04" / RUN_ID / name


class FailingBackend:
    def __init__(self):
        self.fail = True
        self.keys = []

    def put_file(self, key, path):
        if self.fail:
            raise OSError("network down")
        self.keys.append(key)

    def put_bytes(self, key, data):
        if self.fail:
            raise OSError("network down")
        self.keys.append(key)


def test_archive_layout_contains_raw_results_log_and_manifest_but_no_report_or_history(tmp_path):
    settings = make_settings(tmp_path)
    run = make_run(settings)
    archiver = archive.Archiver(settings)
    archiver.mark_pending(RUN_ID)

    assert archiver.archive_run(run) is True

    assert archived(settings, "console.log").read_text(encoding="utf-8") == "line one\nline two\n"
    assert archived(settings, "allure-results/a-result.json").exists()
    assert archived(settings, "allure-results/attachments/shot.png").read_bytes() == b"png"
    assert json.loads(archived(settings, "run.json").read_text(encoding="utf-8"))["build"] == {"git_sha": "abc"}
    manifest = json.loads(archived(settings, "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == archive.SCHEMA_VERSION and manifest["run_id"] == RUN_ID
    names = {entry["name"] for entry in manifest["files"]}
    assert names == {"console.log", "allure-results/a-result.json", "allure-results/attachments/shot.png", "run.json"}
    assert not list(settings.archive_dir.rglob("index.html"))  # the HTML report is not archived
    assert not archiver.is_pending(RUN_ID)


def test_failed_upload_keeps_marker_and_manifest_is_never_written(tmp_path):
    settings = make_settings(tmp_path)
    run = make_run(settings)
    backend = FailingBackend()
    archiver = archive.Archiver(settings, backend)
    archiver.mark_pending(RUN_ID)

    assert archiver.archive_run(run) is False
    assert archiver.is_pending(RUN_ID) and backend.keys == []


def test_retry_pending_uploads_after_recovery_and_drops_markers_of_removed_runs(tmp_path):
    settings = make_settings(tmp_path)
    run = make_run(settings)
    backend = FailingBackend()
    archiver = archive.Archiver(settings, backend)
    archiver.mark_pending(RUN_ID)
    archiver.mark_pending("20260101-000000-gone00")
    loader = lambda run_id: run if run_id == RUN_ID else None  # noqa: E731

    assert archiver.retry_pending(loader) == 0
    assert archiver.is_pending(RUN_ID) and not archiver.is_pending("20260101-000000-gone00")

    backend.fail = False
    assert archiver.retry_pending(loader) == 1
    assert not archiver.is_pending(RUN_ID)
    assert backend.keys[-1].endswith(f"{RUN_ID}/manifest.json")  # manifest is written last


def test_key_prefix_uses_utc_creation_date_and_configured_prefix(tmp_path):
    settings = make_settings(tmp_path, archive_prefix="custom")
    key = archive.Archiver(settings).key_prefix({"id": "r1", "created_at": "2026-11-04T23:30:00-02:00"})
    assert key == "custom/2026/11/05/r1"


def test_local_backend_refuses_keys_that_escape_the_folder(tmp_path):
    backend = archive.LocalDirBackend(tmp_path / "archive")
    with pytest.raises(ValueError):
        backend.put_bytes("../outside.txt", b"x")


def test_s3_backend_uploads_with_bucket_and_key(tmp_path):
    calls = []

    class Client:
        def upload_file(self, filename, bucket, key):
            calls.append(("file", bucket, key))

        def put_object(self, **kwargs):
            calls.append(("object", kwargs["Bucket"], kwargs["Key"]))

    settings = make_settings(tmp_path, archive_dir=None, archive_bucket="my-bucket")
    run = make_run(settings)
    assert archive.Archiver(settings, archive.S3Backend("my-bucket", Client())).archive_run(run)
    assert ("file", "my-bucket", f"runs/2026/11/04/{RUN_ID}/console.log") in calls
    assert calls[-1] == ("object", "my-bucket", f"runs/2026/11/04/{RUN_ID}/manifest.json")


def test_disabled_archive_does_nothing(tmp_path):
    settings = make_settings(tmp_path, archive_dir=None)
    archiver = archive.Archiver(settings)
    assert not settings.archive_enabled and not archiver.enabled
    assert archiver.archive_run(make_run(settings)) is False


def old(settings: Settings, run_id: str, days: int) -> None:
    stamp = time.time() - days * 86400
    os.utime(settings.runs_dir / f"{run_id}.json", (stamp, stamp))


def test_prune_keeps_run_waiting_for_upload_but_deletes_other_old_runs(tmp_path):
    settings = make_settings(tmp_path)
    waiting = make_run(settings, "20260101-000000-wait00")
    other = make_run(settings, "20260101-000000-done00")
    fresh = make_run(settings, "20261103-000000-new000")
    for run_id in (waiting["id"], other["id"]):
        old(settings, run_id, 61)
    archive.Archiver(settings).mark_pending(waiting["id"])

    assert reports.prune(settings, set()) == 1
    assert (settings.runs_dir / f"{waiting['id']}.json").exists()
    assert not (settings.runs_dir / f"{other['id']}.json").exists()
    assert (settings.runs_dir / f"{fresh['id']}.json").exists()


def test_prune_boundaries_for_retention_days(tmp_path):
    settings = make_settings(tmp_path)
    inside = make_run(settings, "20260901-000000-in0000")
    outside = make_run(settings, "20260801-000000-out000")
    old(settings, inside["id"], 59)
    old(settings, outside["id"], 61)
    assert reports.prune(settings, set()) == 1
    assert (settings.runs_dir / f"{inside['id']}.json").exists()

    keep_all = make_settings(tmp_path, retention_days=0)
    old(keep_all, inside["id"], 400)
    assert reports.prune(keep_all, set()) == 0


def test_prune_ignores_markers_when_archive_is_disabled(tmp_path):
    settings = make_settings(tmp_path, archive_dir=None)
    stale = make_run(settings, "20260101-000000-stale0")
    old(settings, stale["id"], 90)
    (settings.pending_dir / stale["id"]).touch()
    assert reports.prune(settings, set()) == 1


def test_default_retention_is_60_days_and_archive_settings_are_read_from_environment(tmp_path, monkeypatch):
    for name in ("RETENTION_DAYS", "ARCHIVE_S3_BUCKET", "ARCHIVE_DIR", "ARCHIVE_PREFIX"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    defaults = service_settings.load_settings()
    assert defaults.retention_days == 60 and not defaults.archive_enabled and defaults.archive_prefix == "runs"

    monkeypatch.setenv("ARCHIVE_S3_BUCKET", "bucket-1")
    monkeypatch.setenv("ARCHIVE_PREFIX", "/analysis/runs/")
    configured = service_settings.load_settings()
    assert configured.archive_bucket == "bucket-1" and configured.archive_prefix == "analysis/runs"
    assert configured.archive_enabled


def test_build_info_reads_image_tag_and_git_sha(monkeypatch):
    monkeypatch.setenv("IMAGE_TAG", "abc1234")
    monkeypatch.setenv("GIT_SHA", "f" * 40)
    buildinfo.collect.cache_clear()
    try:
        info = buildinfo.collect()
        assert info["image_tag"] == "abc1234" and info["git_sha"] == "f" * 40
        assert info["python_version"]
    finally:
        buildinfo.collect.cache_clear()


def test_finished_run_is_archived_with_build_info(tmp_path, monkeypatch):
    pytest.importorskip("fastapi")
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARCHIVE_DIR", str(tmp_path / "archive"))
    monkeypatch.setenv("IMAGE_TAG", "tag-1")
    monkeypatch.delenv("ARCHIVE_S3_BUCKET", raising=False)
    monkeypatch.delenv("ALLURE_BIN", raising=False)
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setattr(runs.RunManager, "_command",
                        lambda self, run: [sys.executable, "-c", "print('hello from run')"])
    buildinfo.collect.cache_clear()
    manager = runs.RunManager(service_settings.load_settings())
    try:
        run = manager.submit("meditik", "bdd", None, "4444401", "test", True)
        assert run["build"]["image_tag"] == "tag-1"
        deadline = time.time() + 20
        manifests = []
        while time.time() < deadline and not manifests:
            manifests = list((tmp_path / "archive").rglob("manifest.json"))
            time.sleep(0.1)
        assert manifests, "run was not archived"
        folder = manifests[0].parent
        assert "hello from run" in (folder / "console.log").read_text(encoding="utf-8")
        assert json.loads((folder / "run.json").read_text(encoding="utf-8"))["build"]["image_tag"] == "tag-1"
        pending = tmp_path / "data" / "archive_pending"
        while time.time() < deadline and list(pending.iterdir()):  # the marker is removed right after the manifest
            time.sleep(0.05)
        assert not list(pending.iterdir())
    finally:
        manager.shutdown()
        buildinfo.collect.cache_clear()


def _lose_local_volume(settings: Settings) -> None:
    """What a pod restart does to the emptyDir: runs, results and reports are gone."""
    import shutil
    for directory in (settings.runs_dir, settings.results_dir, settings.reports_dir, settings.pending_dir):
        shutil.rmtree(directory)
    settings.ensure_directories()


def test_restore_brings_back_run_record_and_log_and_keeps_the_report_link(tmp_path):
    settings = make_settings(tmp_path, retention_days=0)
    run = {**make_run(settings), "report_url": f"/reports/{RUN_ID}/", "summary": {"passed": 2}}
    archiver = archive.Archiver(settings)
    assert archiver.archive_run(run) is True
    _lose_local_volume(settings)

    assert archiver.restore() == 1

    restored = json.loads((settings.runs_dir / f"{RUN_ID}.json").read_text(encoding="utf-8"))
    assert restored["id"] == RUN_ID and restored["summary"] == {"passed": 2}
    assert restored["report_url"] == f"/reports/{RUN_ID}/"  # rebuilt from the archived results when opened
    assert restored["restored_from_archive"] is True
    assert (settings.runs_dir / f"{RUN_ID}.log").read_bytes() == archived(settings, "console.log").read_bytes()
    created = archive._created(run).timestamp()
    assert abs((settings.runs_dir / f"{RUN_ID}.json").stat().st_mtime - created) < 2  # retention counts from the run
    assert archiver.restore() == 0  # known runs are left alone


def test_restore_skips_incomplete_archives_foreign_ids_and_runs_outside_retention(tmp_path):
    settings = make_settings(tmp_path, retention_days=0)
    run = make_run(settings)
    archiver = archive.Archiver(settings)
    assert archiver.archive_run(run) is True
    archived(settings, "manifest.json").rename(archived(settings, "manifest.json.bak"))  # upload never finished
    odd = settings.archive_dir / "runs" / "2026" / "11" / "04" / "..evil" / "manifest.json"
    odd.parent.mkdir(parents=True)
    odd.write_text("{}", encoding="utf-8")
    other = settings.archive_dir / "runs" / "2026" / "11" / "04" / "20261104-100000-def456"
    other.mkdir()
    (other / "manifest.json").write_text("{}", encoding="utf-8")
    (other / "run.json").write_text(json.dumps({"id": "somebody-else"}), encoding="utf-8")  # id does not match its folder
    _lose_local_volume(settings)

    assert archiver.restore() == 0
    assert list(settings.runs_dir.iterdir()) == []

    archived(settings, "manifest.json.bak").rename(archived(settings, "manifest.json"))
    old = make_settings(tmp_path, retention_days=3)  # the archived run is from 2026-11-04: far outside the window
    assert archive.Archiver(old).restore() == 0


def test_restore_reads_days_inside_the_retention_window(tmp_path):
    from datetime import datetime, timedelta, timezone
    settings = make_settings(tmp_path, retention_days=5)
    created = (datetime.now(timezone.utc) - timedelta(days=2)).replace(microsecond=0)
    run_id = f"{created:%Y%m%d-%H%M%S}-abc123"
    run = make_run(settings, run_id, created.isoformat())
    archiver = archive.Archiver(settings)
    assert archiver.archive_run(run) is True
    _lose_local_volume(settings)
    assert archiver.restore() == 1 and (settings.runs_dir / f"{run_id}.json").exists()


def test_run_manager_restores_history_at_start_so_the_run_list_survives_a_restart(tmp_path):
    settings = make_settings(tmp_path, retention_days=0)
    run = make_run(settings)
    assert archive.Archiver(settings).archive_run(run) is True
    _lose_local_volume(settings)

    manager = runs.RunManager(settings)
    manager._archive_executor.shutdown(wait=True)  # the restore runs on the archive worker
    assert [item["id"] for item in manager.list()] == [RUN_ID]
    assert manager.read_log(RUN_ID, 0)["text"].splitlines() == ["line one", "line two"]
    manager.shutdown()


class FakeS3Client:
    """The few boto3 calls S3Backend makes, over a dict."""

    class exceptions:  # noqa: N801 - mirrors boto3's client.exceptions
        class NoSuchKey(Exception):
            pass

    def __init__(self, objects):
        self.objects = objects

    def get_paginator(self, name):
        assert name == "list_objects_v2"
        client = self

        class Paginator:
            def paginate(self, Bucket, Prefix):  # noqa: N803 - boto3 argument names
                keys = sorted(key for key in client.objects if key.startswith(Prefix))
                yield {"Contents": [{"Key": key} for key in keys[:1]]}  # two pages, to exercise the loop
                yield {"Contents": [{"Key": key} for key in keys[1:]]}
                yield {}

        return Paginator()

    def get_object(self, Bucket, Key):  # noqa: N803
        if Key not in self.objects:
            raise self.exceptions.NoSuchKey()
        data = self.objects[Key]

        class Body:
            def read(self):
                return data

        return {"Body": Body()}


def test_s3_backend_lists_across_pages_and_maps_a_missing_key_to_none():
    client = FakeS3Client({"runs/a": b"1", "runs/b": b"2", "other/c": b"3"})
    backend = archive.S3Backend("bucket", client)
    assert list(backend.list_keys("runs/")) == ["runs/a", "runs/b"]
    assert backend.get_bytes("runs/b") == b"2" and backend.get_bytes("runs/none") is None


def test_restored_run_without_archived_results_has_no_report_link(tmp_path):
    import shutil
    settings = make_settings(tmp_path, retention_days=0)
    run = {**make_run(settings), "report_url": f"/reports/{RUN_ID}/"}
    shutil.rmtree(settings.results_dir / RUN_ID)  # nothing to archive but the log
    archiver = archive.Archiver(settings)
    assert archiver.archive_run(run) is True
    _lose_local_volume(settings)
    assert archiver.restore() == 1
    assert json.loads((settings.runs_dir / f"{RUN_ID}.json").read_text(encoding="utf-8"))["report_url"] is None


def test_fetch_results_downloads_the_archived_results_and_nothing_outside_the_folder(tmp_path):
    settings = make_settings(tmp_path, retention_days=0)
    run = make_run(settings)
    archiver = archive.Archiver(settings)
    assert archiver.archive_run(run) is True
    _lose_local_volume(settings)

    target = archiver.fetch_results(run)

    assert target == (settings.results_dir / RUN_ID).resolve()
    assert (target / "a-result.json").read_text(encoding="utf-8") == '{"name": "t"}'
    assert (target / "attachments" / "shot.png").read_bytes() == b"png"
    assert not (target / "history").exists() and not (target / "console.log").exists()
    assert archive.Archiver(make_settings(tmp_path / "other", archive_dir=None)).fetch_results(run) is None  # no archive


def test_fetch_results_returns_none_when_the_run_has_no_archived_results(tmp_path):
    settings = make_settings(tmp_path, retention_days=0)
    run = make_run(settings)
    assert archive.Archiver(settings).fetch_results(run) is None
