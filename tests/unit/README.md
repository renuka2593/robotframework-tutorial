# Unit Tests for Robot Framework UI Test Automation

This directory contains unit tests for validating the core functionality of the framework.

## Running the Tests

```bash
# Run from the project root
python -m pytest tests/unit

# Run a specific test file
python -m pytest tests/unit/test_locators.py

# Run with coverage
python -m pytest tests/unit --cov=utils --cov=resources
```

## Test Files

- `test_locators.py` - Tests for dynamic locator generation functionality

## Adding New Tests

When adding new tests:

1. Follow the naming convention `test_*.py`
2. Import the module to be tested by adding the project root to `sys.path`
3. Use unittest assertions for validation
