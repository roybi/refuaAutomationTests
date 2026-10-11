# GitHub Copilot Instructions — refuaAutomationTests

## ⚠️ Multi-Agent Handoff (MANDATORY — read first)

This repository is worked on by multiple LLM agents (GitHub Copilot and Claude Code).
**At the start of every session, read `AGENT_HANDOFF.md` in the repo root.**

- If its `STATUS` is `IN_PROGRESS`, continue from the `RESUME POINT` section — do NOT restart the task from scratch.
- Follow the PROTOCOL rules in that file:
  - Mark checklist steps `[x]` as you complete them.
  - Append entries to the WORK LOG (never delete history).
  - Before stopping (token/context limit, session end), fill in the RESUME POINT with the exact file, line, and next action so the other agent can continue.
- Respect decisions listed under KEY DECISIONS & CONTEXT — do not re-litigate them.

## Project Overview

**refuaAutomationTests** — Playwright/pytest test automation for the MEDITEK medical application. Depends on the `refua-automation-core` framework package.

## Conventions

- **Page objects**: `refua_tests/pages/<feature>_page.py`, inherit from `BasePage`, locators as `@property`.
- **Tests**: `refua_tests/tests/test_<feature>.py`, use `@pytest.mark` markers defined in `pytest.ini`.
- **Fixtures**: shared fixtures in `refua_tests/tests/conftest.py`; data factories in `refua_tests/fixtures/test_data.py`.
- **Run tests**: `TEST_ENV=test pytest refua_tests/tests/ -v`
- **Commits**: `test: <description>` / `fix: <description>`; push after validated changes.

Full details: see `CLAUDE.md`, `README.md` and `docs/architecture/ARCHITECTURE.md`.
