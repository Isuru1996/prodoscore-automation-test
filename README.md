# Prodoscore Automation Test Suite

This project contains all test cases for the Prodoscore application using the shared automation library.

## Project Structure

```
prodoscore-automation-test/
├── tests/                      # Test cases organized by type
│   ├── smoke/                  # Quick smoke tests
│   ├── regression/             # Full regression suite
│   ├── integration/            # Integration tests
│   └── conftest.py            # Pytest fixtures
├── config/                     # Configuration files
│   ├── pytest.ini             # Pytest configuration
│   ├── settings.yaml          # Test settings
│   └── testdata/              # Test data files
├── reports/                    # Test reports
│   ├── allure_results/        # Allure test results
│   └── html/                  # HTML reports
└── runner/                     # Test execution scripts
    ├── run.py                 # Main test runner
    └── run_parallel.py        # Parallel test runner
```

## Setup

1. Install dependencies using uv:
   ```bash
   uv sync
   ```

2. Install Playwright browsers:
   ```bash
   uv run playwright install
   ```

3. Configure test settings in `config/settings.yaml`

## Running Tests

### Run all tests:
```bash
uv run pytest
```

### Run specific test suite:
```bash
uv run pytest tests/smoke/
uv run pytest tests/regression/
```

### Run with markers:
```bash
uv run pytest -m smoke
uv run pytest -m regression
```

### Run in parallel:
```bash
uv run pytest -n auto
# or
uv run python runner/run_parallel.py
```

### Using test runners:
```bash
# Basic run
uv run python runner/run.py

# Run smoke tests only
uv run python runner/run.py --markers smoke --parallel

# Run specific path
uv run python runner/run.py --path tests/smoke/test_basic.py
```

## Test Reports

### HTML Report
After test execution, view the HTML report at:
```
reports/html/report.html
```

### Allure Report
Generate and view Allure report:
```bash
allure serve reports/allure_results
```

## Writing Tests

Tests use the automation library from `prodoscore-automation-library`. Import components as needed:

```python
from automation_lib.core.base_page import BasePage
from automation_lib.playwright.browser_manager import BrowserManager
from automation_lib.db.mysql_client import MySQLClient
```

Example test:
```python
def test_example(page):
    base_page = BasePage(page)
    base_page.navigate_to("https://example.com")
    assert base_page.is_visible("h1")
```

## Environment Variables

Set environment-specific variables:
- `TEST_ENV`: Test environment (staging, production)
- `BASE_URL`: Application base URL
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`: Database credentials

## CI/CD Integration

This project can be integrated with CI/CD pipelines using the provided test runners.
