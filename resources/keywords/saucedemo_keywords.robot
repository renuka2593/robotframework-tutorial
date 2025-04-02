*** Settings ***
Documentation     Common keywords for SauceDemo tests
Library           Browser
Library           OperatingSystem
Library           Collections
Library           String
Library           ../pages/saucedemo/LoginPage.py    WITH NAME    LoginPage
Library           ../pages/saucedemo/ProductsPage.py    WITH NAME    ProductsPage
Resource          ../variables/saucedemo_variables.robot

*** Keywords ***
Setup SauceDemo Test
    [Documentation]    Setup for SauceDemo tests
    [Arguments]    ${browser}=${DEFAULT_BROWSER}    ${headless}=${DEFAULT_HEADLESS}    ${timeout}=${DEFAULT_TIMEOUT}    ${slowmo}=${DEFAULT_SLOWMO}
    
    # Setup browser with configurable parameters
    New Browser    browser=${browser}    headless=${headless}    timeout=${timeout}    slowMo=${slowmo}
    New Context    viewport={'width': ${VIEWPORT_WIDTH}, 'height': ${VIEWPORT_HEIGHT}}
    Set Browser Timeout    ${DEFAULT_TIMEOUT}
    
    # Navigate to SauceDemo
    New Page    ${SAUCEDEMO_URL}
    
    # Verify login page is loaded
    LoginPage.Verify Login Page Loaded

Teardown SauceDemo Test
    [Documentation]    Teardown for SauceDemo tests
    Take Screenshot
    Close Browser

Login As Standard User
    [Documentation]    Login as the standard user
    LoginPage.Login As User    ${STANDARD_USER}
    ProductsPage.Verify Products Page Loaded

Login As Problem User
    [Documentation]    Login as the problem user
    LoginPage.Login As User    ${PROBLEM_USER}
    ProductsPage.Verify Products Page Loaded

Login With Custom Credentials
    [Documentation]    Login with custom username and password
    [Arguments]    ${username}    ${password}
    LoginPage.Login With Credentials    ${username}    ${password}

Verify Login Failed With Error
    [Documentation]    Verify login failed with expected error message
    [Arguments]    ${expected_error}
    LoginPage.Verify Login Error    ${expected_error}

Add Products To Cart
    [Documentation]    Add multiple products to cart
    [Arguments]    @{product_names}
    FOR    ${product_name}    IN    @{product_names}
        ProductsPage.Add Product To Cart    ${product_name}
    END
    
    # Verify cart count matches the number of products added
    ${cart_count}=    ProductsPage.Get Cart Count
    Should Be Equal As Integers    ${cart_count}    ${product_names.__len__()}

Verify Products Are Sorted By Price Low To High
    [Documentation]    Verify products are sorted by price in ascending order
    ProductsPage.Sort Products    lohi
    
    # Get all product prices
    ${prices}=    ProductsPage.Get Product Prices
    
    # Create a copy and sort it
    ${sorted_prices}=    Evaluate    sorted(${prices})
    
    # Compare the original list with the sorted one
    Lists Should Be Equal    ${prices}    ${sorted_prices}

Verify Products Are Sorted By Price High To Low
    [Documentation]    Verify products are sorted by price in descending order
    ProductsPage.Sort Products    hilo
    
    # Get all product prices
    ${prices}=    ProductsPage.Get Product Prices
    
    # Create a copy and sort it in reverse
    ${sorted_prices}=    Evaluate    sorted(${prices}, reverse=True)
    
    # Compare the original list with the sorted one
    Lists Should Be Equal    ${prices}    ${sorted_prices}

Complete Purchase Flow
    [Documentation]    Complete a full purchase flow
    [Arguments]    @{product_names}
    
    # Add products to cart
    Add Products To Cart    @{product_names}
    
    # Go to cart
    ProductsPage.Go To Cart
    
    # Wait for cart page and proceed to checkout
    Wait For Elements State    css=.cart_list    visible
    Click    id=checkout
    
    # Fill checkout info
    Wait For Elements State    css=.checkout_info    visible
    Fill Text    id=first-name    Test
    Fill Text    id=last-name    User
    Fill Text    id=postal-code    12345
    Click    id=continue
    
    # Complete checkout
    Wait For Elements State    css=.checkout_summary_container    visible
    Click    id=finish
    
    # Verify completion
    Wait For Elements State    css=.checkout_complete_container    visible
    Get Text    css=.complete-header    ==    THANK YOU FOR YOUR ORDER 