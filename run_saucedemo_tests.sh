#!/bin/bash
# Script to run SauceDemo tests with different browser configurations

# Set default values
BROWSER=${BROWSER:-"chromium"}
HEADLESS=${HEADLESS:-"false"}
SLOWMO=${SLOWMO:-"0ms"}
TIMEOUT=${TIMEOUT:-"10s"}
TEST_TYPE=${TEST_TYPE:-"all"}
REPORTS_DIR=${REPORTS_DIR:-"reports/saucedemo"}

# Create reports directory if it doesn't exist
mkdir -p $REPORTS_DIR

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}============================================"
echo -e "SauceDemo Tests Runner"
echo -e "============================================${NC}"
echo -e "${YELLOW}Browser: $BROWSER${NC}"
echo -e "${YELLOW}Headless: $HEADLESS${NC}"
echo -e "${YELLOW}SlowMo: $SLOWMO${NC}"
echo -e "${YELLOW}Reports: $REPORTS_DIR${NC}"
echo

# Function to run tests
run_tests() {
    local test_type=$1
    local browser=$2
    local headless=$3
    local test_path=$4
    local report_name=$5
    
    echo -e "${BLUE}Running $test_type tests with $browser browser...${NC}"
    
    # Export environment variables
    export BROWSER=$browser
    export HEADLESS=$headless
    export SLOWMO=$SLOWMO
    export TIMEOUT=$TIMEOUT
    
    # Run the tests
    robot --outputdir $REPORTS_DIR \
          --name "SauceDemo-$test_type-$browser" \
          --output "$report_name.xml" \
          --report "$report_name.html" \
          --log "$report_name.log.html" \
          $test_path
    
    # Check if tests passed
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Tests passed!${NC}"
    else
        echo -e "${RED}✗ Tests failed!${NC}"
        FAILED=1
    fi
    echo
}

# Initialize failure flag
FAILED=0

# Determine test path based on test type
case $TEST_TYPE in
    login)
        TEST_PATH="tests/saucedemo/login_tests.robot"
        ;;
    products)
        TEST_PATH="tests/saucedemo/product_tests.robot"
        ;;
    performance)
        TEST_PATH="tests/saucedemo/performance_tests.robot"
        ;;
    all)
        TEST_PATH="tests/saucedemo/"
        ;;
    *)
        echo -e "${RED}Invalid test type: $TEST_TYPE${NC}"
        echo "Valid options: login, products, performance, all"
        exit 1
        ;;
esac

# Check if we should run in cross-browser mode
if [[ "$1" == "--cross-browser" ]]; then
    # Run with Chrome
    run_tests "Chromium" "chromium" $HEADLESS $TEST_PATH "saucedemo-chromium"
    
    # Run with Firefox
    run_tests "Firefox" "firefox" $HEADLESS $TEST_PATH "saucedemo-firefox"
    
    # Run with WebKit
    run_tests "WebKit" "webkit" $HEADLESS $TEST_PATH "saucedemo-webkit"
else
    # Run with the specified browser
    run_tests "Single" $BROWSER $HEADLESS $TEST_PATH "saucedemo-$BROWSER"
fi

# Generate combined report if cross-browser
if [[ "$1" == "--cross-browser" ]]; then
    echo -e "${BLUE}Generating combined report...${NC}"
    rebot --outputdir $REPORTS_DIR \
          --name "SauceDemo-CrossBrowser" \
          --output "saucedemo-combined.xml" \
          --report "saucedemo-combined.html" \
          --merge \
          $REPORTS_DIR/saucedemo-*.xml
fi

# Print usage information
echo -e "${BLUE}Usage examples:${NC}"
echo -e "${YELLOW}./run_saucedemo_tests.sh${NC} - Run all tests with default browser"
echo -e "${YELLOW}BROWSER=firefox ./run_saucedemo_tests.sh${NC} - Run with Firefox"
echo -e "${YELLOW}TEST_TYPE=login ./run_saucedemo_tests.sh${NC} - Run only login tests"
echo -e "${YELLOW}HEADLESS=true ./run_saucedemo_tests.sh${NC} - Run in headless mode"
echo -e "${YELLOW}./run_saucedemo_tests.sh --cross-browser${NC} - Run with all browsers"

# Exit with appropriate status
if [ $FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi 