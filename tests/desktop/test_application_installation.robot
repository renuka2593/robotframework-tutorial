*** Settings ***
Documentation     Test cases demonstrating application installation with PyWinAuto
Resource          ../../resources/install_helpers.resource
Library           OperatingSystem
Suite Setup       Setup Test Environment
Suite Teardown    Cleanup Test Environment

*** Variables ***
# Replace these paths with actual paths for your environment
${TEST_APP_INSTALLER}        C:\\Path\\To\\TestApp.exe
${TEST_APP_MSI_INSTALLER}    C:\\Path\\To\\TestApp.msi
${TEST_APP_NAME}             Test Application
${CUSTOM_INSTALL_PATH}       C:\\Program Files\\Test Application

*** Test Cases ***
Install Application Using EXE Installer
    [Documentation]    Install an application using its EXE installer
    [Tags]    installation    exe    windows
    
    # Skip test if not on Windows
    ${is_windows}=    Evaluate    platform.system() == 'Windows'    platform
    Skip If    not ${is_windows}    This test only runs on Windows
    
    # Skip if installer doesn't exist
    Skip If    not os.path.exists('${TEST_APP_INSTALLER}')    Installer not found at: ${TEST_APP_INSTALLER}
    
    # Install silently
    ${result}=    Install EXE Application    
    ...    exe_path=${TEST_APP_INSTALLER}
    ...    silent=${TRUE}
    ...    timeout=120
    
    # Verify installation
    Should Be True    ${result}    Installation failed
    
    # Verify installation result (e.g., check if an executable exists)
    ${exe_path}=    Join Path    C:\\Program Files    Test Application    TestApp.exe
    File Should Exist    ${exe_path}    Application executable not found after installation

Install Application Using MSI Installer
    [Documentation]    Install an application using its MSI installer
    [Tags]    installation    msi    windows
    
    # Skip test if not on Windows
    ${is_windows}=    Evaluate    platform.system() == 'Windows'    platform
    Skip If    not ${is_windows}    This test only runs on Windows
    
    # Skip if installer doesn't exist
    Skip If    not os.path.exists('${TEST_APP_MSI_INSTALLER}')    Installer not found at: ${TEST_APP_MSI_INSTALLER}
    
    # Install with custom properties
    ${properties}=    Set Variable    INSTALLDIR="${CUSTOM_INSTALL_PATH}" ACCEPT_EULA=1
    ${result}=    Install MSI Application
    ...    msi_path=${TEST_APP_MSI_INSTALLER}
    ...    properties=${properties}
    ...    timeout=120
    
    # Verify installation
    Should Be Equal As Integers    ${result}    0    MSI installation failed with code: ${result}
    
    # Verify installation path
    ${exe_path}=    Join Path    ${CUSTOM_INSTALL_PATH}    TestApp.exe
    File Should Exist    ${exe_path}    Application executable not found after installation

Install Application Interactively
    [Documentation]    Install an application interactively (with UI)
    [Tags]    installation    interactive    windows
    
    # Skip test if not on Windows
    ${is_windows}=    Evaluate    platform.system() == 'Windows'    platform
    Skip If    not ${is_windows}    This test only runs on Windows
    
    # Skip if installer doesn't exist
    Skip If    not os.path.exists('${TEST_APP_INSTALLER}')    Installer not found at: ${TEST_APP_INSTALLER}
    
    # Install interactively
    ${result}=    Install Application With PyWinAuto
    ...    installer_path=${TEST_APP_INSTALLER}
    ...    silent=${FALSE}
    ...    custom_install_path=${CUSTOM_INSTALL_PATH}
    ...    timeout=180
    
    # Verify installation
    Should Be True    ${result}    Interactive installation failed
    
    # Verify installation result
    ${exe_path}=    Join Path    ${CUSTOM_INSTALL_PATH}    TestApp.exe
    File Should Exist    ${exe_path}    Application executable not found after installation

Uninstall Application
    [Documentation]    Uninstall an application
    [Tags]    uninstallation    windows
    
    # Skip test if not on Windows
    ${is_windows}=    Evaluate    platform.system() == 'Windows'    platform
    Skip If    not ${is_windows}    This test only runs on Windows
    
    # Uninstall application
    ${result}=    Uninstall Application With PyWinAuto
    ...    app_name=${TEST_APP_NAME}
    ...    silent=${TRUE}
    ...    timeout=120
    
    # Verify uninstallation
    Should Be True    ${result}    Uninstallation failed
    
    # Verify application is no longer installed
    ${exe_path}=    Join Path    ${CUSTOM_INSTALL_PATH}    TestApp.exe
    File Should Not Exist    ${exe_path}    Application still exists after uninstallation

*** Keywords ***
Setup Test Environment
    [Documentation]    Setup the test environment
    
    # Skip environment setup on non-Windows platforms
    ${is_windows}=    Evaluate    platform.system() == 'Windows'    platform
    Skip If    not ${is_windows}    This test only runs on Windows
    
    # Create dummy installer files for demonstration purposes
    # In real testing, you would use actual installers
    Create Dummy Installer Files

Cleanup Test Environment
    [Documentation]    Clean up the test environment
    
    # Skip cleanup on non-Windows platforms
    ${is_windows}=    Evaluate    platform.system() == 'Windows'    platform
    Return From Keyword If    not ${is_windows}

    # If the test app is still installed, try to uninstall it
    TRY
        Uninstall Application With PyWinAuto    ${TEST_APP_NAME}    silent=${TRUE}
    EXCEPT    AS    ${error}
        Log    Failed to uninstall application: ${error}    WARN
    END
    
    # Remove dummy installer files
    TRY
        Remove File    ${TEST_APP_INSTALLER}
        Remove File    ${TEST_APP_MSI_INSTALLER}
    EXCEPT    AS    ${error}
        Log    Failed to remove dummy files: ${error}    WARN
    END

Create Dummy Installer Files
    [Documentation]    Create dummy installer files for demonstration
    
    # NOTE: This is just for demonstration. In real tests, use actual installers.
    # These dummy files won't actually work with the installation functions.
    
    # Create directory if it doesn't exist
    ${installer_dir}=    Evaluate    os.path.dirname('${TEST_APP_INSTALLER}')    os
    Create Directory    ${installer_dir}
    
    # Create dummy files with minimal content
    Create File    ${TEST_APP_INSTALLER}    # This is a dummy installer file for testing
    Create File    ${TEST_APP_MSI_INSTALLER}    # This is a dummy MSI file for testing
    
    Log    Created dummy installer files for demonstration    INFO
    Log    In real tests, use actual installer files    WARN 