# GridDigger Local Testing Guide

This guide explains how to test GridDigger locally with production credentials for fast development and debugging.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy the template
cp .env.local.template .env.local

# Edit with your production credentials
nano .env.local  # or use your preferred editor
```

### 2. Start Optional Services
```bash
# Start Redis for caching (optional)
docker-compose -f docker-compose.local.yml up -d
```

### 3. Run the Bot
```bash
# The script automatically loads .env.local
python3 run_local.py

# Alternative: Load manually and run directly
source .env.local && python3 app.py
```

### 4. Test with Telegram
- Open your Telegram app
- Find your bot
- Send `/start` to begin testing
- Test all bot features with real data!

## 📋 What You Need

### Required Credentials
- **Telegram Bot Token**: Your real bot token from @BotFather
- **Database Credentials**: Access to your production database
- **GraphQL Endpoint**: V2 endpoint (no authentication required)

### Optional Services
- **Redis**: For caching (can run locally via Docker)

## 🔧 Configuration Details

### Environment Variables (.env.local)
```bash
# Essential
TELEGRAM_BOT_TOKEN=your_real_bot_token
DB_HOST=your_production_db_host
DB_DATABASE=your_production_db_name
DB_USER=your_production_db_user
DB_PASSWORD=your_production_db_password
GRAPHQL_ENDPOINT_V2=https://beta.node.thegrid.id/graphql

# Recommended
MODE=polling
LOG_LEVEL=DEBUG
ENABLE_CACHING=true
REDIS_URL=redis://localhost:6379/0
```

### Key Features
- **Production Database**: Direct connection to your production database
- **Production API**: Uses the V2 GraphQL endpoint
- **Local Execution**: Runs on your machine for fast debugging
- **Real Telegram**: Test with actual Telegram UI and interactions

## 🛠️ Troubleshooting

### Database Connection Issues
```bash
# Test database connection
python -c "from database_v2 import db_manager; print(db_manager.health_check())"
```

### GraphQL API Issues
```bash
# Test API endpoint
python -c "from config import Config; print(Config.get_current_endpoint_info())"
```

### Bot Token Issues
- Make sure your bot token is valid
- Check that the bot is not running elsewhere
- Verify the token has the right permissions

### Common Fixes
1. **"Table already exists" errors**: Fixed! The new database initialization handles existing tables gracefully
2. **MySQL syntax errors**: Fixed! Compatible with all MySQL versions
3. **Connection pool issues**: Optimized pool size for local testing

## 📊 What's Different from Production

### Optimizations for Local Testing
- **Smaller connection pool**: 5 connections instead of 10
- **Debug logging**: Full debug output for troubleshooting
- **Polling mode**: No webhook setup needed
- **Local Redis**: Optional caching without external dependencies

### Same as Production
- **Database**: Same production database and data
- **API**: Same V2 GraphQL endpoint
- **Bot logic**: Identical bot behavior and responses

## 🔍 Debugging Tips

### Logging
- All logs go to console and `logs/local_test.log`
- Debug level shows detailed database queries and API calls
- Each test session is clearly marked in logs

### Database Queries
- All SQL queries are logged with parameters
- Connection pool status is monitored
- Health checks provide performance metrics

### API Calls
- GraphQL queries and responses are logged
- Authentication status is verified
- Endpoint selection is clearly shown

## 🚦 Testing Workflow

### 1. Start Testing Session
```bash
python run_local.py
```

### 2. Verify Connections
The script automatically checks:
- ✅ Environment variables
- ✅ Database connection
- ✅ GraphQL endpoint
- ✅ Bot token validity

### 3. Test Bot Features
- Send `/start` to test basic functionality
- Try profile searches and filters
- Test all bot commands and interactions
- Verify data is correctly saved to database

### 4. Monitor Logs
- Watch console output for real-time debugging
- Check `logs/local_test.log` for detailed logs
- Monitor database queries and API calls

### 5. Stop Testing
- Press `Ctrl+C` to stop the bot
- Logs are automatically saved
- Redis container keeps running for next session

## 📁 File Structure

```
GridDigger/
├── run_local.py              # Main local testing script
├── .env.local.template       # Template for credentials
├── .env.local               # Your actual credentials (create this)
├── docker-compose.local.yml  # Minimal Docker setup (Redis only)
├── database_v2.py           # Fixed database handling
├── config.py                # Simplified configuration
└── logs/
    └── local_test.log       # Local testing logs
```

## 🔄 Migration from Old Testing

### What Changed
- ❌ **Removed**: Complex Docker test orchestration
- ❌ **Removed**: Separate test database setup
- ❌ **Removed**: Old endpoint configurations
- ✅ **Added**: Simple local runner script
- ✅ **Added**: Production database integration
- ✅ **Fixed**: MySQL compatibility issues

### Benefits
- **Faster setup**: Minutes instead of hours
- **Real data testing**: Use actual production data
- **Better debugging**: Full IDE support and logging
- **Production parity**: Same environment as production
- **Simplified maintenance**: One configuration to manage

## 🎯 Next Steps

1. **Setup**: Follow the Quick Start guide above
2. **Test**: Run through all bot features
3. **Debug**: Use the enhanced logging for any issues
4. **Deploy**: Your local testing ensures production readiness

---

**Need help?** Check the troubleshooting section or review the logs in `logs/local_test.log`.