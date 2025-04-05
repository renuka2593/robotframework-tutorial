*** Settings ***
Documentation     Keywords for interacting with the inventory page
Resource         ../locators/inventory_page.resource
Library          Browser
Library          ../../libraries/LoggerLibrary.py

*** Keywords ***
Verify Inventory Page Loaded
    [Documentation]    Verifies that the inventory page has loaded
    Wait For Elements State    ${INVENTORY_CONTAINER}    visible
    Log Info    Inventory page loaded successfully

Add Product To Cart
    [Documentation]    Adds a product to the cart by its name
    [Arguments]    ${product_name}
    ${selector}=    Set Variable    ${ADD_TO_CART_PREFIX}${product_name}
    Click    ${selector}
    Wait For Elements State    ${REMOVE_FROM_CART_PREFIX}${product_name}    visible

Remove Product From Cart
    [Documentation]    Removes a product from the cart by its name
    [Arguments]    ${product_name}
    ${selector}=    Set Variable    ${REMOVE_FROM_CART_PREFIX}${product_name}
    Click    ${selector}
    Wait For Elements State    ${ADD_TO_CART_PREFIX}${product_name}    visible

Get Cart Item Count
    [Documentation]    Returns the number of items in the cart
    ${count}=    Get Text    ${SHOPPING_CART_BADGE}
    RETURN    ${count}

Sort Products
    [Documentation]    Sorts products using the dropdown
    [Arguments]    ${sort_option}
    Select Options By    ${PRODUCT_SORT}    text    ${sort_option}
    Log Info    Products sorted by ${sort_option}

Open Shopping Cart
    [Documentation]    Opens the shopping cart page
    Click    ${SHOPPING_CART_LINK}

Logout
    [Documentation]    Logs out of the application
    Click    ${BURGER_MENU}
    Wait For Elements State    ${LOGOUT_LINK}    visible
    Click    ${LOGOUT_LINK}
    Wait For Elements State    ${LOGIN_LOGO}    visible    timeout=10s 