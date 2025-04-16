*** Settings ***
Documentation    Example test case demonstrating the use of URL and data configuration
Resource         ../resources/variables/config.robot
Library          ../libraries/LoggerLibrary.py

*** Variables ***
${PRODUCT_KEY}    product1

*** Test Cases ***
Example Login Test
    [Documentation]    Example test demonstrating login with configured credentials
    Initialize Configuration
    ${user}=           Get User Data    standard_user
    ${base_url}=       Set Variable     ${BASE_URL}
    ${login_url}=      Set Variable     ${BASE_URL}${LOGIN_ENDPOINT}
    
    Log    Opening URL: ${login_url}
    Log    Logging in as: ${user}[username]
    
    # Simulated test steps - in a real test you would use Browser or other libraries
    # to interact with the application
    Log    Entering username: ${user}[username]
    Log    Entering password: ${user}[password]
    Log    Clicking login button
    
    # Use the Logger Library to capture a screenshot
    Capture And Embed Screenshot    login_screen
    
    # Use assertion from Logger Library
    Assert True    ${True}    Login should be successful

Example Product Test
    [Documentation]    Example test demonstrating the use of product data
    Initialize Configuration
    ${product}=        Get Product    ${PRODUCT_KEY}
    ${base_url}=       Set Variable   ${BASE_URL}
    ${product_url}=    Set Variable   ${BASE_URL}${PRODUCTS_ENDPOINT}/${product}[id]
    
    Log    Opening URL: ${product_url}
    Log    Viewing product: ${product}[name]
    
    # Simulated verification - in a real test you would verify actual UI or API data
    ${product_price}=    Set Variable    ${product}[price]
    ${expected_price}=   Set Variable    29.99
    
    # Use assertion from Logger Library
    Assert Equal    ${product_price}    ${expected_price}    Product price should be correct
    Capture And Embed Screenshot    product_view

Example API Test
    [Documentation]    Example test demonstrating API data usage
    Initialize Configuration
    ${api_data}=       Get API Data    valid_order
    ${api_url}=        Set Variable    ${API_URL}/orders
    
    Log    Sending POST request to: ${api_url}
    Log    With order data: ${api_data}
    
    # Simulated API test - in a real test you would use requests or other API libraries
    Log    Verifying order has customer ID: ${api_data}[customer_id]
    Log    Verifying order has ${api_data}[items][0][quantity] items of product ${api_data}[items][0][product_id]
    
    # Use assertion and logging from Logger Library
    Assert Contains    ${api_data}[payment_method]    credit    Payment method should be credit-based
    Assert Equal      ${api_data}[shipping_address][city]    Test City    Shipping city should be Test City
    Log Info    API Test completed successfully 