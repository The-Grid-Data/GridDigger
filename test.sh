#!/bin/bash

# GridDigger Bot - Test Runner Script
# This script provides easy commands to run different types of tests

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

show_help() {
    echo "🧪 GridDigger Test Runner"
    echo "========================"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  local           Run tests locally (requires local setup)"
    echo "  docker          Run tests in Docker containers"
    echo "  coverage        Run tests with coverage report"
    echo "  integration     Run integration tests only"
    echo "  unit            Run unit tests only"
    echo "  clean           Clean up test artifacts and containers"
    echo "  setup           Set up test environment"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 docker                    # Run all tests in Docker"
    echo "  $0 coverage                  # Run tests with coverage"
    echo "  $0 local unit               # Run unit tests locally"
    echo "  $0 docker integration       # Run integration tests in Docker"
    echo ""
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        echo ""
        echo "To install Docker:"
        echo "  macOS:   brew install docker"
        echo "  Ubuntu:  sudo apt install docker.io"
        echo "  Windows: Install Docker Desktop"
        echo ""
        echo "Or run tests locally with: ./test.sh local"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        echo ""
        echo "To install Docker Compose:"
        echo "  macOS:   brew install docker-compose"
        echo "  Ubuntu:  sudo apt install docker-compose"
        echo "  Windows: Included with Docker Desktop"
        echo ""
        echo "Or run tests locally with: ./test.sh local"
        exit 1
    fi
}

setup_test_env() {
    print_header "Setting up test environment..."
    
    # Create .env.test if it doesn't exist
    if [ ! -f .env.test ]; then
        if [ -f .env.testing ]; then
            cp .env.testing .env.test
            print_status "Created .env.test from .env.testing template"
        else
            print_error ".env.testing template not found!"
            exit 1
        fi
    else
        print_status ".env.test already exists"
    fi
    
    # Create coverage reports directory
    mkdir -p coverage_reports
    print_status "Created coverage_reports directory"
    
    print_status "Test environment setup complete"
}

run_local_tests() {
    print_header "Running tests locally..."
    
    # Check if .env.test exists
    if [ ! -f .env.test ]; then
        print_warning ".env.test not found, setting up..."
        setup_test_env
    fi
    
    # Check if pytest is available
    if ! command -v pytest &> /dev/null; then
        print_error "pytest not found! Install with: pip install -r requirements.txt"
        exit 1
    fi
    
    # Set test environment
    export PYTHONPATH=.
    
    case "$1" in
        "unit")
            print_status "Running unit tests..."
            python -m pytest tests/ -v -m "not integration" --tb=short
            ;;
        "integration")
            print_status "Running integration tests..."
            python -m pytest tests/ -v -m "integration" --tb=short
            ;;
        "coverage")
            print_status "Running tests with coverage..."
            python -m pytest tests/ -v --cov=. --cov-report=html:coverage_reports --cov-report=term-missing
            print_status "Coverage report generated in coverage_reports/"
            ;;
        *)
            print_status "Running all tests..."
            python -m pytest tests/ -v --tb=short
            ;;
    esac
}

run_docker_tests() {
    print_header "Running tests in Docker..."
    check_docker
    
    case "$1" in
        "unit")
            print_status "Running unit tests in Docker..."
            docker-compose -f docker-compose.test.yml run --rm griddigger-test \
                python -m pytest tests/ -v -m "not integration" --tb=short
            ;;
        "integration")
            print_status "Running integration tests in Docker..."
            docker-compose -f docker-compose.test.yml run --rm --profile integration integration-test
            ;;
        "coverage")
            print_status "Running tests with coverage in Docker..."
            docker-compose -f docker-compose.test.yml run --rm --profile coverage test-coverage
            print_status "Coverage report will be in coverage_reports/"
            ;;
        *)
            print_status "Running all tests in Docker..."
            docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
            ;;
    esac
}

clean_test_artifacts() {
    print_header "Cleaning up test artifacts..."
    
    # Clean Docker containers and volumes
    if command -v docker-compose &> /dev/null; then
        print_status "Stopping and removing test containers..."
        docker-compose -f docker-compose.test.yml down -v --remove-orphans 2>/dev/null || true
        
        # Remove test images
        docker rmi griddigger_griddigger-test 2>/dev/null || true
        docker rmi griddigger_test-coverage 2>/dev/null || true
        docker rmi griddigger_integration-test 2>/dev/null || true
    fi
    
    # Clean local artifacts
    print_status "Cleaning local test artifacts..."
    rm -rf .pytest_cache/
    rm -rf __pycache__/
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Clean coverage reports (optional)
    read -p "Remove coverage reports? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf coverage_reports/
        rm -f .coverage
        print_status "Coverage reports removed"
    fi
    
    print_status "Cleanup complete"
}

show_test_status() {
    print_header "Test Environment Status"
    
    echo "Configuration Files:"
    [ -f .env.test ] && echo "  ✅ .env.test" || echo "  ❌ .env.test (missing)"
    [ -f .env.testing ] && echo "  ✅ .env.testing" || echo "  ❌ .env.testing (missing)"
    [ -f docker-compose.test.yml ] && echo "  ✅ docker-compose.test.yml" || echo "  ❌ docker-compose.test.yml (missing)"
    
    echo ""
    echo "Test Files:"
    [ -d tests/ ] && echo "  ✅ tests/ directory" || echo "  ❌ tests/ directory (missing)"
    [ -f tests/test_api_v2.py ] && echo "  ✅ API tests" || echo "  ❌ API tests (missing)"
    [ -f tests/test_services.py ] && echo "  ✅ Service tests" || echo "  ❌ Service tests (missing)"
    
    echo ""
    echo "Dependencies:"
    command -v python3 &> /dev/null && echo "  ✅ Python 3" || echo "  ❌ Python 3 (missing)"
    command -v pytest &> /dev/null && echo "  ✅ pytest" || echo "  ❌ pytest (missing)"
    command -v docker &> /dev/null && echo "  ✅ Docker" || echo "  ❌ Docker (missing)"
    command -v docker-compose &> /dev/null && echo "  ✅ Docker Compose" || echo "  ❌ Docker Compose (missing)"
    
    echo ""
    if command -v docker-compose &> /dev/null; then
        echo "Docker Test Services:"
        docker-compose -f docker-compose.test.yml ps 2>/dev/null || echo "  No test containers running"
    fi
}

# Main execution
case "$1" in
    "local")
        run_local_tests "$2"
        ;;
    "docker")
        run_docker_tests "$2"
        ;;
    "coverage")
        if [ "$2" = "docker" ]; then
            run_docker_tests "coverage"
        else
            run_local_tests "coverage"
        fi
        ;;
    "integration")
        if [ "$2" = "docker" ]; then
            run_docker_tests "integration"
        else
            run_local_tests "integration"
        fi
        ;;
    "unit")
        if [ "$2" = "docker" ]; then
            run_docker_tests "unit"
        else
            run_local_tests "unit"
        fi
        ;;
    "setup")
        setup_test_env
        ;;
    "clean")
        clean_test_artifacts
        ;;
    "status")
        show_test_status
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

print_status "Test runner completed!"