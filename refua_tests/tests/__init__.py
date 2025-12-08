"""
Test Cases Module

Contains test cases for MEDITEK application.
All tests inherit from refua_core.core.BaseTest.

Execution:
    # Run all tests
    TEST_ENV=test pytest refua_tests/tests/ -v

    # Run specific test file
    TEST_ENV=test pytest refua_tests/tests/test_authentication.py -v

    # Run tests matching pattern
    TEST_ENV=test pytest refua_tests/tests/ -k "login" -v

    # Run with Allure reporting
    TEST_ENV=test pytest refua_tests/tests/ --alluredir=./allure-results -v
"""
