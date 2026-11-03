"""The DB seed guard must accept container settings (env vars) but never silently pick another environment."""

import pytest

from refua_tests.utils import meditik_seed as seed


@pytest.fixture
def no_env_files(tmp_path, monkeypatch):
    monkeypatch.setattr(seed, "REPO_ROOT", tmp_path)  # empty folder: no .env.test / .env.prod
    for name in ("MEDITIK_SEED_ENV", "ORM_DB_HOST", "ORM_DB_DATABASE"):
        monkeypatch.delenv(name, raising=False)
    return tmp_path


def test_container_settings_from_environment_variables_are_accepted(no_env_files, monkeypatch):
    monkeypatch.setenv("MEDITIK_SEED_ENV", "test")
    monkeypatch.setenv("ORM_DB_HOST", "db.example")
    seed.load_env("test")  # must not raise


def test_missing_file_without_explicit_seed_env_is_refused(no_env_files, monkeypatch):
    monkeypatch.setenv("ORM_DB_HOST", "db.example")
    with pytest.raises(seed.SeedGuardError, match="no fallback"):
        seed.load_env("test")


def test_missing_file_with_seed_env_for_another_environment_is_refused(no_env_files, monkeypatch):
    monkeypatch.setenv("MEDITIK_SEED_ENV", "preprod")
    monkeypatch.setenv("ORM_DB_HOST", "db.example")
    with pytest.raises(seed.SeedGuardError, match="no fallback"):
        seed.load_env("test")


def test_missing_file_without_db_host_is_refused(no_env_files, monkeypatch):
    monkeypatch.setenv("MEDITIK_SEED_ENV", "test")
    with pytest.raises(seed.SeedGuardError, match="no fallback"):
        seed.load_env("test")


def test_prod_is_never_allowed(no_env_files, monkeypatch):
    monkeypatch.setenv("MEDITIK_SEED_ENV", "prod")
    monkeypatch.setenv("ORM_DB_HOST", "db.example")
    with pytest.raises(seed.SeedGuardError, match="allowed only"):
        seed.load_env("prod")
