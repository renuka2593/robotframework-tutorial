# Robot Framework UI Test Automation

A comprehensive UI test automation framework built with Robot Framework for both web and desktop applications.

## Features

- Keyword-driven approach
- Page Object Model implementation
- Web UI testing with Selenium
- Desktop UI testing with WhiteLibrary and Pywinauto
- Dynamic locator generation
- Detailed test reporting

## Directory Structure

```
.
├── resources/
│   ├── pages/           # Page object model implementations
│   ├── keywords/        # Custom keywords
│   ├── libraries/       # Custom Python libraries
│   └── variables/       # Variable files
├── tests/
│   ├── web/             # Web UI tests
│   └── desktop/         # Desktop application tests
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

## Running Tests

### Web UI Tests

```bash
robot -d reports tests/web
```

### Desktop UI Tests

```bash
robot -d reports tests/desktop
```

### Run All Tests in Parallel

```bash
pabot --processes 2 -d reports tests/
```

## Generating Reports

Reports are automatically generated in the `reports` directory after test execution.

## Environment Configuration

Configure environment variables in a `.env` file.
