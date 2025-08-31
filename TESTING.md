# 🧪 GridDigger Testing Guide

This guide explains how to run tests for the GridDigger Telegram Bot.

## Quick Start

### Option 1: Local Testing (No Docker Required)
```bash
# Set up test environment first
./test.sh setup

# Install dependencies (use stable version to avoid conflicts)
pip install -r requirements_stable.txt

# Run tests locally
./test.sh local                 # All tests
./test.sh local unit           # Unit tests only
./test.sh local coverage       # With coverage report
```

### Option 2: Docker Testing (If Docker is Available)
```bash
# First install Docker and Docker Compose:
# macOS: brew install docker docker-compose
# Ubuntu: sudo apt install docker.io docker-compose
# Windows: Install Docker Desktop

# Then run tests in Docker
./test.sh docker               # All tests
./test.sh docker unit          # Unit tests only
./test.sh docker integration   # Integration tests only
./test.sh docker coverage      # Tests with coverage report
```

## Test Environment Setup

### Automatic Setup
```bash
./test.sh setup
```
This creates `.env.test` from the template with test-specific configuration.

### Manual Setup
1. Copy the testing template:
   ```bash
   cp .env.testing .env.test
   ```

2. Edit `.env.test` with your test database credentials:
   ```bash
   TEST_DB_HOST=localhost
   TEST_DB_DATABASE=griddigger_test
   TEST_DB_USER=your_test_user
   TEST_DB_PASSWORD=your_test_password
   ```

3. Create the test database:
   ```sql
   CREATE DATABASE griddigger_test;
   GRANT ALL PRIVILEGES ON griddigger_test.* TO 'your_test_user'@'localhost';
   ```

## Test Commands Reference

### Using test.sh (Recommended)
```bash
./test.sh help                  # Show all available commands
./test.sh status                # Check test environment status
./test.sh setup                 # Set up test environment
./test.sh clean                 # Clean up test artifacts

# Docker testing
./test.sh docker                # All tests in Docker
./test.sh docker unit           # Unit tests in Docker
./test.sh docker integration    # Integration tests in Docker
./test.sh docker coverage       # Coverage report in Docker

# Local testing
./test.sh local                 # All tests locally
./test.sh local unit           # Unit tests locally
./test.sh local integration    # Integration tests locally
./test.sh local coverage       # Coverage report locally
```

### Direct pytest Commands
```bash
# Basic test run
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_api_v2.py -v
python -m pytest tests/test_services.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Run only unit tests (exclude integration)
python -m pytest tests/ -v -m "not integration"

# Run only integration tests
python -m pytest tests/ -v -m "integration"

# Run with specific verbosity
python -m pytest tests/ -v --tb=short    # Short traceback
python -m pytest tests/ -vv --tb=long    # Detailed output
```

### Direct Docker Commands
```bash
# Build and run all tests
docker-compose -f docker-compose.test.yml up --build

# Run specific test services
docker-compose -f docker-compose.test.yml run --rm griddigger-test
docker-compose -f docker-compose.test.yml run --rm --profile coverage test-coverage
docker-compose -f docker-compose.test.yml run --rm --profile integration integration-test

# Clean up test containers
docker-compose -f docker-compose.test.yml down -v
```

## Test Structure

### Test Files
- `tests/test_api_v2.py` - Tests for the new GraphQL API client
- `tests/test_services.py` - Tests for service layer components
- `tests/__init__.py` - Test package initialization

### Test Categories
- **Unit Tests**: Test individual functions and classes in isolation
- **Integration Tests**: Test interactions between components
- **Coverage Tests**: Generate code coverage reports

## Test Configuration

### Environment Variables for Testing
```bash
# Required for testing
TEST_DB_HOST=localhost
TEST_DB_DATABASE=griddigger_test
TEST_DB_USER=test_user
TEST_DB_PASSWORD=test_password
TELEGRAM_BOT_TOKEN=dummy_token_for_tests

# Optional for testing
TEST_LOG_LEVEL=DEBUG
TEST_ENABLE_CACHING=false
TEST_USE_NEW_GRAPHQL_ENDPOINT=false
```

