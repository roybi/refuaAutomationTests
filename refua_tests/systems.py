"""Registry of the systems (applications) this repository tests.

A system owns the tests carrying its marker: ``@pytest.mark.<marker>`` on pytest tests and
``@<marker>`` on BDD feature files. ``--system`` (see the root ``conftest.py``) selects which
system a run targets, so one entry point can serve Meditik today and CPR GO later.

To onboard a new system, add one ``SystemSpec`` below and follow the checklist in
``docs/guides/RUNBOOK.md`` ("Adding a new system").
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set

ALL = "all"


@dataclass(frozen=True)
class SystemSpec:
    name: str
    marker: str
    # Value exported as TEST_APP; it is also what the CORE framework expects as ``--app``.
    app_id: str
    description: str
    requires_user: bool = False
    aliases: tuple = ()


SYSTEMS: Dict[str, SystemSpec] = {
    spec.name: spec
    for spec in (
        SystemSpec(
            name="meditik",
            marker="meditik",
            app_id="meditek",
            description="MEDITIK patient portal",
            requires_user=True,
            aliases=("meditek",),
        ),
    )
}


def system_names() -> List[str]:
    return sorted(SYSTEMS)


def resolve_system(value: str) -> Optional[SystemSpec]:
    """Return the spec for a system name or alias; ``None`` means ``all`` systems."""
    name = (value or "").strip().lower()
    if name == ALL:
        return None
    for spec in SYSTEMS.values():
        if name == spec.name or name in spec.aliases:
            return spec
    valid = ", ".join(system_names() + [ALL])
    raise ValueError(
        f"Unknown system '{value}'. Registered systems: {valid}. "
        "To add a system, register it in refua_tests/systems.py "
        "(see docs/guides/RUNBOOK.md, 'Adding a new system')."
    )


def owners_of(item) -> Set[str]:
    """Names of the registered systems whose marker is on a collected test."""
    marks = {mark.name for mark in item.iter_markers()}
    return {spec.name for spec in SYSTEMS.values() if spec.marker in marks}


def active_systems(config) -> Set[str]:
    """Systems with at least one selected test; every system when no ``--system`` was given."""
    active = getattr(config, "_refua_active_systems", None)
    return set(SYSTEMS) if active is None else set(active)


def is_system_active(config, name: str) -> bool:
    return name in active_systems(config)


def describe(names: Iterable[str]) -> str:
    return ", ".join(sorted(names)) or "none"
