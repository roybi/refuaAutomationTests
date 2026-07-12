"""
Common Step Definitions for BDD Tests

Provides reusable step definitions that can be used across multiple feature files.
"""

import pytest
from pytest_bdd import given, when, then, parsers


@given("the test environment is configured")
def test_environment_configured():
    """Verify test environment is configured"""
    # Environment is already configured by BaseTest setup
    pass


@given("the browser is launched")
def browser_launched(setup_browser):
    """Verify browser is launched"""
    # Browser is launched by BaseTest setup via fixture
    assert setup_browser is not None
    pass


@then(parsers.parse('the "{attribute}" should be a string'))
def attribute_should_be_string(context, attribute):
    """Verify attribute is a string"""
    value = context.get(attribute)
    assert isinstance(value, str), f"{attribute} should be string, got {type(value)}"


@then(parsers.parse('it should return a string'))
def should_return_string(context):
    """Verify returned value is a string"""
    value = context.get('result')
    assert isinstance(value, str), f"Result should be string, got {type(value)}"


@then(parsers.parse('it should start with "{prefix}"'))
def should_start_with(context, prefix):
    """Verify value starts with prefix"""
    value = context.get('result')
    assert value.startswith(prefix), f"Value should start with '{prefix}', got '{value}'"


@then(parsers.parse('it should end with "{suffix}"'))
def should_end_with(context, suffix):
    """Verify value ends with suffix"""
    value = context.get('result')
    assert value.endswith(suffix), f"Value should end with '{suffix}', got '{value}'"


@then(parsers.parse('the "{property}" property should not be None'))
def property_should_not_be_none(main_page, property):
    """Verify property is not None"""
    value = getattr(main_page, property, None)
    assert value is not None, f"{property} should not be None"


@then(parsers.parse('the "{method}" method should be callable'))
def method_should_be_callable(main_page, method):
    """Verify method is callable"""
    method_obj = getattr(main_page, method, None)
    assert callable(method_obj), f"{method} should be callable"


@then(parsers.parse('the "{attribute}" should be initialized'))
def attribute_should_be_initialized(main_page, attribute):
    """Verify attribute is initialized"""
    value = getattr(main_page, attribute, None)
    assert value is not None, f"{attribute} should be initialized"
