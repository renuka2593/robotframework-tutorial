*** Settings ***
Documentation     Common variables used across all test suites
Library           OperatingSystem

*** Variables ***
${BROWSER}        %{BROWSER=chrome}
${HEADLESS}       %{HEADLESS=False}
${DEFAULT_TIMEOUT}    %{DEFAULT_TIMEOUT=10}
${IMPLICIT_WAIT}      %{IMPLICIT_WAIT=5}
${SCREENSHOT_ON_FAILURE}    %{SCREENSHOT_ON_FAILURE=True}

# URLs
${WEB_URL}        %{WEB_URL=https://www.example.com}
${DEMO_APP_URL}   %{DEMO_APP_URL=https://www.saucedemo.com}

# Credentials
${TEST_USERNAME}  %{TEST_USERNAME=standard_user}
${TEST_PASSWORD}  %{TEST_PASSWORD=secret_sauce}

# Directories
${TEST_DATA_DIR}  ${EXECDIR}/resources/test_data
${DOWNLOAD_DIR}   ${EXECDIR}/downloads 