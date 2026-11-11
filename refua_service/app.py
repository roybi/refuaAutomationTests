"""FastAPI backend: run parameters in, test runs and Allure reports out.

Start locally:  uvicorn refua_service.app:app --port 8080
"""

import hmac
import html
import re
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from refua_tests.systems import ALL, SYSTEMS, resolve_system, system_names
from tools import update_bdd_tags

from . import reports
from .runs import DuplicateRunError, RunManager
from .settings import load_settings

SUITES = ("all", "bdd", "pytest")
TAG_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
STATIC_DIR = Path(__file__).parent / "static"
LOGOS = (("meditik-logo.png", "MediTik"), ("idf-computer-service-directorate-logo.png", "IDF Computer Service Directorate"))

settings = load_settings()
manager: Optional[RunManager] = None


def get_manager() -> RunManager:
    global manager
    if manager is None:
        manager = RunManager(settings)
    return manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_manager()
    yield
    if manager is not None:
        manager.shutdown()


app = FastAPI(title="Refua automation runner", lifespan=lifespan)


def require_token(x_api_token: Optional[str] = Header(default=None)) -> None:
    """Triggering or cancelling runs needs the token when SERVICE_API_TOKEN is set; reads stay open."""
    if settings.api_token and not (x_api_token and hmac.compare_digest(x_api_token, settings.api_token)):
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Token")


@lru_cache(maxsize=1)
def available_tags() -> List[dict]:
    """Tags with at least one runnable scenario; the feature files are fixed for the life of the image."""
    try:
        collected = update_bdd_tags.collect()
    except OSError:
        return []
    return [{"name": name, "total": info["total"], "runnable": info["runnable"]}
            for name, info in sorted(collected.items()) if info["runnable"] > 0]


class RunRequest(BaseModel):
    system: str = Field(min_length=1, max_length=32)
    suite: str = "all"
    tags: Optional[str] = Field(default=None, max_length=64)
    user: str = Field(pattern=r"^[0-9]{3,12}$")
    env: str = "test"
    clean: bool = True


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "allure": bool(settings.allure_bin), "data_dir": str(settings.data_dir)}


@app.get("/api/options")
def options() -> dict:
    return {
        "systems": [{"name": s.name, "description": s.description} for s in SYSTEMS.values()] + [
            {"name": ALL, "description": "Every registered system"}],
        "suites": list(SUITES),
        "envs": list(settings.allowed_envs),
        "tags": available_tags(),
        "users": settings.selectable_users(),
        "restrict_users": bool(settings.user_ranges),
        "token_required": bool(settings.api_token),
        "max_concurrent_runs": settings.max_concurrent_runs,
    }


@app.post("/api/runs", status_code=201, dependencies=[Depends(require_token)])
def create_run(request: RunRequest) -> dict:
    try:
        spec = resolve_system(request.system)
    except ValueError as error:
        raise HTTPException(422, str(error))
    system = spec.name if spec else ALL
    if request.suite not in SUITES:
        raise HTTPException(422, f"suite must be one of {', '.join(SUITES)}")
    if request.env.lower() not in settings.allowed_envs:
        raise HTTPException(422, f"env must be one of {', '.join(settings.allowed_envs)}")
    if not settings.is_user_allowed(request.user):
        raise HTTPException(422, f"user {request.user} is not in the allowed user list")
    tags = (request.tags or "").strip() or None
    if tags and (not TAG_PATTERN.match(tags) or tags not in {t["name"] for t in available_tags()}):
        raise HTTPException(422, f"tag '{tags}' is not an available runnable tag")
    try:
        return get_manager().submit(system, request.suite, tags, request.user, request.env.lower(), request.clean)
    except DuplicateRunError as error:
        raise HTTPException(409, str(error))


