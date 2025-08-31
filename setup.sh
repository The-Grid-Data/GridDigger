#!/bin/bash

# GridDigger Bot - Quick Setup Script
# This script helps you set up the environment for development or testing

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

echo "🚀 GridDigger Bot - Quick Setup"
echo "==============================="

# Check if .env already exists
if [ -f .env ]; then
    print_warning ".env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Keeping existing .env file"
        exit 0
    fi
fi

print_header "Setting up environment configuration..."

# Copy template to .env
cp .env.template .env
print_status "Created .env file from template"

# Interactive setup
print_header "Let's configure your bot step by step:"

# Telegram Bot Token
echo ""
print_status "1. Telegram Bot Configuration"
echo "   Get your bot token from @BotFather on Telegram"
read -p "   Enter your Telegram Bot Token: " bot_token
if [ ! -z "$bot_token" ]; then
    sed -i "s/TELEGRAM_BOT_TOKEN=your_bot_token_here_from_botfather/TELEGRAM_BOT_TOKEN=$bot_token/" .env
    print_status "Bot token configured"
else
    print_warning "Bot token not set - you'll need to edit .env manually"
fi

# Mode selection
echo ""
print_status "2. Bot Mode"
echo "   Choose 'polling' for development or 'webhook' for production"
read -p "   Enter mode (polling/webhook) [polling]: " mode
mode=${mode:-polling}
sed -i "s/MODE=webhook/MODE=$mode/" .env
print_status "Mode set to: $mode"

# Database configuration
echo ""
print_status "3. Database Configuration"
read -p "   Database host [localhost]: " db_host
db_host=${db_host:-localhost}
sed -i "s/DB_HOST=localhost/DB_HOST=$db_host/" .env

read -p "   Database name [griddigger]: " db_name
db_name=${db_name:-griddigger}
sed -i "s/DB_DATABASE=griddigger/DB_DATABASE=$db_name/" .env

read -p "   Database username: " db_user
if [ ! -z "$db_user" ]; then
    sed -i "s/DB_USER=your_db_username/DB_USER=$db_user/" .env
fi

read -s -p "   Database password: " db_password
echo
if [ ! -z "$db_password" ]; then
    sed -i "s/DB_PASSWORD=your_db_password/DB_PASSWORD=$db_password/" .env
fi

print_status "Database configuration completed"

# API Configuration
echo ""
print_status "4. API Configuration"
read -p "   Use new GraphQL endpoint? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sed -i "s/USE_NEW_GRAPHQL_ENDPOINT=false/USE_NEW_GRAPHQL_ENDPOINT=true/" .env
    print_status "New GraphQL endpoint enabled"
else
    print_status "Using current GraphQL endpoint"
fi

# Optional Redis
echo ""
print_status "5. Caching (Optional)"
read -p "   Do you have Redis available? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "   Redis URL [redis://localhost:6379]: " redis_url
    redis_url=${redis_url:-redis://localhost:6379}
    echo "REDIS_URL=$redis_url" >> .env
    print_status "Redis caching configured"
else
    print_status "Using in-memory caching"
fi

# Testing setup
echo ""
print_status "6. Testing Setup (Optional)"
read -p "   Set up testing environment? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cp .env.testing .env.test
    
    # Update test database name
    test_db_name="${db_name}_test"
    sed -i "s/TEST_DB_DATABASE=griddigger_test/TEST_DB_DATABASE=$test_db_name/" .env.test
    sed -i "s/TEST_DB_USER=root/TEST_DB_USER=$db_user/" .env.test
    sed -i "s/TEST_DB_PASSWORD=password/TEST_DB_PASSWORD=$db_password/" .env.test
    sed -i "s/TEST_DB_HOST=localhost/TEST_DB_HOST=$db_host/" .env.test
    
    print_status "Testing environment configured (.env.test created)"
    print_warning "Remember to create the test database: $test_db_name"
fi

print_header "Setup completed! 🎉"
echo ""
print_status "Configuration files created:"
echo "  ✅ .env - Main configuration"
if [ -f .env.test ]; then
    echo "  ✅ .env.test - Testing configuration"
fi

echo ""
print_status "Next steps:"
echo "  1. Review and edit .env file if needed"
echo "  2. Create your database: $db_name"
if [ -f .env.test ]; then
    echo "  3. Create test database: ${db_name}_test"
    echo "  4. Run tests: python -m pytest"
    echo "  5. Start the bot: python app.py"
else
    echo "  3. Start the bot: python app.py"
fi

echo ""
print_status "For deployment, run: ./deploy.sh"
print_status "For help, see: README_ENHANCED.md"

echo ""
print_warning "Important: Never commit .env files to version control!"