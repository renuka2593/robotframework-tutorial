*** Settings ***
Documentation     Browser Library Test suite for login functionality
Library           Browser
Resource          ../../resources/variables/common.robot
Library           ../../resources/pages/BrowserLoginPage.py    WITH NAME    BrowserLoginPage

Test Setup        Setup Browser Test
Test Teardown     Teardown Browser Test

*** Variables ***
${VALID_USERNAME}       standard_user
${VALID_PASSWORD}       secret_sauce
${INVALID_USERNAME}     invalid_user
${INVALID_PASSWORD}     wrong_password
${LOCKED_USER}          locked_out_user

*** Test Cases ***
Valid Login With Browser Library
    [Documentation]    Test login with valid credentials using Browser Library
    [Tags]    browser    login    smoke    positive
    BrowserLoginPage.Verify Page Loaded
    BrowserLoginPage.Login    ${VALID_USERNAME}    ${VALID_PASSWORD}
    BrowserLoginPage.Verify Successful Login
    ${count}=    BrowserLoginPage.Get Inventory Item Count
    Should Be True    ${count} > 3

Invalid Login With Browser Library
    [Documentation]    Test login with invalid credentials using Browser Library
    [Tags]    browser    login    negative
    BrowserLoginPage.Verify Page Loaded
    BrowserLoginPage.Login Should Fail With Message    ${INVALID_USERNAME}    ${INVALID_PASSWORD}    Username and password do not match

Locked User Login With Browser Library
    [Documentation]    Test login with a locked out user using Browser Library
    [Tags]    browser    login    negative
    BrowserLoginPage.Verify Page Loaded
    BrowserLoginPage.Login Should Fail With Message    ${LOCKED_USER}    ${VALID_PASSWORD}    Sorry, this user has been locked out

Visual Validation With Browser Library
    [Documentation]    Test visual validation capabilities with Browser Library
    [Tags]    browser    visual    login
    BrowserLoginPage.Verify Page Loaded
    BrowserLoginPage.Take Element Screenshot    css=.login_logo    ${EXECDIR}/reports/logo.png
    Take Screenshot    selector=css=.login_wrapper    filename=${EXECDIR}/reports/login-form.png
    
Advanced Browser Library Features
    [Documentation]    Test advanced Browser Library features
    [Tags]    browser    advanced    login
    BrowserLoginPage.Verify Page Loaded
    
    # Parallel execution
    ${parallel_results}=    Run Keywords
    ...    Type Text    id=user-name    ${VALID_USERNAME}    AND
    ...    Type Secret    id=password    ${VALID_PASSWORD}
    
    # Take video recording
    Start Video Recording    filename=${EXECDIR}/reports/login-recording
    BrowserLoginPage.Login    ${VALID_USERNAME}    ${VALID_PASSWORD}
    BrowserLoginPage.Verify Successful Login
    Stop Video Recording
    
    # Check browser console logs
    ${logs}=    Get Browser Console Log Level    ALL
    Log    ${logs}

*** Keywords ***
Setup Browser Test
    [Documentation]    Setup for Browser Library tests
    New Browser    browser=${BROWSER}    headless=${HEADLESS}
    New Context    viewport={'width': 1920, 'height': 1080}
    New Page    ${DEMO_APP_URL}
    Wait For Elements State    css=.login_logo    visible

Teardown Browser Test
    [Documentation]    Teardown for Browser Library tests
    Take Screenshot
    Close Browser 