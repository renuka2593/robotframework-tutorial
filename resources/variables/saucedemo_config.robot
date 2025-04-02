*** Variables ***
# Test configuration
${DEFAULT_BROWSER}              %{BROWSER=chromium}
${DEFAULT_HEADLESS}             %{HEADLESS=False}
${DEFAULT_TIMEOUT}              %{TIMEOUT=10s}
${DEFAULT_SLOWMO}               %{SLOWMO=0ms}

# Browser configuration dictionary (for advanced use)
&{CHROME_CONFIG}                browserName=chromium    headless=${DEFAULT_HEADLESS}    args=--disable-gpu
&{FIREFOX_CONFIG}               browserName=firefox    headless=${DEFAULT_HEADLESS}    firefoxUserPrefs={'media.autoplay.enabled': False}
&{WEBKIT_CONFIG}                browserName=webkit    headless=${DEFAULT_HEADLESS}    colorScheme=dark

# Viewport configurations
&{DESKTOP_VIEWPORT}             width=1920    height=1080
&{TABLET_VIEWPORT}              width=1024    height=768
&{MOBILE_VIEWPORT}              width=414     height=896

# Test data file paths
${TEST_DATA_DIR}                ${EXECDIR}/resources/test_data
${SCREENSHOTS_DIR}              ${EXECDIR}/reports/screenshots

# Retry configuration
${RETRY_ATTEMPTS}               3
${RETRY_INTERVAL}               2s 