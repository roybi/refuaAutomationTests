"""The homepage run list must show a gap-free, duplicate-free list while new runs arrive between "Load more" clicks."""

import shutil
import subprocess

import pytest

from refua_service.settings import REPO_ROOT

SIMULATION = REPO_ROOT / "tools" / "tests" / "js" / "runlist_sim.js"


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_run_list_has_no_gaps_when_new_runs_arrive_after_load_more():
    result = subprocess.run(["node", str(SIMULATION)], cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "FAIL" not in result.stdout
    assert "PASS new run after Load more" in result.stdout