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

## Test Metrics Generation

This project includes a script to generate enhanced test metrics reports from Robot Framework `output.xml` files.

### Dependencies

Ensure you have the following installed:

- Python (>= 3.8 recommended for type hinting compatibility)
- Robot Framework (`pip install robotframework==7.0` or as specified in `requirements.txt`)
- psutil (`pip install psutil` or as specified in `requirements.txt`)
- Any other dependencies listed in `requirements.txt`.

You can install dependencies using:

```bash
pip install -r requirements.txt
```

### Usage

To generate the metrics report, run the `generate_metrics.py` script:

```bash
python3 resources/libraries/generate_metrics.py <input_path> <output_dir> [-v]
```

- `<input_path>`: Path to either:
  - A single `output.xml` file.
  - A directory containing one or more `output.xml` files (searched recursively).
- `<output_dir>`: The directory where the `metrics.json` and `index.html` report files will be saved. This directory will be created if it doesn't exist.
- `-v` (Optional): Use the verbose flag for detailed debug logging during generation.

**Examples:**

1.  **Process a single file:**

    ```bash
    python3 resources/libraries/generate_metrics.py results/output.xml metrics_report
    ```

2.  **Process all `output.xml` files in a directory (recursively):**

    ```bash
    python3 resources/libraries/generate_metrics.py results/ metrics_report
    ```

3.  **Process a directory with verbose logging:**
    ```bash
    python3 resources/libraries/generate_metrics.py -v results/ metrics_report
    ```

The generated HTML report (`index.html`) can be opened in any web browser.
