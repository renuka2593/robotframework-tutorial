*** Settings ***
Documentation     Common keywords for Robot Framework UI tests
Library           SeleniumLibrary
Library           OperatingSystem
Library           DateTime
Library           ../libraries/BrowserLibrary.py
Library           ../libraries/LocatorLibrary.py
Resource          ../variables/common.robot

*** Keywords ***
Setup Browser
    [Documentation]    Setup the browser for testing
    [Arguments]    ${url}=${WEB_URL}    ${browser}=${BROWSER}    ${headless}=${HEADLESS}
    ${selenium}=    Init Browser    url=${url}    browser=${browser}    headless=${headless}
    Set Screenshot Directory    ${EXECDIR}/reports
    [Return]    ${selenium}

Teardown Browser
    [Documentation]    Teardown the browser after testing
    Close All Browsers

Take Timestamped Screenshot
    [Documentation]    Take a screenshot with a timestamp
    [Arguments]    ${name}=screenshot
    ${timestamp}=    Get Current Date    result_format=%Y%m%d-%H%M%S
    ${filename}=    Set Variable    ${name}_${timestamp}
    Capture Page Screenshot    ${filename}.png
    [Return]    ${filename}.png

Wait And Click
    [Documentation]    Wait for an element and click it
    [Arguments]    ${locator}    ${timeout}=${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    Wait Until Element Is Enabled    ${locator}    timeout=${timeout}
    Click Element    ${locator}

Wait And Input
    [Documentation]    Wait for an element and input text
    [Arguments]    ${locator}    ${text}    ${timeout}=${DEFAULT_TIMEOUT}    ${clear}=True
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    Run Keyword If    ${clear}    Clear Element Text    ${locator}
    Input Text    ${locator}    ${text}

Element Should Contain Text
    [Documentation]    Verify that an element contains the expected text
    [Arguments]    ${locator}    ${expected_text}    ${timeout}=${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    ${actual_text}=    Get Text    ${locator}
    Should Contain    ${actual_text}    ${expected_text}

Element Should Have Exact Text
    [Documentation]    Verify that an element has the exact expected text
    [Arguments]    ${locator}    ${expected_text}    ${timeout}=${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    ${actual_text}=    Get Text    ${locator}
    Should Be Equal    ${actual_text}    ${expected_text}

Wait For Page To Load
    [Documentation]    Wait for a page to load completely
    [Arguments]    ${timeout}=${DEFAULT_TIMEOUT}
    Wait For Condition    return document.readyState == "complete"    timeout=${timeout}

Create Dynamic XPath
    [Documentation]    Create a dynamic XPath locator
    [Arguments]    ${base_xpath}    &{kwargs}
    ${locator}=    Create XPath Locator    ${base_xpath}    &{kwargs}
    [Return]    ${locator}

Create Dynamic CSS
    [Documentation]    Create a dynamic CSS locator
    [Arguments]    ${base_css}    &{kwargs}
    ${locator}=    Create CSS Locator    ${base_css}    &{kwargs}
    [Return]    ${locator}

Verify Element Count
    [Documentation]    Verify the count of elements matching a locator
    [Arguments]    ${locator}    ${expected_count}    ${timeout}=${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    ${count}=    Get Element Count    ${locator}
    Should Be Equal As Integers    ${count}    ${expected_count}
    [Return]    ${count}

Get Element Attribute Value
    [Documentation]    Get the value of an element's attribute
    [Arguments]    ${locator}    ${attribute}    ${timeout}=${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    ${value}=    Get Element Attribute    ${locator}    ${attribute}
    [Return]    ${value}

Scroll Element Into View
    [Documentation]    Scroll an element into view
    [Arguments]    ${locator}    ${timeout}=${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
    Execute JavaScript    arguments[0].scrollIntoView(true);    ARGUMENTS    ${locator}

Get Current Timestamp
    [Documentation]    Get current timestamp in the specified format
    [Arguments]    ${format}=%Y%m%d-%H%M%S
    ${timestamp}=    Get Current Date    result_format=${format}
    [Return]    ${timestamp}

Get Random String
    [Documentation]    Generate a random string with the specified length
    [Arguments]    ${length}=10    ${chars}=[LETTERS][NUMBERS]
    ${random_string}=    Generate Random String    ${length}    ${chars}
    [Return]    ${random_string} 