### Docker Test Services
- **mysql-test**: Test MySQL database (port 3307)
- **redis-test**: Test Redis cache (port 6380)
- **griddigger-test**: Main test runner
- **test-coverage**: Coverage report generator
- **integration-test**: Integration test runner

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check if test database exists
mysql -u root -p -e "SHOW DATABASES LIKE 'griddigger_test';"

# Create test database if missing
mysql -u root -p -e "CREATE DATABASE griddigger_test;"
```

#### 2. Permission Errors
```bash
# Make sure scripts are executable
chmod +x test.sh
chmod +x setup.sh
chmod +x deploy.sh
```

#### 3. Docker Issues
```bash
# Clean up Docker resources
./test.sh clean

# Rebuild Docker images
docker-compose -f docker-compose.test.yml build --no-cache
```

#### 4. Import Errors
```bash
# Make sure PYTHONPATH is set
export PYTHONPATH=.

# Install all dependencies
pip install -r requirements_enhanced.txt
```

### Test Environment Status
```bash
# Check test environment status
./test.sh status
```

This will show:
- ✅ Configuration files present
- ✅ Test files available
- ✅ Dependencies installed
- ✅ Docker services status

## Coverage Reports

### Generating Coverage Reports
```bash
# Local coverage
./test.sh local coverage

# Docker coverage
./test.sh docker coverage
```

### Viewing Coverage Reports
- **HTML Report**: Open `coverage_reports/index.html` in your browser
- **Terminal Report**: Shows coverage summary in terminal
- **Coverage File**: `.coverage` file for CI/CD integration

### Coverage Targets
- **Minimum Coverage**: 80%
- **Critical Files**: 90%+ coverage for core modules
- **Test Files**: Excluded from coverage calculation

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: ./test.sh docker coverage
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Best Practices

### Writing Tests
1. **Use descriptive test names**: `test_search_profiles_success`
2. **Mock external dependencies**: Use `@patch` for API calls
3. **Test both success and failure cases**
4. **Keep tests independent**: Each test should be able to run alone
5. **Use fixtures for common setup**: Create reusable test data

### Test Organization
1. **Group related tests**: Use test classes for related functionality
2. **Use markers**: `@pytest.mark.integration` for test categorization
3. **Separate unit and integration tests**
4. **Mock external services**: Don't rely on external APIs in unit tests

### Performance
1. **Use test database**: Always separate from production data
2. **Disable caching**: For predictable test results
3. **Use shorter timeouts**: For faster test execution
4. **Parallel execution**: Use `pytest-xdist` for faster runs

## Examples

### Running Specific Tests
```bash
# Test specific function
python -m pytest tests/test_api_v2.py::TestGraphQLClient::test_execute_query_success -v

# Test specific class
python -m pytest tests/test_services.py::TestProfileService -v

# Test with keyword matching
python -m pytest tests/ -k "profile" -v
```

### Test Output Examples
```bash
# Successful test run
tests/test_api_v2.py::TestGraphQLClient::test_execute_query_success PASSED
tests/test_services.py::TestProfileService::test_get_profile_by_id_success PASSED

# Coverage report
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
api_v2.py                 150     10    93%   45-50, 120
services/profile_service.py  120      5    96%   89-92
-----------------------------------------------------
TOTAL                     500     25    95%
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `./test.sh docker` | Run all tests in Docker |
| `./test.sh local` | Run all tests locally |
| `./test.sh setup` | Set up test environment |
| `./test.sh clean` | Clean up test artifacts |
| `./test.sh status` | Check test environment |
| `./test.sh help` | Show all commands |

**Ready to test!** 🚀

Start with: `./test.sh docker` for the easiest testing experience.