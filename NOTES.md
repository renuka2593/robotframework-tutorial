# Robot Framework Best Practices and Guidelines

## Directory Structure

```
project_root/
├── resources/
│   ├── libraries/         # Custom Python libraries
│   ├── keywords/         # Reusable keywords
│   ├── locators/        # Element locators
│   ├── variables/       # Test variables
│   └── config/         # Configuration files
├── tests/
│   ├── acceptance/    # End-to-end tests
│   ├── integration/  # Integration tests
│   └── unit/        # Unit tests
├── results/        # Test execution results
└── docs/         # Documentation
```

## Naming Conventions

### Test Cases

- Use descriptive names that explain the test purpose
- Follow Given-When-Then format

```robot
Test Case Name Should Describe Expected Behavior
    Given precondition is set
    When action is performed
    Then expected outcome is verified
```

### Keywords

- Use verb-noun format
- Be specific and descriptive

```robot
Open Login Page
Verify Dashboard Is Visible
Enter User Credentials    ${username}    ${password}
```

### Variables

- UPPER_CASE for global variables
- lower_case for local variables
- Use descriptive names

```robot
${GLOBAL_TIMEOUT}=    30s
${DEFAULT_BROWSER}=    chrome
${user_input}=    Get User Input
```

## Best Practices

### 1. Test Organization

- One test case per file for complex scenarios
- Group related tests in suites
- Use tags for test categorization

```robot
*** Settings ***
Force Tags        regression    login
Default Tags     smoke

*** Test Cases ***
Valid Login
    [Tags]    critical    authentication
```

### 2. Locator Management

- Keep locators in separate resource files
- Use meaningful IDs in application
- Prefer ID > name > CSS > XPath

```robot
*** Variables ***
${LOGIN_BUTTON}    id=loginBtn
${USERNAME_FIELD}    css=[data-test="username-input"]
```

### 3. Test Data Management

- Externalize test data
- Use variables files
- Avoid hardcoding test data

```robot
*** Settings ***
Variables    test_data.py
Resource    common_variables.resource
```

### 4. Error Handling

- Use try-except blocks in custom libraries
- Set proper timeouts
- Handle expected errors gracefully

```robot
*** Keywords ***
Handle Expected Error
    [Arguments]    ${expected_error}
    Run Keyword And Expect Error    ${expected_error}    Keyword That May Fail
```

### 5. Logging and Screenshots

- Use appropriate log levels
- Capture screenshots on failures
- Add descriptive messages

```robot
*** Keywords ***
Log Test Step
    [Arguments]    ${message}
    Log    ${message}    level=INFO
    Capture Page Screenshot    filename=step_{index}.png
```

## Common Patterns

### Page Object Pattern

```robot
*** Settings ***
Resource    ../resources/locators/login_page.resource

*** Keywords ***
Login Page Should Be Open
    Wait Until Element Is Visible    ${LOGIN_PAGE_HEADING}

Enter Credentials
    [Arguments]    ${username}    ${password}
    Input Text    ${USERNAME_FIELD}    ${username}
    Input Password    ${PASSWORD_FIELD}    ${password}
```

### Data-Driven Testing

```robot
*** Settings ***
Test Template    Login With Invalid Credentials

*** Test Cases ***    Username    Password    Error Message
Empty Username        ${EMPTY}    valid       Username is required
Empty Password       valid       ${EMPTY}    Password is required
Invalid Both         invalid     invalid     Invalid credentials
```

## Performance Considerations

- Use appropriate wait conditions
- Avoid sleep keywords
- Optimize test execution time

```robot
*** Keywords ***
Wait For Element With Timeout
    [Arguments]    ${locator}    ${timeout}=10s
    Wait Until Element Is Visible    ${locator}    timeout=${timeout}
```

## Security Guidelines

- Never commit sensitive data
- Use environment variables for credentials
- Implement proper access controls

```robot
*** Variables ***
${USERNAME}    %{TEST_USER}
${PASSWORD}    %{TEST_PASSWORD}
```

## Continuous Integration

- Set up proper test environments
- Configure parallel execution
- Implement proper reporting

```bash
robot --outputdir results
      --listener allure_robotframework
      --variable BROWSER:headlesschrome
      tests/
```

## Debugging Tips

1. Use `Log To Console` for immediate feedback
2. Set log level to DEBUG for detailed information
3. Use tags to run specific tests
4. Implement custom listeners for advanced debugging

## Common Issues and Solutions

1. Element not found

   - Implement proper wait conditions
   - Check element locators
   - Verify page load completion

2. Test flakiness

   - Add proper waits
   - Improve locators
   - Check for race conditions

3. Performance issues
   - Optimize test setup/teardown
   - Use proper wait conditions
   - Implement parallel execution

## Additional Resources

- [Robot Framework User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [Browser Library Documentation](https://marketsquare.github.io/robotframework-browser/Browser.html)
- [SeleniumLibrary Documentation](https://robotframework.org/SeleniumLibrary/SeleniumLibrary.html)
