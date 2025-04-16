*** Settings ***
Documentation     Simple demo test for EnvLibrary - .env file handling
Library           ../libraries/EnvLibrary.py
Library           BuiltIn

*** Test Cases ***
Verify EnvLibrary Basic Usage
    [Documentation]    Test basic functionality of EnvLibrary
    [Tags]    env    demo
    
    # Load the default .env file
    ${result}=    Load Env File
    Should Be True    ${result}
    
    # Get an environment variable value
    ${browser}=    Get Env    BROWSER
    Log    Current browser setting: ${browser}
    Should Not Be Empty    ${browser}
    
    # Get an environment variable with a default value
    ${unknown_var}=    Get Env    UNKNOWN_VARIABLE    default_value
    Should Be Equal    ${unknown_var}    default_value
    
    # Get all environment variables from .env file
    ${all_envs}=    Get All Envs
    Log    All environment variables:
    FOR    ${key}    IN    @{all_envs}
        Log    ${key}=${all_envs}[${key}]
    END

Demonstrate Persistent Environment Changes
    [Documentation]    Demo how to persist changes to .env file
    [Tags]    env    demo    persist
    
    # NOTE: This test is commented out to prevent actual changes to your .env file
    # Uncomment and modify it if you want to test the persistence functionality
    
    # Load the .env file
    # ${result}=    Load Dotenv File
    
    # Get the original value
    # ${original_value}=    Get Env    BROWSER
    
    # Set a new value and persist it to the .env file
    # Set Env    TEST_TEMP_VAR    temp_persistent_value    persist=True
    
    # Reload to verify
    # Reload Dotenv
    # ${value}=    Get Env    TEST_TEMP_VAR
    # Should Be Equal    ${value}    temp_persistent_value
    
    # Clean up (remove the variable from .env)
    # Unset Env    TEST_TEMP_VAR    persist=True 