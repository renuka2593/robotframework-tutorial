*** Settings ***
Documentation     Test suite for desktop application (Notepad) testing
Library           WhiteLibrary
Library           OperatingSystem
Library           ../../resources/libraries/DesktopLibrary.py    WITH NAME    DesktopLib
Library           ../../resources/pages/NotepadPage.py    WITH NAME    NotepadPage

Test Setup        Setup Test
Test Teardown     Teardown Test

*** Variables ***
${TEST_TEXT}       Hello, Robot Framework!
${TEST_FILE}       ${EXECDIR}/test_notepad.txt

*** Test Cases ***
Notepad Basic Operations
    [Documentation]    Test basic operations in Notepad
    [Tags]    desktop    notepad    basic
    NotepadPage.Verify Notepad Opened
    NotepadPage.Type Text    ${TEST_TEXT}
    ${text}=    NotepadPage.Get Text
    Should Be Equal    ${text}    ${TEST_TEXT}
    NotepadPage.Take Notepad Screenshot    notepad_text_input

Notepad Save File
    [Documentation]    Test saving a file in Notepad
    [Tags]    desktop    notepad    file
    NotepadPage.Verify Notepad Opened
    NotepadPage.Type Text    ${TEST_TEXT}
    NotepadPage.Save File    ${TEST_FILE}
    File Should Exist    ${TEST_FILE}
    ${file_content}=    Get File    ${TEST_FILE}
    Should Be Equal    ${file_content}    ${TEST_TEXT}
    NotepadPage.Take Notepad Screenshot    notepad_save_file

Notepad Open File
    [Documentation]    Test opening a file in Notepad
    [Tags]    desktop    notepad    file
    # First create a file to open
    Create File    ${TEST_FILE}    ${TEST_TEXT}
    File Should Exist    ${TEST_FILE}
    
    NotepadPage.Verify Notepad Opened
    NotepadPage.Open File    ${TEST_FILE}
    ${text}=    NotepadPage.Get Text
    Should Be Equal    ${text}    ${TEST_TEXT}
    NotepadPage.Take Notepad Screenshot    notepad_open_file

*** Keywords ***
Setup Test
    [Documentation]    Setup for each test case
    NotepadPage.Launch Notepad

Teardown Test
    [Documentation]    Teardown for each test case
    NotepadPage.Close Notepad    save=False
    Run Keyword And Ignore Error    Remove File    ${TEST_FILE} 