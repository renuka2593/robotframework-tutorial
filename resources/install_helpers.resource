*** Settings ***
Documentation     Robot Framework keywords for handling Windows application installations
Library           ${CURDIR}/../utils/installation_helpers.py
Library           OperatingSystem
Library           Collections

*** Variables ***
${DEFAULT_TIMEOUT}    60
${DEFAULT_INSTALL_PATH}    ${EMPTY}

*** Keywords ***
Install Application With PyWinAuto
    [Documentation]    Install a Windows application using PyWinAuto
    [Arguments]    ${installer_path}    ${silent}=${FALSE}    ${silent_args}=${NONE}    ${custom_install_path}=${DEFAULT_INSTALL_PATH}    ${timeout}=${DEFAULT_TIMEOUT}    ${handle_reboot}=${FALSE}
    
    # Validate installer path
    File Should Exist    ${installer_path}    Installer file does not exist: ${installer_path}
    
    # Convert boolean arguments to Python booleans
    ${silent_python}=    Convert To Boolean    ${silent}
    ${handle_reboot_python}=    Convert To Boolean    ${handle_reboot}
    
    # Call the Python function
    ${result}=    Install Application Pywinauto    ${installer_path}    ${silent_python}    ${silent_args}    ${custom_install_path}    ${timeout}    ${handle_reboot_python}
    [Return]    ${result}

Uninstall Application With PyWinAuto
    [Documentation]    Uninstall a Windows application using PyWinAuto
    [Arguments]    ${app_name}    ${uninstaller_path}=${NONE}    ${silent}=${FALSE}    ${timeout}=${DEFAULT_TIMEOUT}
    
    # Convert boolean arguments to Python booleans
    ${silent_python}=    Convert To Boolean    ${silent}
    
    # Call the Python function
    ${result}=    Uninstall Application Pywinauto    ${app_name}    ${uninstaller_path}    ${silent_python}    ${timeout}
    [Return]    ${result}

Run Silent Installation With PyWinAuto
    [Documentation]    Run a silent installation using PyWinAuto
    [Arguments]    ${installer_path}    ${silent_args}=${NONE}    ${timeout}=${DEFAULT_TIMEOUT}
    
    # Validate installer path
    File Should Exist    ${installer_path}    Installer file does not exist: ${installer_path}
    
    # Call the Python function
    ${result}=    Run Silent Installation Pywinauto    ${installer_path}    ${silent_args}    ${timeout}
    [Return]    ${result}

Install MSI Application
    [Documentation]    Install an MSI application silently
    [Arguments]    ${msi_path}    ${properties}=${EMPTY}    ${timeout}=${DEFAULT_TIMEOUT}
    
    # Validate MSI path
    File Should Exist    ${msi_path}    MSI file does not exist: ${msi_path}
    
    # Build silent arguments
    ${silent_args}=    Set Variable    /quiet /norestart
    
    # Add custom properties if provided
    IF    $properties != $EMPTY
        ${silent_args}=    Set Variable    ${silent_args} ${properties}
    END
    
    # Call the silent installation function
    ${result}=    Run Silent Installation Pywinauto    ${msi_path}    ${silent_args}    ${timeout}
    [Return]    ${result}

Install EXE Application
    [Documentation]    Install an EXE application
    [Arguments]    ${exe_path}    ${silent}=${TRUE}    ${silent_args}=${NONE}    ${custom_install_path}=${DEFAULT_INSTALL_PATH}    ${timeout}=${DEFAULT_TIMEOUT}
    
    # Validate EXE path
    File Should Exist    ${exe_path}    EXE file does not exist: ${exe_path}
    
    # Convert boolean arguments to Python booleans
    ${silent_python}=    Convert To Boolean    ${silent}
    
    # Default silent args for common installers if not provided and installation is silent
    IF    $silent_python == $TRUE and $silent_args == $NONE
        ${installer_type}=    Get Installer Type    ${exe_path}
        IF    '${installer_type}' == 'exe'
            ${silent_args}=    Set Variable    /S    # NSIS installers
        END
    END
    
    # Call the installation function
    ${result}=    Install Application Pywinauto    ${exe_path}    ${silent_python}    ${silent_args}    ${custom_install_path}    ${timeout}
    [Return]    ${result}

Check If Process Is Running
    [Documentation]    Check if a process is running by name
    [Arguments]    ${process_name}
    ${result}=    Is Process Running    ${process_name}
    [Return]    ${result}

Wait For Window To Appear
    [Documentation]    Wait for a window to appear based on title regex
    [Arguments]    ${title_regex}    ${timeout}=${DEFAULT_TIMEOUT}
    ${window}=    Wait For Window    ${title_regex}    ${timeout}
    [Return]    ${window}

Install Application With FlaUI
    [Documentation]    Install an application using FlaUI (placeholder - requires implementation)
    [Arguments]    ${installer_path}    ${silent}=${FALSE}    ${silent_args}=${NONE}    ${custom_install_path}=${DEFAULT_INSTALL_PATH}    ${timeout}=${DEFAULT_TIMEOUT}
    
    # Validate installer path
    File Should Exist    ${installer_path}    Installer file does not exist: ${installer_path}
    
    # Convert boolean arguments
    ${silent_python}=    Convert To Boolean    ${silent}
    
    # Log warning that this is not implemented yet
    Log    FlaUI implementation is not available. This keyword is a placeholder.    WARN
    
    # This will raise NotImplementedError until implemented
    TRY
        ${result}=    Install Application Flaui    ${installer_path}    ${silent_python}    ${silent_args}    ${custom_install_path}    ${timeout}
        [Return]    ${result}
    EXCEPT    NotImplementedError    AS    ${error}
        Log    ${error}    ERROR
        Fail    FlaUI implementation is not available. Please implement it first.
    END

Uninstall Application With FlaUI
    [Documentation]    Uninstall an application using FlaUI (placeholder - requires implementation)
    [Arguments]    ${app_name}    ${uninstaller_path}=${NONE}    ${silent}=${FALSE}    ${timeout}=${DEFAULT_TIMEOUT}
    
    # Convert boolean arguments
    ${silent_python}=    Convert To Boolean    ${silent}
    
    # Log warning that this is not implemented yet
    Log    FlaUI implementation is not available. This keyword is a placeholder.    WARN
    
    # This will raise NotImplementedError until implemented
    TRY
        ${result}=    Uninstall Application Flaui    ${app_name}    ${uninstaller_path}    ${silent_python}    ${timeout}
        [Return]    ${result}
    EXCEPT    NotImplementedError    AS    ${error}
        Log    ${error}    ERROR
        Fail    FlaUI implementation is not available. Please implement it first.
    END 