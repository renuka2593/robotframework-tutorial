*** Settings ***
Documentation     Performance tests for SauceDemo using Browser library
Resource          ../../resources/keywords/saucedemo_keywords.robot
Resource          ../../resources/variables/saucedemo_variables.robot
Library           DateTime

Test Setup        Setup SauceDemo Test
Test Teardown     Teardown SauceDemo Test

*** Test Cases ***
Compare Performance Between Standard And Glitch Users
    [Documentation]    Compare login performance between standard and glitch users
    [Tags]            performance    login
    
    # First measure standard user
    ${standard_time}=    Measure Login Time    ${STANDARD_USER}
    
    # Then measure performance glitch user
    ${glitch_time}=    Measure Login Time    ${PERF_GLITCH_USER}
    
    # Log the results
    Log    Standard user login time: ${standard_time}s
    Log    Performance glitch user login time: ${glitch_time}s
    
    # Verify performance glitch user is slower
    Should Be True    ${glitch_time} > ${standard_time}    Performance glitch user should be slower

Verify Page Load Times For Different Products
    [Documentation]    Measure load times for different product pages
    [Tags]            performance    products
    
    # Login first
    Login As Standard User
    
    # List of products to test
    @{products}=    Create List    Sauce Labs Backpack    Sauce Labs Bike Light    Sauce Labs Bolt T-Shirt
    
    # Measure load time for each product
    FOR    ${product}    IN    @{products}
        ${load_time}=    Measure Product Page Load Time    ${product}
        Log    Load time for ${product}: ${load_time}s
        # Verify load time is within acceptable limits
        Should Be True    ${load_time} < 5    Load time for ${product} is too slow: ${load_time}s
    END

Measure Product Sort Performance
    [Documentation]    Measure time to sort products
    [Tags]            performance    products    sorting
    
    # Login first
    Login As Standard User
    
    # Measure sorting times
    ${az_time}=    Measure Sorting Time    az
    ${za_time}=    Measure Sorting Time    za
    ${lohi_time}=    Measure Sorting Time    lohi
    ${hilo_time}=    Measure Sorting Time    hilo
    
    # Log the results
    Log    Time to sort A-Z: ${az_time}s
    Log    Time to sort Z-A: ${za_time}s
    Log    Time to sort price low-high: ${lohi_time}s
    Log    Time to sort price high-low: ${hilo_time}s
    
    # Verify all sorting times are acceptable
    FOR    ${time}    IN    ${az_time}    ${za_time}    ${lohi_time}    ${hilo_time}
        Should Be True    ${time} < 3    Sorting time too slow: ${time}s
    END

*** Keywords ***
Measure Login Time
    [Documentation]    Measure time to login with specified user
    [Arguments]    ${user_dict}
    
    # Reload the page to ensure fresh start
    New Page    ${SAUCEDEMO_URL}
    LoginPage.Verify Login Page Loaded
    
    # Record start time
    ${start_time}=    Get Current Date    result_format=timestamp
    
    # Perform login
    LoginPage.Login As User    ${user_dict}
    
    # Wait for products page to load
    ProductsPage.Verify Products Page Loaded
    
    # Record end time
    ${end_time}=    Get Current Date    result_format=timestamp
    
    # Calculate elapsed time
    ${elapsed}=    Evaluate    ${end_time} - ${start_time}
    
    # Logout for clean state
    ProductsPage.Logout
    
    [Return]    ${elapsed}

Measure Product Page Load Time
    [Documentation]    Measure time to load a specific product page
    [Arguments]    ${product_name}
    
    # Record start time
    ${start_time}=    Get Current Date    result_format=timestamp
    
    # Click on product to open detail page
    Click    css=.inventory_item:has-text("${product_name}") .inventory_item_name
    
    # Wait for product detail page to load
    Wait For Elements State    css=.inventory_details_container    visible
    Wait For Elements State    css=.inventory_details_name:has-text("${product_name}")    visible
    
    # Record end time
    ${end_time}=    Get Current Date    result_format=timestamp
    
    # Calculate elapsed time
    ${elapsed}=    Evaluate    ${end_time} - ${start_time}
    
    # Go back to products page
    Click    css=button#back-to-products
    Wait For Elements State    css=.inventory_container    visible
    
    [Return]    ${elapsed}

Measure Sorting Time
    [Documentation]    Measure time to sort products
    [Arguments]    ${sort_option}
    
    # Record start time
    ${start_time}=    Get Current Date    result_format=timestamp
    
    # Perform sorting
    ProductsPage.Sort Products    ${sort_option}
    
    # Wait for sorting to complete by checking for a stable UI
    Wait For Elements State    css=.inventory_item    stable
    
    # Record end time
    ${end_time}=    Get Current Date    result_format=timestamp
    
    # Calculate elapsed time
    ${elapsed}=    Evaluate    ${end_time} - ${start_time}
    
    [Return]    ${elapsed} 