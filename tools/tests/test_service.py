"""Tests for the container service (refua_service): validation, run lifecycle, persistence, reports."""

import importlib
import json
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from refua_service import reports, runs, settings as service_settings  # noqa: E402

QUICK = [sys.executable, "-c", "print('hello from run'); print('line two')"]
SLOW = [sys.executable, "-c", "import time; print('started', flush=True); time.sleep(60)"]


@pytest.fixture
def service(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SERVICE_ALLOWED_USERS", "4444401,4444410-4444412")
    monkeypatch.setenv("SERVICE_ALLOWED_ENVS", "test,preprod")
    monkeypatch.delenv("SERVICE_API_TOKEN", raising=False)
    monkeypatch.delenv("ALLURE_BIN", raising=False)
    monkeypatch.setattr("shutil.which", lambda name: None)  # no Allure CLI unless a test provides one
    app_module = importlib.reload(importlib.import_module("refua_service.app"))
    with TestClient(app_module.app) as client:
        yield client, app_module
    app_module.manager = None


def use_command(monkeypatch, command):
    monkeypatch.setattr(runs.RunManager, "_command", lambda self, run: command)


def wait_for(client, run_id, *states, timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        run = client.get(f"/api/runs/{run_id}").json()
        if run["status"] in states:
            return run
        time.sleep(0.1)
    raise AssertionError(f"run {run_id} never reached {states}: {run}")


BODY = {"system": "meditik", "suite": "bdd", "tags": "smoke", "user": "4444401", "env": "test", "clean": True}


def test_user_spec_parsing_and_allow_list():
    ranges = service_settings.parse_user_spec("4444401, 4444410-4444412, junk, x-9")
    assert ranges == [(4444401, 4444401), (4444410, 4444412)]
    config = service_settings.Settings(data_dir=None, allure_bin=None, max_concurrent_runs=1, retention_days=0,
                                       api_token=None, allowed_envs=("test",), user_ranges=tuple(ranges),
                                       run_timeout_minutes=1)
    assert config.is_user_allowed("4444411") and not config.is_user_allowed("4444409")
    assert config.selectable_users() == ["4444401", "4444410", "4444411", "4444412"]


def test_options_expose_systems_tags_envs_and_users(service):
    client, _ = service
    options = client.get("/api/options").json()
    assert {s["name"] for s in options["systems"]} >= {"meditik", "all"}
    assert "smoke" in {t["name"] for t in options["tags"]}
    assert "new_referral" not in {t["name"] for t in options["tags"]}  # all scenarios pending -> not runnable
    assert options["envs"] == ["test", "preprod"]
    assert options["users"] == ["4444401", "4444410", "4444411", "4444412"]
    assert options["token_required"] is False


@pytest.mark.parametrize("change", [
    {"user": "abc"}, {"user": "4444499"}, {"env": "prod"}, {"suite": "everything"},
    {"tags": "not_a_tag"}, {"tags": "smoke or home"}, {"system": "nope"}, {"tags": "x; rm -rf /"},
])
def test_invalid_parameters_are_rejected(service, change):
    client, _ = service
    assert client.post("/api/runs", json={**BODY, **change}).status_code == 422
    assert client.get("/api/runs").json() == []


def test_run_lifecycle_persists_status_log_and_command(service, monkeypatch):
    client, _ = service
    use_command(monkeypatch, QUICK)
    created = client.post("/api/runs", json={**BODY, "system": "meditek"})
    assert created.status_code == 201 and created.json()["system"] == "meditik"  # alias normalised
    run = wait_for(client, created.json()["id"], "passed", "failed", "error")
    assert run["status"] == "passed" and run["exit_code"] == 0
    assert run["report_url"] is None  # no Allure CLI available in this fixture
    log = client.get(f"/api/runs/{run['id']}/log").json()
    assert "hello from run" in log["text"] and log["finished"] is True
    assert "Allure" in log["text"] or "no Allure results" in log["text"]


def test_failed_exit_code_maps_to_failed_and_other_codes_to_error(service, monkeypatch):
    client, _ = service
    for code, expected in ((1, "failed"), (5, "error")):
        use_command(monkeypatch, [sys.executable, "-c", f"raise SystemExit({code})"])
        run_id = client.post("/api/runs", json=BODY).json()["id"]
        assert wait_for(client, run_id, "passed", "failed", "error")["status"] == expected


def test_same_user_and_env_cannot_run_twice_and_cancel_stops_the_process(service, monkeypatch):
    client, _ = service
    use_command(monkeypatch, SLOW)
    first = client.post("/api/runs", json=BODY).json()
    wait_for(client, first["id"], "running")
    assert client.post("/api/runs", json=BODY).status_code == 409
    assert client.post("/api/runs", json={**BODY, "user": "4444410"}).status_code == 201  # queued behind it
    cancelled = client.post(f"/api/runs/{first['id']}/cancel")
    assert cancelled.status_code == 200
    assert wait_for(client, first["id"], "cancelled")["status"] == "cancelled"


def test_cancelling_a_queued_run_never_starts_it(service, monkeypatch):
    client, _ = service
    use_command(monkeypatch, SLOW)
    running = client.post("/api/runs", json=BODY).json()
    wait_for(client, running["id"], "running")
    queued = client.post("/api/runs", json={**BODY, "user": "4444410"}).json()
    assert client.post(f"/api/runs/{queued['id']}/cancel").json()["status"] == "cancelled"
    client.post(f"/api/runs/{running['id']}/cancel")
    wait_for(client, running["id"], "cancelled")
    time.sleep(0.3)
    final = client.get(f"/api/runs/{queued['id']}").json()
    assert final["status"] == "cancelled" and final["started_at"] is None


def test_token_protects_mutations_only(tmp_path, monkeypatch):
    monkeypatch.setenv("SERVICE_API_TOKEN", "s3cret")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SERVICE_ALLOWED_USERS", "4444401")
    app_module = importlib.reload(importlib.import_module("refua_service.app"))
    with TestClient(app_module.app) as client:
        assert client.get("/api/runs").status_code == 200
        assert client.post("/api/runs", json=BODY).status_code == 401
        assert client.post("/api/runs", json=BODY, headers={"X-API-Token": "wrong"}).status_code == 401
        use_command(monkeypatch, QUICK)
        ok = client.post("/api/runs", json=BODY, headers={"X-API-Token": "s3cret"})
        assert ok.status_code == 201
        assert client.get("/api/options").json()["token_required"] is True
        wait_for(client, ok.json()["id"], "passed")
    app_module.manager = None


def test_restart_marks_in_flight_runs_interrupted(tmp_path):
    config = service_settings.Settings(data_dir=tmp_path, allure_bin=None, max_concurrent_runs=1, retention_days=0,
                                       api_token=None, allowed_envs=("test",), user_ranges=(), run_timeout_minutes=1)
    config.ensure_directories()
    stale = {"id": "20260101-000000-aaaaaa", "status": "running", "user": "1", "env": "test", "finished_at": None}
    (config.runs_dir / f"{stale['id']}.json").write_text(json.dumps(stale), encoding="utf-8")
    manager = runs.RunManager(config)
    assert manager.get(stale["id"])["status"] == "interrupted"
    manager.shutdown()


def test_command_uses_run_tests_with_persistent_results_dir(tmp_path, monkeypatch):
    monkeypatch.delenv("PYTEST_ADDOPTS", raising=False)
    config = service_settings.Settings(data_dir=tmp_path, allure_bin=None, max_concurrent_runs=1, retention_days=0,
                                       api_token=None, allowed_envs=("test",), user_ranges=(), run_timeout_minutes=1)
    manager = runs.RunManager(config)
    run = {"id": "r1", "system": "meditik", "suite": "bdd", "tags": "home", "user": "4444401", "env": "test",
           "clean": True}
    command = manager._command(run)
    assert command[1].endswith("run_tests.py")
    assert command[2:] == ["--system", "meditik", "--suite", "bdd", "--user", "4444401", "--env", "test",
                           "--allure-dir", str(tmp_path / "allure" / "results" / "r1"), "--tags", "home",
                           "--clean", "--headless"]
    environment = manager._environment()
    assert environment["REFUA_ALLURE_ROOT"] == str(tmp_path / "allure")
    assert environment["MEDITIK_SEED_MANIFEST_DIR"] == str(tmp_path / "seeds")
    # pytest.ini's relative log_file would land in the read-only image root: it must go to the data volume instead
    options = shlex.split(manager._environment("r1")["PYTEST_ADDOPTS"])
    assert options == ["-o", f"log_file={tmp_path / 'pytest' / 'r1.log'}", "-o", f"cache_dir={tmp_path / 'pytest' / 'cache'}"]
    monkeypatch.setenv("PYTEST_ADDOPTS", "-x")
    assert shlex.split(manager._environment("r1")["PYTEST_ADDOPTS"])[0] == "-x"  # an existing value is kept
    manager.shutdown()


def test_log_paging_never_splits_a_line(tmp_path):
    config = service_settings.Settings(data_dir=tmp_path, allure_bin=None, max_concurrent_runs=1, retention_days=0,
                                       api_token=None, allowed_envs=("test",), user_ranges=(), run_timeout_minutes=1)
    manager = runs.RunManager(config)
    run = {"id": "20260101-000000-bbbbbb", "status": "running", "user": "1", "env": "test"}
    (config.runs_dir / f"{run['id']}.json").write_text(json.dumps(run), encoding="utf-8")
    (config.runs_dir / f"{run['id']}.log").write_bytes("שלום\nhalf a li".encode("utf-8"))
    first = manager.read_log(run["id"], 0)
    assert first["text"] == "שלום\n" and first["finished"] is False
    again = manager.read_log(run["id"], first["next_offset"])
    assert again["text"] == "" and again["next_offset"] == first["next_offset"]
    manager.shutdown()


def test_report_generation_carries_history_and_reads_summary(tmp_path, monkeypatch):
    config = service_settings.Settings(data_dir=tmp_path, allure_bin="allure", max_concurrent_runs=1,
                                       retention_days=0, api_token=None, allowed_envs=("test",), user_ranges=(),
                                       run_timeout_minutes=1)
    config.ensure_directories()
    previous = config.reports_dir / "20260101-000000-aaaaaa"
    (previous / "history").mkdir(parents=True)
    (previous / "index.html").write_text("old", encoding="utf-8")
    (previous / "history" / "history.json").write_text("{}", encoding="utf-8")
    results = config.results_dir / "20260102-000000-bbbbbb"
    results.mkdir(parents=True)
    (results / "x-result.json").write_text("{}", encoding="utf-8")
    seen = {}

    def fake_run(command, **_):
        seen["history_present"] = (results / "history" / "history.json").exists()
        output = config.reports_dir / "20260102-000000-bbbbbb"
        (output / "widgets").mkdir(parents=True)
        (output / "index.html").write_text("new", encoding="utf-8")
        (output / "widgets" / "summary.json").write_text(
            json.dumps({"statistic": {"passed": 3, "failed": 1, "broken": 0, "skipped": 2, "unknown": 0, "total": 6}}),
            encoding="utf-8")
        return type("Done", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(reports.subprocess, "run", fake_run)
    messages = []
    summary = reports.generate_report(config, "20260102-000000-bbbbbb", messages.append)
    assert seen["history_present"] is True
    assert summary == {"passed": 3, "failed": 1, "broken": 0, "skipped": 2, "unknown": 0, "total": 6}
    assert reports.latest_report_id(config) == "20260102-000000-bbbbbb"


def test_prune_removes_only_expired_inactive_runs(tmp_path):
    import os
    config = service_settings.Settings(data_dir=tmp_path, allure_bin=None, max_concurrent_runs=1, retention_days=1,
                                       api_token=None, allowed_envs=("test",), user_ranges=(), run_timeout_minutes=1)
    config.ensure_directories()
    for run_id, age_days in (("old-run", 5), ("fresh-run", 0), ("active-run", 5)):
        meta = config.runs_dir / f"{run_id}.json"
        meta.write_text("{}", encoding="utf-8")
        (config.results_dir / run_id).mkdir()
        stamp = time.time() - age_days * 86400
        os.utime(meta, (stamp, stamp))
    assert reports.prune(config, {"active-run"}) == 1
    assert not (config.runs_dir / "old-run.json").exists() and not (config.results_dir / "old-run").exists()
    assert (config.runs_dir / "fresh-run.json").exists() and (config.runs_dir / "active-run.json").exists()


def _seed_runs(config, specs):
    """Write finished run records: (id, status, system, created_at, summary)."""
    config.ensure_directories()
    for run_id, status, system, created, summary in specs:
        record = {"id": run_id, "status": status, "system": system, "suite": "all", "tags": None, "user": "4444401",
                  "env": "test", "created_at": created, "started_at": created, "summary": summary}
        (config.runs_dir / f"{run_id}.json").write_text(json.dumps(record), encoding="utf-8")


def test_run_list_pages_and_filters(service):
    client, app_module = service
    _seed_runs(app_module.settings, [
        ("20260101-000000-aaaaaa", "passed", "meditik", "2026-01-01T10:00:00+00:00", None),
        ("20260102-000000-bbbbbb", "failed", "meditik", "2026-01-02T10:00:00+00:00", None),
        ("20260103-000000-cccccc", "passed", "other", "2026-01-03T10:00:00+00:00", None),
        ("20260104-000000-dddddd", "passed", "meditik", "2026-01-04T10:00:00+00:00", None),
    ])
    ids = lambda **params: [r["id"][:8] for r in client.get("/api/runs", params=params).json()]  # noqa: E731
    assert ids() == ["20260104", "20260103", "20260102", "20260101"]
    assert ids(limit=2) == ["20260104", "20260103"]
    assert ids(limit=2, offset=2) == ["20260102", "20260101"]
    assert ids(status="passed") == ["20260104", "20260103", "20260101"]
    assert ids(status="passed", limit=1, offset=1) == ["20260103"]  # offset counts matching runs only
    assert ids(system="meditik", date_from="2026-01-02") == ["20260104", "20260102"]
    assert ids(date_from="2026-01-02", date_to="2026-01-03") == ["20260103", "20260102"]
    assert client.get("/api/runs", params={"date_from": "yesterday"}).status_code == 422
    assert client.get("/api/runs", params={"offset": -1}).status_code == 422


def test_reports_index_lists_every_stored_report_newest_first(service):
    client, app_module = service
    config = app_module.settings
    _seed_runs(config, [
        ("20260101-000000-aaaaaa", "passed", "meditik", "2026-01-01T10:00:00+00:00",
         {"passed": 3, "failed": 1, "broken": 1, "skipped": 2, "unknown": 0, "total": 7}),
        ("20260102-000000-bbbbbb", "failed", "meditik", "2026-01-02T10:00:00+00:00", None),
    ])
    for run_id in ("20260101-000000-aaaaaa", "20260102-000000-bbbbbb", "20260103-000000-orphan"):
        (config.reports_dir / run_id).mkdir()
        (config.reports_dir / run_id / "index.html").write_text("<html></html>", encoding="utf-8")
    (config.reports_dir / "20260104-000000-nohtml").mkdir()  # no index.html: not a report
    for url in ("/reports/", "/reports"):
        page = client.get(url)
        assert page.status_code == 200 and "text/html" in page.headers["content-type"]
        text = page.text
        assert text.index("20260103-000000-orphan") < text.index("20260102-000000-bbbbbb") < text.index("20260101-000000-aaaaaa")
        assert "nohtml" not in text and "3 passed, 2 failed, 2 skipped" in text
    assert client.get("/reports/20260101-000000-aaaaaa/").status_code == 200  # the static mount still serves reports


def test_latest_report_without_reports_shows_a_message_instead_of_an_error(service, monkeypatch):
    client, _ = service
    monkeypatch.setattr(reports, "allure_version", lambda settings: "2.30.0")
    for url in ("/reports/latest", "/reports/latest/"):
        page = client.get(url)
        assert page.status_code == 200 and "text/html" in page.headers["content-type"]
        assert "No reports yet" in page.text and "Allure report generator is running" in page.text
    monkeypatch.setattr(reports, "allure_version", lambda settings: None)
    page = client.get("/reports/latest")
    assert page.status_code == 200 and "Allure report generator is not available" in page.text


def test_latest_report_redirects_to_the_newest_report(service):
    client, app_module = service
    config = app_module.settings
    for run_id in ("20260101-000000-aaaaaa", "20260102-000000-bbbbbb"):
        (config.reports_dir / run_id).mkdir()
        (config.reports_dir / run_id / "index.html").write_text("<html></html>", encoding="utf-8")
    response = client.get("/reports/latest", follow_redirects=False)
    assert response.status_code in (302, 307) and response.headers["location"] == "/reports/20260102-000000-bbbbbb/"


def test_reports_index_without_reports_explains_why_and_carries_the_logos(service, monkeypatch):
    client, _ = service
    monkeypatch.setattr(reports, "allure_version", lambda settings: "2.30.0")
    page = client.get("/reports/")
    assert page.status_code == 200 and "No reports yet" in page.text
    assert "/assets/meditik-logo.png" in page.text
    for name in ("meditik-logo.png", "idf-computer-service-directorate-logo.png"):
        image = client.get(f"/assets/{name}")
        assert image.status_code == 200 and image.headers["content-type"] == "image/png"


def test_reports_status_tells_whether_allure_runs(service, monkeypatch):
    client, _ = service
    assert client.get("/api/reports/status").json() == {
        "allure_ready": False, "allure_version": None, "run_count": 0, "runs_with_report": 0,
        "report_count": 0, "latest_report": None}
    monkeypatch.setattr(reports, "allure_version", lambda settings: "2.30.0")
    status = client.get("/api/reports/status").json()
    assert status["allure_ready"] is True and status["allure_version"] == "2.30.0"


def test_reports_status_counts_executions_and_the_ones_that_have_a_report(service):
    client, app_module = service
    config = app_module.settings
    for run_id in ("20260101-000000-aaaaaa", "20260102-000000-bbbbbb", "20260103-000000-cccccc"):
        (config.runs_dir / f"{run_id}.json").write_text(json.dumps({"id": run_id, "status": "failed"}), encoding="utf-8")
    for run_id in ("20260102-000000-bbbbbb", "20260109-000000-orphan"):  # the second report has no run record
        (config.reports_dir / run_id).mkdir()
        (config.reports_dir / run_id / "index.html").write_text("<html></html>", encoding="utf-8")
    status = client.get("/api/reports/status").json()
    assert status["run_count"] == 3 and status["runs_with_report"] == 1 and status["report_count"] == 2
    assert status["latest_report"] == "20260109-000000-orphan"


def test_homepage_uses_execution_wording_and_a_pinned_header():
    page = (Path(__file__).resolve().parents[2] / "refua_service" / "static" / "index.html").read_text(encoding="utf-8")
    assert "<h2>New execution</h2>" in page and "<h2>Execution history " in page
    assert "<h2>New run</h2>" not in page and "<h2>Runs " not in page
    assert re.search(r"header \{[^}]*position:\s*sticky;[^}]*top:\s*0", page)


def test_allure_version_reads_the_cli_and_does_not_remember_failures(tmp_path, monkeypatch):
    config = service_settings.Settings(data_dir=tmp_path, allure_bin="allure", max_concurrent_runs=1, retention_days=0,
                                       api_token=None, allowed_envs=("test",), user_ranges=(), run_timeout_minutes=1)
    monkeypatch.setattr(reports, "_allure_versions", {})
    answers = iter([subprocess.CompletedProcess([], 1, "", "no java"), subprocess.CompletedProcess([], 0, "2.30.0\n", "")])
    monkeypatch.setattr(reports.subprocess, "run", lambda *args, **kwargs: next(answers))
    assert reports.allure_version(config) is None
    assert reports.allure_version(config) == "2.30.0"
    assert reports.allure_version(config) == "2.30.0"  # remembered: no third subprocess answer is needed
    assert reports.allure_version(service_settings.Settings(
        data_dir=tmp_path, allure_bin=None, max_concurrent_runs=1, retention_days=0, api_token=None,
        allowed_envs=("test",), user_ranges=(), run_timeout_minutes=1)) is None


RUN_A = "20261104-093700-abc123"
RUN_B = "20261105-101500-def456"


@pytest.fixture
def archived_service(tmp_path, monkeypatch):
    """The service with an archive folder holding two finished runs that the pod no longer has locally."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARCHIVE_DIR", str(tmp_path / "archive"))
    monkeypatch.setenv("SERVICE_ALLOWED_USERS", "4444401")
    monkeypatch.delenv("SERVICE_API_TOKEN", raising=False)
    monkeypatch.delenv("ALLURE_BIN", raising=False)
    monkeypatch.setattr("shutil.which", lambda name: None)
    from refua_service import archive as archive_module
    config = service_settings.load_settings()
    config.ensure_directories()
    archiver = archive_module.Archiver(config)
    for run_id, day, with_results in ((RUN_A, "2026-11-04", True), (RUN_B, "2026-11-05", False)):
        run = {"id": run_id, "status": "failed", "created_at": f"{day}T09:37:00+00:00", "system": "meditik",
               "summary": {"passed": 1}, "report_url": f"/reports/{run_id}/"}
        (config.runs_dir / f"{run_id}.json").write_text(json.dumps(run), encoding="utf-8")
        (config.runs_dir / f"{run_id}.log").write_text("log\n", encoding="utf-8")
        results = config.results_dir / run_id
        results.mkdir(parents=True)
        if with_results:
            (results / "one-result.json").write_text("{}", encoding="utf-8")
            (results / "attachments").mkdir()
            (results / "attachments" / "shot.png").write_bytes(b"png")
        assert archiver.archive_run(run)
    import shutil
    for directory in (config.runs_dir, config.results_dir, config.reports_dir, config.pending_dir):  # the pod restarts
        shutil.rmtree(directory)
    app_module = importlib.reload(importlib.import_module("refua_service.app"))
    with TestClient(app_module.app) as client:
        app_module.get_manager()._archive_executor.shutdown(wait=True)  # the start-up restore of the run list
        yield client, app_module
    app_module.manager = None


def fake_allure(monkeypatch, built):
    """Stand-in for `allure generate`: writes an index.html from the downloaded results and records the call."""
    def generate(config, run_id, log):
        results = config.results_dir / run_id
        assert (results / "one-result.json").exists() and (results / "attachments" / "shot.png").read_bytes() == b"png"
        built.append(run_id)
        (config.reports_dir / run_id).mkdir(parents=True, exist_ok=True)
        (config.reports_dir / run_id / "index.html").write_text(f"<html>report {run_id}</html>", encoding="utf-8")
        return {"passed": 1}
    monkeypatch.setattr(reports, "generate_report", generate)
    monkeypatch.setattr(reports, "allure_version", lambda config: "2.30.0")


def test_restored_runs_keep_a_report_link_only_when_the_archive_has_results(archived_service):
    client, _ = archived_service
    assert client.get(f"/api/runs/{RUN_A}").json()["report_url"] == f"/reports/{RUN_A}/"
    assert client.get(f"/api/runs/{RUN_B}").json()["report_url"] is None


def test_opening_a_report_that_the_pod_lost_rebuilds_it_from_the_archive_once(archived_service, monkeypatch):
    client, _ = archived_service
    built = []
    fake_allure(monkeypatch, built)
    for _ in range(2):
        page = client.get(f"/reports/{RUN_A}/")
        assert page.status_code == 200 and f"report {RUN_A}" in page.text
    assert built == [RUN_A]  # the second visit uses the rebuilt report


def test_a_report_without_archived_results_or_with_a_bad_id_shows_a_message_or_404(archived_service, monkeypatch):
    client, _ = archived_service
    fake_allure(monkeypatch, [])
    page = client.get(f"/reports/{RUN_B}/")
    assert page.status_code == 200 and "Report not available" in page.text
    assert client.get("/reports/20260101-000000-aaaaaa/").status_code == 200  # no such run: same message, no crash
    assert client.get("/reports/..%2f..%2fetc/").status_code == 404
    assert client.get(f"/reports/{RUN_A}", follow_redirects=False).headers["location"] == f"/reports/{RUN_A}/"


def test_all_reports_and_latest_report_use_executions_that_can_be_rebuilt(archived_service, monkeypatch):
    client, _ = archived_service
    built = []
    fake_allure(monkeypatch, built)
    index = client.get("/reports/").text
    assert f"/reports/{RUN_A}/" in index and RUN_B not in index and "Reports (1)" in index
    assert "rebuilt from the archived results" in index
    latest = client.get("/reports/latest", follow_redirects=False)
    assert latest.status_code in (302, 307) and latest.headers["location"] == f"/reports/{RUN_A}/"
    assert built == [RUN_A]
    status = client.get("/api/reports/status").json()
    assert status["run_count"] == 2 and status["runs_with_report"] == 1 and status["report_count"] == 1


def test_latest_report_skips_an_execution_whose_report_cannot_be_built(archived_service, monkeypatch):
    client, app_module = archived_service
    fake_allure(monkeypatch, [])
    manager = app_module.get_manager()
    manager._update(RUN_B, report_url=f"/reports/{RUN_B}/")  # newer run that claims a report but has no archived results
    latest = client.get("/reports/latest", follow_redirects=False)
    assert latest.headers["location"] == f"/reports/{RUN_A}/"


def test_homepage_links_every_finished_execution_to_its_own_report():
    page = (Path(__file__).resolve().parents[2] / "refua_service" / "static" / "index.html").read_text(encoding="utf-8")
    assert "isFinished(run)" in page and "function reportUrl(run)" in page
    assert "'/reports/' + encodeURIComponent(run.id) + '/'" in page
    assert "if (run.report_url) {" not in page  # the link no longer depends on a report that the pod may have lost
