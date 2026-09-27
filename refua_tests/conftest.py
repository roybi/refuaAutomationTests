"""Suite-wide fixtures shared by refua_tests/tests and refua_tests/bdd."""

import logging
import os
import warnings

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def meditik_seed_session():
    """BEFORE ALL: seed 3 requests of every Meditik request type. AFTER ALL: cleanup per MEDITIK_SEED_CLEANUP.

    Per execution: --personal-number 4444410 (or TEST_PERSONAL_NUMBER); it must match
    SEED_ALLOWED_PERSONAL_NUMBERS (numbers/ranges). Configured in .env.<env>: MEDITIK_SEED_ENV
    (must equal TEST_ENV), optional MEDITIK_SEED_DATASET (default "all") and
    MEDITIK_SEED_CLEANUP ("report" keeps rows, "delete-owned" removes them). A blocked or
    failed seed is reported as a warning and yields None; it never fails the suite.
    """
    from dotenv import load_dotenv

    from refua_tests.utils import meditik_seed as ms

    test_env = os.getenv("TEST_ENV", "").strip().lower()
    if test_env:
        load_dotenv(ms.REPO_ROOT / f".env.{test_env}", override=False)
    seed_env = os.getenv("MEDITIK_SEED_ENV", "").strip().lower()
    if not seed_env or seed_env != test_env:
        yield None
        return
    if os.getenv("TEST_APP", "meditek").lower() not in ("meditek", "meditik"):
        yield None
        return
    # Under xdist each worker has its own session; only one worker owns the seed.
    if os.getenv("PYTEST_XDIST_WORKER", "gw0") != "gw0":
        yield None
        return

    dataset = os.getenv("MEDITIK_SEED_DATASET", "all")
    try:
        manifest = ms.seed(seed_env, os.getenv("TEST_PERSONAL_NUMBER", ""), dataset)
    except Exception as error:  # noqa: BLE001 - seeding problems must not abort unrelated tests
        message = f"Meditik DB seed skipped ({type(error).__name__}: {error})"
        logger.warning(message)
        warnings.warn(message)
        yield None
        return

    logger.info("Meditik DB seed %s: %d requests committed (%s)", manifest.run_id,
                len(manifest.entities), dataset)
    try:
        yield manifest
    finally:
        ms.cleanup(manifest, os.getenv("MEDITIK_SEED_CLEANUP", "report"))
        logger.info("Meditik DB seed %s cleanup status: %s", manifest.run_id, manifest.status)
        for message in manifest.warnings:
            logger.warning(message)
            warnings.warn(message)


@pytest.fixture
def meditik_seeded_requests(meditik_seed_session):
    """This run's seed manifest (entities with request/child IDs); skips the test if seeding did not run."""
    if meditik_seed_session is None:
        pytest.skip("Meditik DB seed data is not available for this run.")
    return meditik_seed_session
