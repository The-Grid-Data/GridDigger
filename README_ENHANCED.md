# GridDigger - Enhanced Telegram Bot

[![GridDigger](https://github.com/The-Grid-Data/GridDigger/tree/railway)](https://github.com/The-Grid-Data/GridDigger/)

## Overview

GridDigger is a high-performance Telegram bot that provides access to The Grid ID database through an intuitive interface. This enhanced version features improved architecture, performance optimizations, and comprehensive GraphQL API integration.

## 🚀 New Features & Improvements

### Technical Excellence
- **GraphQL Migration**: Seamless migration to new GraphQL endpoint with backward compatibility
- **Enhanced Architecture**: Clean separation of concerns with service layer pattern
- **Performance Optimization**: Connection pooling, caching, and async operations
- **Comprehensive Testing**: Unit tests, integration tests, and performance benchmarks
- **Advanced Logging**: Structured logging with multiple output formats
- **Error Handling**: Robust error handling with detailed monitoring

### API Integration
- **Dual API Support**: Supports both legacy and new GraphQL endpoints
- **Smart Caching**: Redis and in-memory caching with configurable TTL
- **Connection Pooling**: Optimized database and HTTP connection management
- **Retry Logic**: Automatic retry with exponential backoff for failed requests

### Monitoring & Observability
- **Health Checks**: Comprehensive health monitoring for all components
- **Performance Metrics**: Detailed performance tracking and analytics
- **Error Monitoring**: Integration with Sentry for error tracking
- **User Analytics**: Enhanced user behavior tracking and statistics

## 📋 Requirements

### System Requirements
- Python 3.8+
- MySQL 5.7+ or 8.0+
- Redis 6.0+ (optional, for caching)
- 512MB+ RAM
- 1GB+ disk space

### Dependencies
See `requirements_enhanced.txt` for complete dependency list.

## 🛠 Installation

### 1. Clone Repository
```bash
git clone https://github.com/The-Grid-Data/GridDigger.git
cd GridDigger
```

### 2. Install Dependencies
```bash
# Install enhanced requirements
pip install -r requirements_enhanced.txt

# Or install basic requirements
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file with the following variables:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
MODE=webhook  # or 'polling' for development
PORT=5000
LAMBDA_WEBHOOK_URL=your_webhook_url_here

# GraphQL API Configuration
GRAPHQL_ENDPOINT=https://maximum-grackle-73.hasura.app/v1/graphql
GRAPHQL_ENDPOINT_V2=https://beta.node.thegrid.id/graphql
HASURA_API_TOKEN=your_token_here  # optional
HASURA_API_TOKEN_V2=your_v2_token_here  # optional

# Database Configuration
DB_HOST=localhost
DB_DATABASE=griddigger
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_PORT=3306

# Performance Configuration
CONNECTION_POOL_SIZE=10
REQUEST_TIMEOUT=30
CACHE_TTL=300
MAX_RETRIES=3

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# Feature Flags
USE_NEW_GRAPHQL_ENDPOINT=false  # Set to true to use new endpoint
ENABLE_CACHING=true
ENABLE_MONITORING=true

# Monitoring Configuration
MONITORING_GROUP_ID=your_monitoring_group_id
LOG_LEVEL=INFO
SENTRY_DSN=your_sentry_dsn  # optional
```

### 4. Database Setup
```bash
# The application will automatically create required tables
# Or run manually:
python -c "from database_v2 import db_initializer; db_initializer.initialize_schema()"
```

## 🚀 Usage

### Development Mode
```bash
# Set environment variables
export MODE=polling
export LOG_LEVEL=DEBUG

# Run the bot
python app.py
```

### Production Mode
```bash
# Set environment variables
export MODE=webhook
export LOG_LEVEL=INFO

# Run with gunicorn (recommended)
gunicorn --bind 0.0.0.0:$PORT --workers 2 app:main

# Or run directly
python app.py
```

### Docker Deployment
```bash
# Build image
docker build -t griddigger .

# Run container
docker run -d \
  --name griddigger \
  --env-file .env \
  -p 5000:5000 \
  griddigger
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_api_v2.py

# Run with verbose output
python -m pytest -v
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Security check
bandit -r .
```

## 📊 API Endpoints

### GraphQL Queries

#### Search Profiles
```graphql
query SearchForProfileNameOrAssetTicker($searchTerm: String!) {
  roots(
    where: {
      _or: [
        {profileInfos: {name: {_contains: $searchTerm}}}, 
        {assets: {ticker: {_contains: $searchTerm}}}
      ]
    }
  ) {
    id
    slug
    profileInfos {
      name
      descriptionShort
      logo
    }
  }
}
```

#### Get Profile Details
```graphql
query getProfileData($profileId: String!) {
  profileInfos(
    where: {
      _or: [
        {root: {id: {_eq: $profileId}}},
        {root: {slug: {_eq: $profileId}}}
      ]
    }
  ) {
    name
    tagLine
    descriptionShort
    descriptionLong
    logo
    profileSector { name }
    profileType { name }
    profileStatus { name }
    urls { url, urlType { name } }
    root {
      assets { name, ticker }
      socials { url }
      entities { name }
      products { name }
    }
  }
}
```

## 🏗 Architecture

### Project Structure
```
GridDigger/
├── app.py                 # Enhanced main application
├── config.py             # Configuration management
├── logging_config.py     # Logging setup
├── cache.py              # Caching layer
├── api_v2.py             # New GraphQL API client
├── database_v2.py        # Enhanced database operations
├── models/               # Data models
│   ├── __init__.py
│   ├── common.py
│   ├── profile.py
│   └── search.py
├── services/             # Business logic layer
│   ├── __init__.py
│   ├── profile_service.py
│   ├── search_service.py
│   └── filter_service.py
├── handlers/             # Telegram handlers
│   ├── __init__.py
│   ├── commands.py
│   ├── profiles.py
│   ├── filters.py
│   └── utils.py
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_api_v2.py
│   └── test_services.py
└── logs/                 # Log files
```

### Key Components

#### 1. Configuration Management (`config.py`)
- Centralized configuration with validation
- Environment-based settings
- Feature flags for gradual rollout

#### 2. Enhanced API Client (`api_v2.py`)
- GraphQL client with connection pooling
- Automatic retry logic with exponential backoff
- Comprehensive error handling
- Backward compatibility functions

#### 3. Service Layer (`services/`)
- **ProfileService**: Profile-related business logic
- **SearchService**: Search functionality and caching
- **FilterService**: Filter management and validation

#### 4. Caching System (`cache.py`)
- Redis and in-memory caching support
- Configurable TTL and cache keys
- Cache warming and statistics

#### 5. Database Layer (`database_v2.py`)
- Connection pooling with MySQL
- Repository pattern implementation
- Health checks and monitoring
- Automatic schema initialization

## 🔧 Configuration Options

### Feature Flags
- `USE_NEW_GRAPHQL_ENDPOINT`: Enable new GraphQL endpoint
- `ENABLE_CACHING`: Enable caching layer
- `ENABLE_MONITORING`: Enable monitoring and analytics

### Performance Tuning
- `CONNECTION_POOL_SIZE`: Database connection pool size
- `REQUEST_TIMEOUT`: HTTP request timeout
- `CACHE_TTL`: Default cache time-to-live
- `MAX_RETRIES`: Maximum retry attempts

## 📈 Monitoring & Analytics

### Health Checks
- Database connectivity and performance
- API endpoint availability
- Cache system status
- Memory and CPU usage

### Metrics
- User interaction statistics
- API response times
- Cache hit rates
- Error rates and types

### Logging
- Structured JSON logging for production
- Colored console logging for development
- Separate error log files
- Configurable log levels

## 🔄 Migration Guide

### From Legacy to New API

1. **Enable Feature Flag**
   ```bash
   export USE_NEW_GRAPHQL_ENDPOINT=true
   ```

2. **Update Environment Variables**
   ```bash
   export GRAPHQL_ENDPOINT_V2=https://beta.node.thegrid.id/graphql
   export HASURA_API_TOKEN_V2=your_new_token
   ```

3. **Test Migration**
   ```bash
   # Run tests to verify compatibility
   python -m pytest tests/test_api_v2.py
   ```

4. **Monitor Performance**
   - Check logs for any errors
   - Monitor response times
   - Verify data consistency

### Rollback Plan
If issues occur, simply set:
```bash
export USE_NEW_GRAPHQL_ENDPOINT=false
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Run tests before committing
5. Follow code style guidelines

### Code Style
- Use `black` for code formatting
- Follow PEP 8 guidelines
- Add type hints where possible
- Write comprehensive tests

### Pull Request Process
1. Ensure all tests pass
2. Update documentation if needed
3. Add changelog entry
4. Request review from maintainers

## 📝 Changelog

### v2.0.0 (Enhanced Version)
- ✅ GraphQL API migration with backward compatibility
- ✅ Enhanced architecture with service layer
- ✅ Performance optimizations and caching
- ✅ Comprehensive testing framework
- ✅ Advanced logging and monitoring
- ✅ Database connection pooling
- ✅ Error handling improvements
- ✅ Configuration management
- ✅ Health checks and analytics

### v1.0.0 (Original Version)
- Basic Telegram bot functionality
- REST API integration
- Simple database operations
- Basic error handling

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/The-Grid-Data/GridDigger/issues)
- **Documentation**: [Wiki](https://github.com/The-Grid-Data/GridDigger/wiki)
- **Telegram**: [@the_grid_id_bot](https://t.me/the_grid_id_bot)

## 🙏 Acknowledgments

- The Grid ID team for providing the data API
- Telegram Bot API for the platform
- Open source community for the tools and libraries