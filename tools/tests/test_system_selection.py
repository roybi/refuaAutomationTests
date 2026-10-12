"""Selection rules for --system: required flag, per-system filtering and fixture gating."""

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from refua_tests import systems

pytest_plugins = ["pytester"]

ROOT_CONFTEST = (Path(__file__).resolve().parents[2] / "conftest.py").read_text(encoding="utf-8")

TESTS = """
import pytest

@pytest.mark.meditik
def test_meditik_case():
    pass

@pytest.mark.cprgo
def test_cprgo_case():
    pass
"""


@pytest.fixture
def fake_cprgo(monkeypatch):
    spec = systems.SystemSpec(
        name="cprgo", marker="cprgo", app_id="cprgo-app", description="test double")
    monkeypatch.setitem(systems.SYSTEMS, "cprgo", spec)
    monkeypatch.setenv("TEST_APP", "unchanged")
    return spec


@pytest.fixture
def project(pytester, fake_cprgo):
    pytester.makeconftest(ROOT_CONFTEST)
    pytester.makepyfile(test_systems=TESTS)
    return pytester


def run_ids(result):
    outcomes = result.parseoutcomes()
    return outcomes.get("passed", 0), outcomes.get("deselected", 0)


def test_system_is_required_when_system_tests_are_collected(project):
    result = project.runpytest()
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stdout.fnmatch_lines(["*--system is required*"])


def test_system_is_not_required_for_tests_without_a_system(pytester, fake_cprgo):
    pytester.makeconftest(ROOT_CONFTEST)
    pytester.makepyfile("def test_plain():\n    pass\n")
    assert pytester.runpytest().ret == pytest.ExitCode.OK


@pytest.mark.parametrize("system, expected", [("meditik", 1), ("meditek", 1), ("cprgo", 1), ("all", 2)])
def test_system_selects_only_its_tests(project, system, expected):
    result = project.runpytest("--system", system)
    assert result.ret == pytest.ExitCode.OK
    passed, _ = run_ids(result)
    assert passed == expected


def test_selected_system_sets_test_app(project):
    project.runpytest("--system", "cprgo")
    assert os.environ["TEST_APP"] == "cprgo-app"


def test_all_keeps_the_existing_test_app(project):
    project.runpytest("--system", "all")
    assert os.environ["TEST_APP"] == "unchanged"


def test_unknown_system_is_a_usage_error(project):
    result = project.runpytest("--system", "nope")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*Unknown system 'nope'*"])


def test_header_shows_system_user_and_env(project):
    result = project.runpytest("--system", "meditik", "--personal-number", "4444405")
    result.stdout.fnmatch_lines(["System: meditik | User: 4444405 | Env: *"])


def test_active_systems_follow_the_selection(project):
    project.makeconftest(
        ROOT_CONFTEST
        + "\n\ndef pytest_sessionfinish(session):\n"
        "    from refua_tests.systems import active_systems\n"
        "    print('ACTIVE=' + ','.join(sorted(active_systems(session.config))))\n"
    )
    result = project.runpytest("--system", "cprgo", "-s")
    result.stdout.fnmatch_lines(["*ACTIVE=cprgo*"])
    result = project.runpytest("--system", "all", "-s")
    result.stdout.fnmatch_lines(["*ACTIVE=cprgo,meditik*"])


def test_every_system_is_active_when_no_selection_was_made():
    config = SimpleNamespace(_refua_active_systems=None)
    assert systems.active_systems(config) == set(systems.SYSTEMS)
    assert systems.is_system_active(config, "meditik")


def test_inactive_system_is_reported_as_not_active():
    config = SimpleNamespace(_refua_active_systems={"cprgo"})
    assert not systems.is_system_active(config, "meditik")


def test_resolve_system_accepts_names_aliases_and_all():
    assert systems.resolve_system("Meditik").name == "meditik"
    assert systems.resolve_system("meditek").name == "meditik"
    assert systems.resolve_system("all") is None
    with pytest.raises(ValueError, match="Registered systems"):
        systems.resolve_system("unknown")
