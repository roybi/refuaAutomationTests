"""Data-validation queries for the AWS MEDITEK database, used before/after tests.

The functions below are EXAMPLES/placeholders (table and column names are guesses) —
replace them with queries matching the real MEDITEK schema before using in a test.
Add one function per validation need and call it from the ``db`` fixture in tests:

    def test_soft_note_created(db, browser_page):
        # ... perform the UI action ...
        row = get_soft_note_by_id(db, note_id)
        assert row is not None
        assert row["status"] == "submitted"

Keep queries read-only where possible; use ``db.execute()`` only for setup/cleanup
of data the test itself owns.
"""

from __future__ import annotations

from typing import Any, Optional

from refua_core.config.database import DatabaseManager


def get_patient_by_id(db: DatabaseManager, patient_id: str) -> Optional[dict[str, Any]]:
    """Fetch a single patient row for before/after-test comparisons."""
    return db.fetch_one(
        "SELECT * FROM patients WHERE id = %s",
        (patient_id,),
    )


def get_soft_note_by_id(db: DatabaseManager, note_id: str) -> Optional[dict[str, Any]]:
    """Fetch a single soft note row created via the UI, to confirm it persisted."""
    return db.fetch_one(
        "SELECT * FROM soft_notes WHERE id = %s",
        (note_id,),
    )


def count_requests_for_patient(db: DatabaseManager, patient_id: str) -> int:
    """Count request-form submissions for a patient, e.g. to assert +1 after a test."""
    row = db.fetch_one(
        "SELECT COUNT(*) AS count FROM requests WHERE patient_id = %s",
        (patient_id,),
    )
    return int(row["count"]) if row else 0


def get_system_message_description(db: DatabaseManager, message_id: int) -> Optional[str]:
    """Fetch the description column of public.system_message for a given id."""
    row = db.fetch_one(
        "SELECT description FROM public.system_message WHERE id = %s",
        (message_id,),
    )
    return row["description"] if row else None
