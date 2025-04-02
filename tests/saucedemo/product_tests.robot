*** Settings ***
Documentation     Product tests for SauceDemo using Browser library
Resource          ../../resources/keywords/saucedemo_keywords.robot
Resource          ../../resources/variables/saucedemo_variables.robot

Test Setup        Setup Product Tests
Test Teardown     Teardown SauceDemo Test

*** Variables ***
@{TEST_PRODUCTS}    Sauce Labs Backpack    Sauce Labs Bike Light    Sauce Labs Bolt T-Shirt

*** Test Cases ***
Verify Product Count
    [Documentation]    Verify the correct number of products are displayed
    [Tags]            products    smoke
    ${count}=    ProductsPage.Get Product Count
    Should Be Equal As Integers    ${count}    6

Sort Products By Price Low To High
    [Documentation]    Verify sorting products by price low to high
    [Tags]            products    sorting
    Verify Products Are Sorted By Price Low To High

Sort Products By Price High To Low
    [Documentation]    Verify sorting products by price high to low
    [Tags]            products    sorting
    Verify Products Are Sorted By Price High To Low

Add Single Product To Cart
    [Documentation]    Add a single product to cart
    [Tags]            products    cart
    ProductsPage.Add Product To Cart    Sauce Labs Backpack
    ${count}=    ProductsPage.Get Cart Count
    Should Be Equal As Integers    ${count}    1

Add Multiple Products To Cart
    [Documentation]    Add multiple products to cart
    [Tags]            products    cart
    Add Products To Cart    @{TEST_PRODUCTS}
    ${count}=    ProductsPage.Get Cart Count
    Should Be Equal As Integers    ${count}    3

Remove Product From Cart
    [Documentation]    Add and then remove a product from cart
    [Tags]            products    cart
    # First add the product
    ProductsPage.Add Product To Cart    Sauce Labs Backpack
    ${count}=    ProductsPage.Get Cart Count
    Should Be Equal As Integers    ${count}    1
    
    # Then remove it
    ProductsPage.Remove Product From Cart    Sauce Labs Backpack
    ${count}=    ProductsPage.Get Cart Count
    Should Be Equal As Integers    ${count}    0

Complete Checkout Process
    [Documentation]    Complete the entire checkout process
    [Tags]            products    checkout    smoke
    Complete Purchase Flow    Sauce Labs Backpack    Sauce Labs Bike Light

Verify Page Elements With Different Viewport Sizes
    [Documentation]    Test responsive behavior with different viewport sizes
    [Tags]            products    responsive
    [Template]        Check Products Page With Viewport Size
    1920    1080    # Desktop
    1024    768     # Tablet
    414     896     # Mobile

*** Keywords ***
Setup Product Tests
    [Documentation]    Setup for product tests - login first
    Setup SauceDemo Test
    Login As Standard User

Check Products Page With Viewport Size
    [Documentation]    Verify products page with different viewport sizes
    [Arguments]    ${width}    ${height}
    
    # Set the viewport size
    Set Viewport Size    ${width}    ${height}
    
    # Verify the page still works
    ProductsPage.Verify Products Page Loaded
    ${count}=    ProductsPage.Get Product Count
    Should Be Equal As Integers    ${count}    6
    
    # Take a screenshot with the viewport size in the filename
    Take Screenshot    filename=products-${width}x${height} 