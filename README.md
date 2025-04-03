# Robot Framework UI Test Automation

A comprehensive UI test automation framework built with Robot Framework for both web and desktop applications.

## Features

- Keyword-driven approach
- Page Object Model implementation
- Web UI testing with Selenium and Browser Library (Playwright)
- Desktop UI testing with WhiteLibrary and Pywinauto
- Dynamic locator generation
- Detailed test reporting

## Directory Structure

```
.
├── resources/
│   ├── pages/           # Page object model implementations
│   │   └── saucedemo/   # SauceDemo application page objects
│   ├── keywords/        # Custom keywords
│   ├── libraries/       # Custom Python libraries
│   └── variables/       # Variable files
├── tests/
│   ├── web/             # Selenium web UI tests
│   ├── browser/         # Browser Library (Playwright) web UI tests
│   ├── desktop/         # Desktop application tests
│   ├── saucedemo/       # SauceDemo application tests
│   └── unit/            # Unit tests for framework components
├── utils/
│   └── locators/        # Dynamic locator generation tools
├── reports/             # Test execution reports
└── requirements.txt     # Project dependencies
```

## Installation

1. Clone the repository
2. Install Python (3.8 or higher)
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install Browser Library node dependencies:

```bash
rfbrowser init
```

## Running Tests

### Web UI Tests with Selenium

```bash
robot -d reports tests/web
```

### Web UI Tests with Browser Library (Playwright)

```bash
robot -d reports tests/browser
```

### SauceDemo Tests

```bash
# Run all SauceDemo tests with default browser (chromium)
./run_saucedemo_tests.sh

# Run with a specific browser
BROWSER=firefox ./run_saucedemo_tests.sh

# Run only login tests
TEST_TYPE=login ./run_saucedemo_tests.sh

# Run in headless mode
HEADLESS=true ./run_saucedemo_tests.sh

# Run cross-browser tests
./run_saucedemo_tests.sh --cross-browser
```

### Desktop UI Tests

```bash
robot -d reports tests/desktop
```

### Run All Tests in Parallel

```bash
pabot --processes 2 -d reports tests/
```

## Testing Approaches

### 1. Selenium-based Testing (SeleniumLibrary)

- Traditional web UI testing
- Support for multiple browsers
- Extensive keyword library

### 2. Playwright-based Testing (Browser Library)

- Modern web testing with Playwright
- Faster execution and more stable tests
- Advanced features:
  - Network request interception
  - Visual testing
  - Console log access
  - Video recording of test execution

### 3. SauceDemo Application Testing

- Complete test suite for SauceDemo sample application
- Demonstrates best practices:
  - Page Object Model
  - Test layering
  - Parameterized testing
  - Cross-browser testing
  - Performance testing

### 4. Desktop Testing

- Windows desktop application testing
- Automation of native desktop applications

## Generating Reports

Reports are automatically generated in the `reports` directory after test execution.

## Dashboard Reports with Robotframework-Metrics

This framework includes support for enhanced dashboard-style reports using `robotframework-metrics`. These reports provide a comprehensive view of test execution with suite summaries, test details, and visualizations.

### Generating Dashboard Reports

After running your tests, generate a metrics dashboard with:

```bash
python -m robotmetrics --inputpath reports/ --output reports/metrics-dashboard.html
```

The dashboard provides:

- Suite and test case summaries
- Pass/fail statistics and charts
- Execution timeline visualization
- Test execution metrics with filtering
- Status breakdowns by tags and suites

### Key Benefits

- Better visibility into test execution results
- Easy identification of test performance trends
- Shareable HTML reports for stakeholders
- Interactive filtering and sorting of results

## Environment Configuration

Configure environment variables in a `.env`
