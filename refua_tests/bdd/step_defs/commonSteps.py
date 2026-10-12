"""
Backward-compatibility shim.

The generic step definitions have been moved to refua_core.bdd.common_steps
so they can be shared across any app test suite that depends on the framework.

Importing this module re-exports everything from Core so existing imports and
pytest-bdd step registrations continue to work without changes.
"""

from refua_core.bdd.common_steps import *  # noqa: F401, F403
