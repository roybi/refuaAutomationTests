"""Generate a "pending clarification" BDD feature file from a cases JSON.

Every MediTik workbook splits into Ready cases (implemented) and cases blocked
on Product/Security/API/UX/Business-Rule/Data-Model confirmation. The blocked
ones are still registered as Gherkin scenarios — collected and skipped — so the
source case IDs and their Given/When/Then survive in the suite.

This tool renders that file straight from the generated cases JSON, so the
scenario text is a faithful copy of the workbook instead of a hand transcription.

Usage:
    python tools/generate_pending_feature.py docs/setup/SCHEDULING_CASES.json \
        refua_tests/bdd/features/meditik_scheduling_pending.feature \
        --feature-name "Appointment Scheduling workflows awaiting approved clarification" \
        --tags "@bdd @meditik @scheduling" --case-label APPOINTMENTS
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

READY = "Ready"


def _clean(text: str) -> str:
    """Collapse a workbook cell into one Gherkin-safe line."""
    return " ".join(str(text or "").split())


def _strip_keyword(text: str, keyword: str) -> str:
    """Workbook cells sometimes already start with Given/When/Then."""
    cleaned = _clean(text)
    prefix = f"{keyword} "
    if cleaned.lower().startswith(prefix.lower()):
        cleaned = cleaned[len(prefix):]
    return cleaned


def render(cases: list[dict], feature_name: str, tags: str, case_label: str) -> str:
    lines = [tags, f"Feature: {feature_name}", "  Pending specifications, not implemented UI or backend coverage.", ""]

    for case in cases:
        tc_id = case.get("TC_ID", "")
        scenario = _clean(case.get("Scenario", "")) or tc_id
        given = _strip_keyword(case.get("Given", ""), "Given")
        when = _strip_keyword(case.get("When", ""), "When")
        then = _strip_keyword(case.get("Then / Expected Result", ""), "Then")

        lines.append(f"  Scenario: {tc_id} - {scenario}")
        lines.append(
            f'    Given {case_label} case "{tc_id}" has approved execution contracts'
        )
        if given:
            lines.append(f"    Given {given}")
        if when:
            lines.append(f"    When {when}")
        if then:
            lines.append(f"    Then {then}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases_json", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--feature-name", required=True)
    parser.add_argument("--tags", required=True)
    parser.add_argument("--case-label", required=True)
    args = parser.parse_args()

    cases = json.loads(args.cases_json.read_text(encoding="utf-8-sig"))
    pending = [c for c in cases if c.get("Clarification Status") != READY]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render(pending, args.feature_name, args.tags, args.case_label),
        encoding="utf-8",
    )
    print(f"wrote {len(pending)} pending scenarios -> {args.output}")


if __name__ == "__main__":
    main()
