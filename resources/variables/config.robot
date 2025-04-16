*** Settings ***
Documentation     Common configuration for test suites
Library           String
Library           Collections
Library           OperatingSystem
Resource          ../../resources/keywords/common.robot
Library           ../../resources/variables/yaml_reader.py    WITH NAME    YamlReader
Variables         urls.py    dev

*** Variables ***
# Default test configuration
${BROWSER}              chrome
${HEADLESS}             ${True}
${TIMEOUT}              30
${RETRY_ATTEMPTS}       3

# Default credentials - can be overridden
${DEFAULT_USERNAME}     standard_user
${DEFAULT_PASSWORD}     secret_sauce

# Common paths and directories
${TEST_DATA_DIR}        ${CURDIR}${/}..${/}..${/}test_data
${DOWNLOADS_DIR}        ${EXECDIR}${/}downloads
${REPORTS_DIR}          ${EXECDIR}${/}reports

*** Keywords ***
Initialize Configuration
    [Documentation]     Initialize the test configuration
    ${env_settings}=    YamlReader.Get Environment Settings
    Set Test Variable   ${BROWSER}    ${env_settings}[browser]
    Set Test Variable   ${HEADLESS}    ${env_settings}[headless]
    Set Test Variable   ${TIMEOUT}    ${env_settings}[timeout]
    Set Test Variable   ${RETRY_ATTEMPTS}    ${env_settings}[retry_attempts]
    
    ${std_user}=        YamlReader.Get User Credentials    standard_user
    Set Test Variable   ${DEFAULT_USERNAME}    ${std_user}[username]
    Set Test Variable   ${DEFAULT_PASSWORD}    ${std_user}[password]
    
    Log    Initializing test with browser: ${BROWSER}
    Log    Using headless mode: ${HEADLESS}
    Create Directory    ${DOWNLOADS_DIR}
    Create Directory    ${REPORTS_DIR}

Get Dictionary From YAML
    [Documentation]     Get a dictionary from the YAML data
    [Arguments]         ${key}
    ${data}=            YamlReader.Get Test Data
    ${dict}=            Get From Dictionary    ${data}    ${key}
    [Return]            ${dict}

Get User Data
    [Documentation]     Get user data from the YAML data
    [Arguments]         ${user_key}=standard_user
    ${user}=            YamlReader.Get User Credentials    ${user_key}
    [Return]            ${user}

Get Product
    [Documentation]     Get product data from the YAML data
    [Arguments]         ${product_key}=product1
    ${product}=         YamlReader.Get Product Data    ${product_key}
    [Return]            ${product}

Get API Data
    [Documentation]     Get API test data from the YAML data
    [Arguments]         ${key}=valid_order
    ${api_data}=        YamlReader.Get Api Test Data    ${key}
    [Return]            ${api_data}

Get Current Environment
    [Documentation]     Get the current environment settings
    ${env}=             Get Environment Settings
    RETURN              ${env} 