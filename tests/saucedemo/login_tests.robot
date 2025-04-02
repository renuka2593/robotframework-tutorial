*** Settings ***
Documentation     Login tests for SauceDemo using Browser library
Resource          ../../resources/keywords/saucedemo_keywords.robot
Resource          ../../resources/variables/saucedemo_variables.robot

Test Setup        Setup SauceDemo Test
Test Teardown     Teardown SauceDemo Test

*** Test Cases ***
Valid Login With Standard User
    [Documentation]    Test login with standard user
    [Tags]            login    smoke    positive
    Login As Standard User
    # Validate successful login by checking for products
    ProductsPage.Get Product Count
    ProductsPage.Element Should Contain Text    css=.title    Products

Valid Login With Performance Glitch User
    [Documentation]    Test login with performance glitch user
    [Tags]            login    performance    positive
    LoginPage.Login As User    ${PERF_GLITCH_USER}
    # Note: With a performance glitch user, we might need a longer timeout
    ProductsPage.Verify Products Page Loaded

Invalid Login With Locked Out User
    [Documentation]    Test login with locked out user (should fail)
    [Tags]            login    negative
    LoginPage.Login As User    ${LOCKED_USER}
    # Verify error message
    Verify Login Failed With Error    ${ERROR_MSG_LOCKED_USER}

Invalid Login With Wrong Password
    [Documentation]    Test login with wrong password
    [Tags]            login    negative
    Login With Custom Credentials    standard_user    wrong_password
    # Verify generic error message
    Verify Login Failed With Error    Username and password do not match

Login With Different Browsers
    [Documentation]    Parametrized test for login with different browsers
    [Tags]            login    cross-browser
    [Template]        Login With Browser
    chromium
    firefox
    webkit

*** Keywords ***
Login With Browser
    [Documentation]    Login with a specific browser
    [Arguments]    ${browser_name}
    
    # Close the current browser if open
    Try To Close Browser
    
    # Setup a new browser with specified type
    Setup SauceDemo Test    browser=${browser_name}
    
    # Login and verify
    Login As Standard User
    ProductsPage.Get Product Count
    Take Screenshot    filename=login-${browser_name}
    
    # Cleanup
    ProductsPage.Logout
    LoginPage.Verify Login Page Loaded

Try To Close Browser
    [Documentation]    Try to close browser if open
    ${status}=    Run Keyword And Return Status    Browser Is Open
    Run Keyword If    ${status}    Close Browser

Browser Is Open
    [Documentation]    Check if browser is open
    ${context_count}=    Get Context Count
    ${result}=    Evaluate    ${context_count} > 0
    Return From Keyword    ${result}

Get Context Count
    [Documentation]    Get the number of contexts
    ${contexts}=    Get Browser Contexts
    ${count}=    Get Length    ${contexts}
    Return From Keyword    ${count} 