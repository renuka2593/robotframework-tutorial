*** Settings ***
Documentation     Browser automation utilities for Robot Framework
Library           Browser
Library           ${CURDIR}/libraries/BrowserUtilities.py
Library           ${CURDIR}/libraries/LoggerLibrary.py
Library           OperatingSystem
Library           DateTime

*** Variables ***
${DEFAULT_TIMEOUT}         30s
${DEFAULT_BROWSER}         chromium
${DEFAULT_HEADLESS}        ${True}

*** Keywords ***
Open Browser And Go To
    [Documentation]     Opens a browser and navigates to the specified URL
    [Arguments]         ${url}    ${browser}=${DEFAULT_BROWSER}    ${headless}=${DEFAULT_HEADLESS}
    New Browser         ${browser}    headless=${headless}
    New Context         acceptDownloads=True
    New Page            ${url}
    
Wait Until Page Contains Element
    [Documentation]     Waits until the page contains an element matching the given selector
    [Arguments]         ${selector}    ${timeout}=${DEFAULT_TIMEOUT}    ${message}=Element not found
    Wait For Elements State    ${selector}    visible    timeout=${timeout}    message=${message}

Wait Until Page Does Not Contain Element
    [Documentation]     Waits until the page does not contain an element matching the given selector
    [Arguments]         ${selector}    ${timeout}=${DEFAULT_TIMEOUT}    ${message}=Element still visible
    Wait For Elements State    ${selector}    detached    timeout=${timeout}    message=${message}

Download File And Verify
    [Documentation]     Downloads a file by clicking a button and verifies it was successful
    [Arguments]         ${button_selector}    ${save_path}=${EMPTY}
    ${download_info}=   Wait For Download From Button    ${button_selector}    ${save_path}
    ${file_path}=       Verify Download Completed    ${download_info}
    File Should Exist   ${file_path}
    [Return]            ${file_path}

Find Element In Form And Fill
    [Documentation]     Finds an input field in a form and fills it with text
    [Arguments]         ${form_selector}    ${input_selector}    ${text}
    Fill Child Input    ${form_selector}    ${input_selector}    ${text}

Submit Form And Wait For Response
    [Documentation]     Submits a form and waits for the response
    [Arguments]         ${form_selector}    ${submit_button_selector}    ${response_url_pattern}
    ${promise}=         Promise To    Wait For Response    ${response_url_pattern}
    Click Child Button  ${form_selector}    button_selector=${submit_button_selector}
    ${response}=        Wait For    ${promise}
    Log Info            Response received with status: ${response}[status]
    [Return]            ${response}

Verify Element Text With Screenshot
    [Documentation]     Verifies element text and captures screenshot on failure
    [Arguments]         ${selector}    ${expected_text}    ${message}=Element text does not match
    ${actual_text}=     Get Text    ${selector}
    Assert Equal        ${actual_text}    ${expected_text}    ${message}

Verify Page Contains Element With Logging
    [Documentation]     Verifies page contains element and logs the result
    [Arguments]         ${selector}    ${timeout}=${DEFAULT_TIMEOUT}
    Log Info            Checking for element: ${selector}
    ${status}=          Run Keyword And Return Status    Wait Until Page Contains Element    ${selector}    ${timeout}
    Run Keyword If      '${status}'=='False'    Capture And Embed Screenshot    element_not_found
    [Return]            ${status}

Complete Form Fields
    [Documentation]     Fills multiple fields in a form
    [Arguments]         ${form_selector}    ${field_data}
    FOR    ${field}    IN    @{field_data}
        Fill Child Input    ${form_selector}    ${field}[selector]    ${field}[value]
    END 