@app.get("/api/runs")
def list_runs(limit: int = Query(default=50, ge=1, le=500), offset: int = Query(default=0, ge=0),
              status: Optional[str] = Query(default=None, pattern=r"^[a-z_]{1,20}$"),
              system: Optional[str] = Query(default=None, max_length=32),
              date_from: Optional[str] = Query(default=None, pattern=DATE_PATTERN),
              date_to: Optional[str] = Query(default=None, pattern=DATE_PATTERN)) -> List[dict]:
    return get_manager().list(limit, offset, status, system, date_from, date_to)


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict:
    run = get_manager().get(run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return run


@app.get("/api/runs/{run_id}/log")
def get_log(run_id: str, offset: int = Query(default=0, ge=0)) -> dict:
    chunk = get_manager().read_log(run_id, offset)
    if chunk is None:
        raise HTTPException(404, "Run not found")
    return chunk


@app.post("/api/runs/{run_id}/cancel", dependencies=[Depends(require_token)])
def cancel_run(run_id: str) -> dict:
    run = get_manager().cancel(run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return run


@app.get("/api/reports/status")
def reports_status() -> dict:
    """Whether the Allure CLI runs (reports can be built), how many executions exist and how many have a report."""
    version = reports.allure_version(settings)
    report_ids = reports.stored_report_ids(settings)
    run_ids = {path.stem for path in settings.runs_dir.glob("*.json")}
    return {"allure_ready": version is not None, "allure_version": version,
            "run_count": len(run_ids), "runs_with_report": len(run_ids.intersection(report_ids)),
            "report_count": len(report_ids), "latest_report": reports.latest_report_id(settings)}


def _page(title: str, body: str) -> HTMLResponse:
    """Standalone page for the report links, with the same header and logos as the main page."""
    logos = "".join(f'<img src="/assets/{name}" alt="{html.escape(alt)}" height="40">' for name, alt in LOGOS)
    return HTMLResponse(
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(title)}</title>"
        "<style>body{font:14px system-ui,sans-serif;margin:0;color:#1c2733}"
        "header{background:#16222f;color:#fff;padding:12px 24px;display:flex;align-items:center;gap:16px;"
        "position:sticky;top:0}"
        "header h1{font-size:18px;margin:0;flex:1}header a{color:#9cc4ff}header img{border-radius:6px}"
        "main{margin:24px}table{border-collapse:collapse}"
        "th,td{text-align:left;padding:6px 12px;border-bottom:1px solid #d9dee4}"
        ".notice{max-width:640px;padding:12px 16px;border:1px solid #d9dee4;border-radius:8px;background:#f4f6f8}"
        ".notice.warn{border-color:#b26a00;background:#fff6e5}</style></head><body>"
        '<header><h1>Refua automation runner</h1><a href="/">Runs</a><a href="/reports/">All reports</a>'
        f'<a href="/reports/latest">Latest report</a>{logos}</header><main>{body}</main></body></html>')


def _report_notice(report_count: int) -> str:
    """The message shown instead of reports: Allure not usable, or nothing generated yet. Empty when all is well."""
    if reports.allure_version(settings) is None:
        return ('<p class="notice warn"><strong>The Allure report generator is not available on this server.</strong> '
                "Test runs cannot produce reports until it is fixed. Please tell the team that maintains the service.</p>")
    if report_count == 0:
        return ('<p class="notice"><strong>No reports yet.</strong> The Allure report generator is running. '
                'A report appears here after the first test run finishes. Start one from the <a href="/">main page</a>.</p>')
    return ""


@app.get("/reports/latest")
@app.get("/reports/latest/")
def latest_report():
    run_id = reports.latest_report_id(settings)
    if run_id is None:
        return _page("Latest report", "<h2>Latest report</h2>" + _report_notice(0))
    return RedirectResponse(f"/reports/{run_id}/")


@app.get("/reports", include_in_schema=False)
@app.get("/reports/")
def reports_index() -> HTMLResponse:
    """Every stored report, newest first (the static mount below has no directory listing)."""
    rows = []
    for report_id in reports.stored_report_ids(settings):
        run = get_manager().get(report_id) or {}
        summary = run.get("summary") or {}
        started = (run.get("started_at") or run.get("created_at") or "-").replace("T", " ")[:19]
        counts = (f"{summary.get('passed', 0)} passed, {summary.get('failed', 0) + summary.get('broken', 0)} failed, "
                  f"{summary.get('skipped', 0)} skipped") if summary else "-"
        cells = [started, run.get("system", "-"), run.get("tags") or "-", run.get("user", "-"), run.get("env", "-"),
                 run.get("status", "-"), counts]
        rows.append(f'<tr><td><a href="/reports/{html.escape(report_id)}/">{html.escape(report_id)}</a></td>'
                    + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in cells) + "</tr>")
    if not rows:
        return _page("Reports", "<h2>Reports (0)</h2>" + _report_notice(0))
    return _page(
        "Reports",
        f"<h2>Reports ({len(rows)})</h2>" + _report_notice(len(rows))
        + '<table><thead><tr><th>Run</th><th>Started</th><th>System</th><th>Tag</th><th>User</th><th>Env</th>'
        f"<th>Status</th><th>Results</th></tr></thead><tbody>{''.join(rows)}</tbody></table>")


settings.ensure_directories()
app.mount("/assets", StaticFiles(directory=STATIC_DIR / "img"), name="assets")
app.mount("/reports", StaticFiles(directory=settings.reports_dir, html=True), name="reports")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
