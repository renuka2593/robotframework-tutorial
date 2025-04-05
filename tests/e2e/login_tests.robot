*** Settings ***
Documentation     End-to-end tests for the login functionality
Resource          ../../resources/keywords/login_page.resource
Resource          ../../resources/keywords/inventory_page.resource

Suite Setup       Open Login Page
Suite Teardown    Close Browser    ALL

Force Tags        login    e2e

*** Test Cases ***
Valid Login With Standard User
    [Documentation]    Verify that a standard user can log in successfully
    [Tags]    smoke    critical
    Login As User Type    standard
    Verify Inventory Page Loaded

Login With Locked Out User Should Fail
    [Documentation]    Verify that a locked out user cannot log in
    [Tags]    negative
    Login As User Type    locked
    Verify Error Message    Epic sadface: Sorry, this user has been locked out.

Login With Invalid Credentials Should Fail
    [Documentation]    Verify that invalid credentials are rejected
    [Tags]    negative
    Login With Credentials    invalid_user    invalid_pass
    Verify Error Message    Epic sadface: Username and password do not match any user in this service

Successful Logout
    [Documentation]    Verify that a user can successfully log out
    [Tags]    smoke
    Login As User Type    standard
    Verify Inventory Page Loaded
    Logout
    Wait For Elements State    ${LOGIN_USERNAME_FIELD}    visible 