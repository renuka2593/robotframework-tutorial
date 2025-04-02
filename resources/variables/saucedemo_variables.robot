*** Variables ***
# Browser configuration
${DEFAULT_BROWSER}      chromium
${DEFAULT_HEADLESS}     False
${DEFAULT_TIMEOUT}      10s
${DEFAULT_SLOWMO}       0ms
${VIEWPORT_WIDTH}       1280
${VIEWPORT_HEIGHT}      720

# Application URLs
${SAUCEDEMO_URL}        https://www.saucedemo.com

# User credentials
&{STANDARD_USER}        username=standard_user    password=secret_sauce
&{LOCKED_USER}          username=locked_out_user  password=secret_sauce
&{PROBLEM_USER}         username=problem_user     password=secret_sauce
&{PERF_GLITCH_USER}     username=performance_glitch_user    password=secret_sauce

# Expected values
${LOGIN_PAGE_TITLE}     Swag Labs
${PRODUCTS_PAGE_TITLE}  Swag Labs
${INVENTORY_HEADER}     Products
${ERROR_MSG_LOCKED_USER}    Sorry, this user has been locked out 