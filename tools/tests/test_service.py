"""Tests for the container service (refua_service): validation, run lifecycle, persistence, reports."""

import importlib
import json
import sys
import time

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


def test_command_uses_run_tests_with_persistent_results_dir(tmp_path):
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
