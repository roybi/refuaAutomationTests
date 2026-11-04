"""The service must not start without an API token when it is configured to require one (the Docker image does)."""

import re

import pytest

from refua_service import settings as service_settings
from refua_service.settings import MIN_TOKEN_LENGTH, REPO_ROOT, SettingsError, load_settings

GOOD_TOKEN = "x" * MIN_TOKEN_LENGTH


@pytest.fixture(autouse=True)
def clean_environment(tmp_path, monkeypatch):
    for name in ("SERVICE_API_TOKEN", "SERVICE_REQUIRE_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("DATA_DIR", str(tmp_path))


def test_local_default_does_not_require_a_token():
    settings = load_settings()
    assert settings.api_token is None and settings.require_token is False


@pytest.mark.parametrize("value", ["true", "TRUE", "1", "yes", "on"])
def test_requiring_a_token_without_one_stops_the_service(monkeypatch, value):
    monkeypatch.setenv("SERVICE_REQUIRE_TOKEN", value)
    with pytest.raises(SettingsError, match="SERVICE_API_TOKEN"):
        load_settings()


def test_an_empty_token_counts_as_missing(monkeypatch):
    monkeypatch.setenv("SERVICE_REQUIRE_TOKEN", "true")
    monkeypatch.setenv("SERVICE_API_TOKEN", "")
    with pytest.raises(SettingsError):
        load_settings()


def test_a_short_token_is_refused_when_required(monkeypatch):
    monkeypatch.setenv("SERVICE_REQUIRE_TOKEN", "true")
    monkeypatch.setenv("SERVICE_API_TOKEN", "x" * (MIN_TOKEN_LENGTH - 1))
    with pytest.raises(SettingsError, match=str(MIN_TOKEN_LENGTH)):
        load_settings()


def test_a_long_enough_token_starts_the_service(monkeypatch):
    monkeypatch.setenv("SERVICE_REQUIRE_TOKEN", "true")
    monkeypatch.setenv("SERVICE_API_TOKEN", GOOD_TOKEN)
    settings = load_settings()
    assert settings.require_token and settings.api_token == GOOD_TOKEN


@pytest.mark.parametrize("value", ["false", "0", "no", "off", ""])
def test_the_requirement_can_be_switched_off_for_local_runs(monkeypatch, value):
    monkeypatch.setenv("SERVICE_REQUIRE_TOKEN", value)
    assert load_settings().require_token is False


def test_a_short_token_is_allowed_when_not_required(monkeypatch):
    monkeypatch.setenv("SERVICE_API_TOKEN", "short")
    assert load_settings().api_token == "short"


def test_the_error_message_does_not_contain_the_token(monkeypatch):
    monkeypatch.setenv("SERVICE_REQUIRE_TOKEN", "true")
    monkeypatch.setenv("SERVICE_API_TOKEN", "secret-short")
    with pytest.raises(SettingsError) as error:
        load_settings()
    assert "secret-short" not in str(error.value)


def test_the_docker_image_requires_the_token_by_default():
    dockerfile = (REPO_ROOT / "docker" / "tests" / "Dockerfile").read_text(encoding="utf-8")
    assert re.search(r"SERVICE_REQUIRE_TOKEN=true", dockerfile), "the image must set SERVICE_REQUIRE_TOKEN=true"


def test_settings_error_is_exported():
    assert issubclass(service_settings.SettingsError, RuntimeError)
