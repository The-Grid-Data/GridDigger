#!/bin/bash

# GridDigger Enhanced Deployment Script
# This script helps deploy the enhanced GridDigger Telegram Bot

set -e  # Exit on any error

echo "🚀 GridDigger Enhanced Deployment Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        echo "Please create a .env file with the required environment variables."
        echo "See README_ENHANCED.md for the complete list of variables."
        exit 1
    fi
    print_status ".env file found"
}

# Check Docker installation
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Run tests
run_tests() {
    print_header "Running Tests..."
    
    if command -v python3 &> /dev/null; then
        if [ -f requirements_enhanced.txt ]; then
            print_status "Installing test dependencies..."
            pip3 install -r requirements_enhanced.txt > /dev/null 2>&1 || true
        fi
        
        if command -v pytest &> /dev/null; then
            print_status "Running test suite..."
            python3 -m pytest tests/ -v || print_warning "Some tests failed, but continuing deployment"
        else
            print_warning "pytest not available, skipping tests"
        fi
    else
        print_warning "Python3 not available, skipping tests"
    fi
}

# Build and deploy with Docker
deploy_docker() {
    print_header "Building and Deploying with Docker..."
    
    print_status "Building Docker image..."
    docker-compose build
    
    print_status "Starting services..."
    docker-compose up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    print_status "Checking service health..."
    docker-compose ps
    
    # Show logs
    print_status "Recent logs:"
    docker-compose logs --tail=20 griddigger
}

# Deploy without Docker (direct Python)
deploy_python() {
    print_header "Deploying with Python..."
    
    # Check Python version
    if ! python3 -c "import sys; assert sys.version_info >= (3, 8)" 2>/dev/null; then
        print_error "Python 3.8+ is required!"
        exit 1
    fi
    
    print_status "Installing dependencies..."
    pip3 install -r requirements_enhanced.txt
    
    print_status "Initializing database..."
    python3 -c "from database_v2 import db_initializer; db_initializer.initialize_schema()" || print_warning "Database initialization failed"
    
    print_status "Starting bot..."
    python3 app.py
}

# Migration helper
migrate_to_new_api() {
    print_header "GraphQL API Migration Helper"
    
    print_status "This will help you migrate to the new GraphQL endpoint"
    echo ""
    echo "Current endpoint: $(grep GRAPHQL_ENDPOINT= .env | head -1 | cut -d'=' -f2)"
    echo "New endpoint: https://beta.node.thegrid.id/graphql"
    echo ""
    
    read -p "Do you want to enable the new GraphQL endpoint? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Update .env file
        if grep -q "USE_NEW_GRAPHQL_ENDPOINT=" .env; then
            sed -i 's/USE_NEW_GRAPHQL_ENDPOINT=.*/USE_NEW_GRAPHQL_ENDPOINT=true/' .env
        else
            echo "USE_NEW_GRAPHQL_ENDPOINT=true" >> .env
        fi
        
        print_status "New GraphQL endpoint enabled in .env file"
        print_warning "Make sure to set GRAPHQL_ENDPOINT_V2 and HASURA_API_TOKEN_V2 if needed"
    else
        print_status "Keeping current GraphQL endpoint"
    fi
}

# Show deployment status
show_status() {
    print_header "Deployment Status"
    
    if command -v docker-compose &> /dev/null && [ -f docker-compose.yml ]; then
        echo "Docker Services:"
        docker-compose ps 2>/dev/null || echo "Docker services not running"
        echo ""
    fi
    
    echo "Configuration:"
    echo "- Mode: $(grep MODE= .env | cut -d'=' -f2 || echo 'Not set')"
    echo "- New API: $(grep USE_NEW_GRAPHQL_ENDPOINT= .env | cut -d'=' -f2 || echo 'false')"
    echo "- Caching: $(grep ENABLE_CACHING= .env | cut -d'=' -f2 || echo 'true')"
    echo "- Log Level: $(grep LOG_LEVEL= .env | cut -d'=' -f2 || echo 'INFO')"
}

# Main menu
show_menu() {
    echo ""
    print_header "Deployment Options:"
    echo "1) Deploy with Docker (Recommended)"
    echo "2) Deploy with Python directly"
    echo "3) Run tests only"
    echo "4) Migrate to new GraphQL API"
    echo "5) Show deployment status"
    echo "6) Exit"
    echo ""
}

# Main execution
main() {
    print_status "Checking prerequisites..."
    check_env_file
    
    if [ $# -eq 0 ]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Choose an option (1-6): " choice
            
            case $choice in
                1)
                    check_docker
                    run_tests
                    deploy_docker
                    show_status
                    break
                    ;;
                2)
                    run_tests
                    deploy_python
                    break
                    ;;
                3)
                    run_tests
                    ;;
                4)
                    migrate_to_new_api
                    ;;
                5)
                    show_status
                    ;;
                6)
                    print_status "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_error "Invalid option. Please choose 1-6."
                    ;;
            esac
        done
    else
        # Command line mode
        case $1 in
            "docker")
                check_docker
                run_tests
                deploy_docker
                ;;
            "python")
                run_tests
                deploy_python
                ;;
            "test")
                run_tests
                ;;
            "migrate")
                migrate_to_new_api
                ;;
            "status")
                show_status
                ;;
            *)
                echo "Usage: $0 [docker|python|test|migrate|status]"
                echo "Or run without arguments for interactive mode"
                exit 1
                ;;
        esac
    fi
}

# Run main function
main "$@"

print_status "Deployment script completed!"
echo ""
echo "📚 For more information, see README_ENHANCED.md"
echo "🐛 For issues, check the logs/ directory"
echo "💬 Bot should be available at: https://t.me/the_grid_id_bot"