"""
Step Definitions for Main Page Feature

Implements the Gherkin steps defined in main_page.feature
"""

import pytest
from pytest_bdd import given, when, then, parsers, scenarios
from refua_tests.pages.mainPage import MainPage

# Load all scenarios from main_page.feature
scenarios('../features/main_page.feature')


# Fixtures

@pytest.fixture
def context():
    """Shared context dictionary for storing data between steps"""
    return {}


@pytest.fixture
def main_page(setup_browser):
    """Create MainPage instance"""
    page = setup_browser
    return MainPage(page)


# Given Steps

@given("I am testing the main page")
def testing_main_page(main_page, context):
    """Initialize main page for testing"""
    context['main_page'] = main_page


@given(parsers.parse('I am testing the main page for "{environment}" environment'))
def testing_main_page_for_env(main_page, context, environment):
    """Initialize main page for specific environment"""
    context['main_page'] = main_page
    context['environment'] = environment


@given("I have a main page object")
def have_main_page_object(main_page, context):
    """Store main page object in context"""
    context['main_page'] = main_page


# When Steps

@when(parsers.parse('I get the items base URL for "{environment}" environment'))
def get_items_base_url_for_env(context, environment):
    """Get items base URL for specific environment"""
    main_page = context['main_page']
    url = main_page.items_base_url
    env = main_page.get_current_environment()
    context['url'] = url
    context['environment'] = env


@when("I get the items base URL")
def get_items_base_url(main_page, context):
    """Get items base URL"""
    url = main_page.items_base_url
    context['url'] = url
    context['result'] = url


@when("I get the current environment")
def get_current_environment(main_page, context):
    """Get current environment"""
    env = main_page.get_current_environment()
    context['environment'] = env


@when(parsers.parse('I access the "{property}" property'))
def access_property(main_page, context, property):
    """Access a property on main page"""
    value = getattr(main_page, property, None)
    context['result'] = value


# Then Steps

@then(parsers.parse('the URL should contain "{text}"'))
def url_should_contain(context, text):
    """Verify URL contains specific text"""
    url = context.get('url')
    assert text in url, f"URL should contain '{text}', got '{url}'"


@then(parsers.parse('the full URL should be "{expected_url}"'))
def full_url_should_be(context, expected_url):
    """Verify full URL matches expected"""
    url = context.get('url')
    assert url == expected_url, f"Expected '{expected_url}', got '{url}'"


@then(parsers.parse('the current environment should be "{expected_env}"'))
def current_environment_should_be(context, expected_env):
    """Verify current environment matches expected"""
    env = context.get('environment')
    assert env == expected_env, f"Environment should be '{expected_env}', got '{env}'"


@then(parsers.parse('the main page should have the "{method}" method'))
def main_page_should_have_method(main_page, method):
    """Verify main page has specific method"""
    assert hasattr(main_page, method), f"MainPage should have {method} method"


@then(parsers.parse('the main page should have "{attribute}" attribute'))
def main_page_should_have_attribute(main_page, attribute):
    """Verify main page has specific attribute"""
    assert hasattr(main_page, attribute), f"MainPage should have {attribute} attribute"


@then(parsers.parse('the main page should have "{property}" property'))
def main_page_should_have_property(main_page, property):
    """Verify main page has specific property"""
    assert hasattr(main_page, property), f"MainPage should have {property} property"


@then(parsers.parse('the main page should have "{method}" method'))
def main_page_should_have_method_callable(main_page, method):
    """Verify main page has specific method"""
    assert hasattr(main_page, method), f"MainPage should have {method} method"


@then("the environment should be a string")
def environment_should_be_string(context):
    """Verify environment is a string"""
    env = context.get('environment')
    assert isinstance(env, str), f"Environment should be string, got {type(env)}"


@then(parsers.parse('the environment should be one of "{values}"'))
def environment_should_be_one_of(context, values):
    """Verify environment is one of allowed values"""
    env = context.get('environment')
    allowed_values = [v.strip() for v in values.split(',')]
    assert env in allowed_values, f"Environment should be one of {allowed_values}, got '{env}'"


@then(parsers.parse('the URL should contain the "{domain_pattern}" domain'))
def url_should_contain_domain_pattern(context, domain_pattern):
    """Verify URL contains domain pattern for environment"""
    url = context.get('url')
    environment = context.get('environment')

    # For prod, also verify it doesn't contain test/preprod
    if domain_pattern == "meditik.medical.idf.il" and environment == "prod":
        assert ".test" not in url, f"Prod URL should not contain '.test': {url}"
        assert ".preprod" not in url, f"Prod URL should not contain '.preprod': {url}"

    assert domain_pattern in url, f"URL should contain '{domain_pattern}', got '{url}'"


@then("the URL should use HTTPS protocol")
def url_should_use_https(context):
    """Verify URL uses HTTPS"""
    url = context.get('url')
    assert url.startswith("https://"), f"URL should use HTTPS protocol: {url}"


@then(parsers.parse('the URL should end with "{path}" path'))
def url_should_end_with_path(context, path):
    """Verify URL ends with specific path"""
    url = context.get('url')
    assert url.endswith(path), f"URL should end with '{path}': {url}"
