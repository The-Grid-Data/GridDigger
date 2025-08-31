# 🚀 Quick Local Testing Guide

Since Docker isn't available, here's how to test locally right now!

## 1. Install Dependencies
```bash
# Use the stable requirements (no conflicts)
pip install -r requirements_stable.txt
```

## 2. Set Up Test Environment
```bash
# Create test configuration
./test.sh setup
```

## 3. Run Tests
```bash
# Run all tests
./test.sh local

# Or run specific tests
./test.sh local unit        # Unit tests only
./test.sh local coverage    # With coverage report
```

## Alternative: Direct pytest Commands

If the test script doesn't work, use pytest directly:

```bash
# Set Python path
export PYTHONPATH=.

# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_api_v2.py -v
python -m pytest tests/test_services.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=term-missing
```

## Troubleshooting

### If you get import errors:
```bash
export PYTHONPATH=.
```

### If you get database errors:
The tests use mocks, so you don't need a real database for unit tests.

### If you get dependency conflicts:
```bash
pip install -r requirements_stable.txt --force-reinstall
```

## What the Tests Do

- **Unit Tests**: Test individual functions with mocks
- **Service Tests**: Test business logic components
- **API Tests**: Test GraphQL client functionality

All tests use mocks for external dependencies, so they run without needing:
- Real database
- Real API endpoints
- Redis server

## Expected Output

```bash
tests/test_api_v2.py::TestGraphQLClient::test_execute_query_success PASSED
tests/test_api_v2.py::TestGridAPIv2::test_search_profiles_success PASSED
tests/test_services.py::TestProfileService::test_get_profile_by_id_success PASSED
...

========================= X passed in Y.YYs =========================
```

**Ready to test!** 🧪