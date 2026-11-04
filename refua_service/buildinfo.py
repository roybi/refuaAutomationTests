"""What the service is running: stored with every run so a result can be tied to the exact code that produced it."""

import os
import platform
from functools import lru_cache
from importlib import metadata
from typing import Dict, Optional


def _distribution_version(*names: str) -> Optional[str]:
    for name in names:
        try:
            return metadata.version(name)
        except metadata.PackageNotFoundError:
            continue
    return None


def _core_version() -> Optional[str]:
    found = _distribution_version("refua-core", "refua_core")
    if found:
        return found
    try:
        import refua_core.version as core_version
        return str(core_version.__version__)
    except Exception:  # noqa: BLE001 - any import problem just means "unknown"
        return None


@lru_cache(maxsize=1)
def collect() -> Dict[str, Optional[str]]:
    """IMAGE_TAG and GIT_SHA are set at image build time (docker/tests/Dockerfile); both are None outside the image."""
    return {
        "image_tag": os.getenv("IMAGE_TAG") or None,
        "git_sha": os.getenv("GIT_SHA") or None,
        "core_version": _core_version(),
        "playwright_version": _distribution_version("playwright"),
        "python_version": platform.python_version(),
    }
