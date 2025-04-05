*** Settings ***
Documentation     Keywords for interacting with the login page
Resource         ../locators/login_page.resource
Library          Browser
Library          ../../libraries/Config.py
Library          ../../libraries/LoggerLibrary.py

*** Keywords ***
Open Login Page
    [Documentation]    Opens the login page and verifies it's loaded
    ${config}=    Get Browser Config
    ${url}=       Get Base URL
    New Browser    ${config}[browser]    headless=${config}[headless]
    New Context    viewport={'width': 1920, 'height': 1080}
    New Page      ${url}
    Wait For Elements State    ${LOGIN_LOGO}    visible
    Log Info    Login page opened successfully

Login With Credentials
    [Documentation]    Logs in with the specified credentials
    [Arguments]    ${username}    ${password}
    Fill Text    ${LOGIN_USERNAME_FIELD}    ${username}
    Fill Text    ${LOGIN_PASSWORD_FIELD}    ${password}
    Click        ${LOGIN_BUTTON}

Login As User Type
    [Documentation]    Logs in as a specific user type
    [Arguments]    ${user_type}=standard
    ${credentials}=    Get User Credentials    ${user_type}
    Login With Credentials    ${credentials}[username]    ${credentials}[password]

Verify Error Message
    [Documentation]    Verifies that an error message is displayed
    [Arguments]    ${expected_message}
    ${error_text}=    Get Text    ${ERROR_MESSAGE}
    Assert Equal    ${error_text}    ${expected_message}    Error message does not match
    Capture And Embed Screenshot    error_message 