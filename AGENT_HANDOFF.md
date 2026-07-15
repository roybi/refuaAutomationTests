# AGENT HANDOFF FILE

> **Shared task state between LLM agents (Claude Code + GitHub Copilot).**
> This file is the single source of truth for in-progress work. When one agent
> runs out of tokens/context, the other agent continues from the exact point
> recorded here.

---

## PROTOCOL — RULES FOR EVERY AGENT (read this first)

1. **On session start**: Read this ENTIRE file before doing anything else. If `STATUS` is `IN_PROGRESS`, continue from the `RESUME POINT` section — do NOT restart the task from scratch.
2. **While working**: After completing each step in the plan, immediately update the checklist (`[ ]` → `[x]`) and append a short entry to the `WORK LOG`.
3. **Before stopping** (token limit near, session end, or user says stop): Update `RESUME POINT` with (a) the exact file + line you were editing, (b) what you were about to do next, (c) any commands that still need to run. Then set `LAST AGENT` and `LAST UPDATED`.
4. **Never delete** previous WORK LOG entries — only append. History is how the other agent understands decisions already made.
5. **When the task is fully done**: Set `STATUS: DONE`, run the validation commands in `DEFINITION OF DONE`, and clear the `RESUME POINT` section.
6. **Conflicts**: If this file contradicts the code, trust the code and note the discrepancy in the WORK LOG.

---

## CURRENT TASK

**STATUS**: `IDLE`  <!-- IDLE | IN_PROGRESS | BLOCKED | DONE -->
**TASK NAME**: _(none — fill in when starting a task)_
**STARTED**: _(YYYY-MM-DD HH:MM)_
**LAST AGENT**: _(Claude Code | GitHub Copilot)_
**LAST UPDATED**: _(YYYY-MM-DD HH:MM)_
**BRANCH**: `roy_dev_automationTests`

### Task description
_(1-3 sentences: what the user asked for, in plain language.)_

### Definition of done
_(How to verify the task is complete — e.g. `TEST_ENV=test pytest refua_tests/tests/ -v` passes, feature works in browser, etc.)_

---

## PLAN / CHECKLIST

<!-- Break the task into small steps. Mark [x] the moment a step is complete. -->

- [ ] Step 1 —
- [ ] Step 2 —
- [ ] Step 3 —

---

## RESUME POINT  ⟵ the next agent starts HERE

**Current step**: _(which checklist step is in progress)_
**File being edited**: _(path + approx. line number)_
**Exactly what to do next**: _(be specific — "add the `wait_for_popup` method to `popUpInfo.py` after line 42, then call it from `test_main_page.py::test_popup`")_
**Commands still to run**: _(e.g. pytest command, pip install, git commit)_
**Known blockers / gotchas**: _(anything the next agent must know to avoid breaking things)_

---

## FILES TOUCHED THIS TASK

<!-- Keep updated so the next agent knows the blast radius. -->

| File | Change | Status |
|------|--------|--------|
| _(path)_ | _(what was changed)_ | _(done / in progress)_ |

---

## KEY DECISIONS & CONTEXT

<!-- Decisions already made — the next agent must NOT re-litigate these. -->

- _(e.g. "Using Page Object Model — locators as @property, per CLAUDE.md")_
- _(e.g. "Tests run with TEST_ENV=test; session bypass enabled via SKIP_2FA")_

---

## WORK LOG (append only — newest at bottom)

| Date/Time | Agent | What was done |
|-----------|-------|----------------|
| 2026-07-12 | Claude Code | Created this handoff file and protocol. |
| 2026-07-15 | Claude Code | Verified `new_tests.py` + all `home_Page.py` locators against the live app via Playwright — locators OK, login button works. **BLOCKER found: the TEST environment app cannot complete MSAL login** — after redirect back to `/login#code=...`, the token endpoint returns 400 AADSTS70008 and the app loops forever; the dashboard is unreachable. Contributing: 3.2 MB `main` bundle served `no-store` at 60–90 s/download since the 2026-07-13 redeploy (also breaks the 60 s `goto` in `conftest._auth_state_bypasses_2fa`). Recaptured session JSON (expires 2026-07-18) but it contains cookies only, **no MSAL localStorage tokens** (capture ran mid-loop), so the conftest gate triggers interactive recapture every run. Test runs fail in setup until the app team fixes the env (AAD Trace ID 7324488b-9cba-426b-b55a-a8b0d9181600, 2026-07-15 10:33 UTC). Created `documents/TEST_EXECUTION_PROCEDURE.md` (run tests + Allure); verified Allure report generation works. |

---

## PROJECT QUICK REFERENCE (static — rarely changes)

- **Project**: refuaAutomationTests — Playwright/pytest test automation for the MEDITEK medical app.
- **Structure**: page objects in `refua_tests/pages/`, tests in `refua_tests/tests/`, fixtures in `refua_tests/tests/conftest.py`.
- **Run tests**: `TEST_ENV=test pytest refua_tests/tests/ -v`
- **Run one test**: `TEST_ENV=test pytest refua_tests/tests/test_<file>.py -v -k "<name>"`
- **Conventions**: see `CLAUDE.md` (page objects inherit `BasePage`, tests named `test_<feature>.py`, markers in `pytest.ini`).
- **Commit style**: `test: <description>` / `fix: <description>`; commit + push after validated changes.
