*** Settings ***
Documentation     Test suite for login functionality
Library           SeleniumLibrary
Library           ../../resources/libraries/BrowserLibrary.py    WITH NAME    BrowserLib
Library           ../../resources/libraries/LocatorLibrary.py    WITH NAME    LocatorLib
Resource          ../../resources/keywords/common.robot
Resource          ../../resources/variables/common.robot
Library           ../../resources/pages/LoginPage.py    WITH NAME    LoginPage

Test Setup        Setup Test
Test Teardown     Teardown Test

*** Variables ***
${VALID_USERNAME}       standard_user
${VALID_PASSWORD}       secret_sauce
${INVALID_USERNAME}     invalid_user
${INVALID_PASSWORD}     wrong_password
${LOCKED_USER}          locked_out_user

*** Test Cases ***
Valid Login
    [Documentation]    Test login with valid credentials
    [Tags]    login    smoke    positive
    LoginPage.Verify Page Loaded
    LoginPage.Login    ${VALID_USERNAME}    ${VALID_PASSWORD}
    Wait Until Page Contains Element    css:.inventory_container
    Page Should Contain Element    css:.inventory_list

Invalid Login
    [Documentation]    Test login with invalid credentials
    [Tags]    login    negative
    LoginPage.Verify Page Loaded
    LoginPage.Login Should Fail With Message    ${INVALID_USERNAME}    ${INVALID_PASSWORD}    Username and password do not match

Locked User Login
    [Documentation]    Test login with a locked out user
    [Tags]    login    negative
    LoginPage.Verify Page Loaded
    LoginPage.Login Should Fail With Message    ${LOCKED_USER}    ${VALID_PASSWORD}    Sorry, this user has been locked out

Login Page Title
    [Documentation]    Verify the login page title
    [Tags]    login    smoke
    LoginPage.Verify Page Loaded
    LoginPage.Verify Login Page Title    Swag Labs

*** Keywords ***
Setup Test
    [Documentation]    Setup for each test case
    BrowserLib.Init Browser    url=${DEMO_APP_URL}
    LoginPage.Verify Page Loaded

Teardown Test
    [Documentation]    Teardown for each test case
    Take Timestamped Screenshot    login_test
    Close All Browsers 