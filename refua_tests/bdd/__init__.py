"""
BDD (Behavior-Driven Development) Testing Package

This package contains Gherkin feature files and step definitions for behavior-driven testing.
It provides an additional layer of testing alongside traditional pytest tests.

Structure:
- features/: Gherkin .feature files describing test scenarios
- step_defs/: Python step definitions implementing the Gherkin steps
- conftest.py: BDD-specific pytest fixtures and configuration

Usage:
    pytest refua_tests/bdd/ -v                    # Run all BDD tests
    pytest refua_tests/bdd/features/main_page.feature -v  # Run specific feature

Requirements:
    - pytest-bdd: BDD framework for pytest
    - All BDD tests can run alongside traditional pytest tests
"""

__all__ = ['features', 'step_defs']
