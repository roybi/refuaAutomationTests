"""Soft notes: label/copy mismatches that should not fail the hard test.

Allure has no native yellow status for a passed test. We:
  - attach a per-test \"⚠ Soft warnings\" log
  - tag the test ``soft-warning`` (filterable in Allure)
  - add a yellow HTML banner on the test description
  - optionally escalate via SOFT_NOTES_MODE=broken|fail (orange/red badge)

SOFT_NOTES_MODE:
  note   (default) — test stays green; warnings visible in Allure
  broken — raise non-AssertionError in teardown → Allure \"broken\" (orange)
  fail   — pytest.fail → Allure \"failed\" (red)
"""

from __future__ import annotations

import os
import warnings
from contextvars import ContextVar

_soft_notes: ContextVar[list[str] | None] = ContextVar("meditik_soft_notes", default=None)
_session_notes: list[str] = []


def clear_soft_notes() -> None:
    _soft_notes.set([])


def get_soft_notes() -> list[str]:
    return list(_soft_notes.get() or [])


def drain_soft_notes() -> list[str]:
    notes = get_soft_notes()
    _soft_notes.set([])
    return notes


def session_soft_notes() -> list[str]:
    return list(_session_notes)


def clear_session_soft_notes() -> None:
    _session_notes.clear()


def soft_notes_mode() -> str:
    return (os.getenv("SOFT_NOTES_MODE") or "note").strip().lower()


def report_soft_note(message: str, *, name: str = "Soft note (label/copy)") -> None:
    """Record a non-fatal note (Allure step + warning; summary attached at teardown)."""
    notes = _soft_notes.get()
    if notes is None:
        notes = []
        _soft_notes.set(notes)
    notes.append(message)
    _session_notes.append(message)

    warnings.warn(message, UserWarning, stacklevel=2)
    try:
        import allure

        with allure.step(f"⚠ {message}"):
            pass
    except Exception:
        # warnings.warn above already surfaces the note; avoid echoing it to stdout.
        pass


def publish_soft_notes_to_allure(notes: list[str]) -> None:
    """Call at end of test: summary attachment, tag, yellow description banner."""
    if not notes:
        return
    try:
        import allure
        from allure_commons.types import Severity

        summary = "\n".join(f"• {n}" for n in notes)
        allure.attach(
            summary,
            name="⚠ Soft warnings",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.dynamic.tag("soft-warning")
        allure.dynamic.label("soft_warning", "true")
        allure.dynamic.severity(Severity.MINOR)
        banner = (
            '<div style="background:#FFF3CD;border:1px solid #FFECB5;'
            'color:#664D03;padding:12px;border-radius:6px;margin:8px 0;">'
            "<b>⚠ Soft warnings</b> — data-testid OK; UI copy/label differed."
            f"<pre style='white-space:pre-wrap;margin:8px 0 0'>{_html_escape(summary)}</pre>"
            "</div>"
        )
        allure.dynamic.description_html(banner)
    except Exception:
        print("[SOFT WARNINGS]\n" + "\n".join(notes))


def _html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
