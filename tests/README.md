# XHS Python SDK Tests

This directory contains the test suite for the XHS Python SDK.

## Structure

```
tests/
├── __init__.py           # Test package init
├── README.md            # This file
├── run_tests.py         # Main test runner
├── unit/                # Unit tests
│   ├── __init__.py
│   └── test_basic.py    # Basic functionality tests
├── integration/         # Integration tests
│   ├── __init__.py
│   ├── test_api_live.py # Live API tests (requires XHS_COOKIE)
│   └── test_demo.py     # Demo tests with mock data
└── fixtures/            # Test data and mocks
    └── test_data.py     # Mock data for testing
```

## Running Tests

### Quick Test Run
```bash
python tests/run_tests.py
```

### Using pytest (recommended)
```bash
# Install dev dependencies first
pip install -e ".[dev]"

# Run all tests
pytest

# Run specific test types
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only

# Run with coverage
pytest --cov=xhs_sdk
```

### Live API Testing
For integration tests that use real API calls, set the `XHS_COOKIE` environment variable:

```bash
export XHS_COOKIE="your_cookie_here"
python tests/run_tests.py
```

## Test Types

### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Mock external dependencies
- Fast execution
- No network calls

### Integration Tests (`tests/integration/`)
- Test component interactions
- May require network access
- Test with real/demo data
- `test_api_live.py` requires valid XHS_COOKIE
- `test_demo.py` uses mock data for safe testing

## Notes

⚠️  **This SDK is for learning purposes only!**
⚠️  **Do not use for commercial purposes!**

- Tests use expired/mock cookies for safety
- Live tests require setting XHS_COOKIE environment variable
- Some API calls may fail due to account permissions or rate limiting