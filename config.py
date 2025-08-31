"""
Configuration management for GridDigger Telegram Bot
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Telegram Bot Configuration
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    MODE: str = os.getenv("MODE", "webhook")
    PORT: int = int(os.getenv("PORT", 5000))
    WEBHOOK_URL: str = os.getenv("LAMBDA_WEBHOOK_URL", "")
    
    # GraphQL API Configuration
    GRAPHQL_ENDPOINT: str = os.getenv("GRAPHQL_ENDPOINT_V2", "https://beta.node.thegrid.id/graphql")
    HASURA_API_TOKEN: Optional[str] = os.getenv("HASURA_API_TOKEN_V2")
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_DATABASE: str = os.getenv("DB_DATABASE", "griddigger")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    
    # Performance Configuration
    CONNECTION_POOL_SIZE: int = int(os.getenv("CONNECTION_POOL_SIZE", 10))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 30))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", 300))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))
    
    # Redis Configuration (optional)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Monitoring Configuration
    MONITORING_GROUP_ID: Optional[str] = os.getenv("MONITORING_GROUP_ID")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    # Feature Flags
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    ENABLE_MONITORING: bool = os.getenv("ENABLE_MONITORING", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = [
            "TELEGRAM_TOKEN",
            "DB_HOST",
            "DB_DATABASE",
            "DB_USER"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
        
        return True
    
    @classmethod
    def get_graphql_endpoint(cls) -> str:
        """Get the GraphQL endpoint"""
        return cls.GRAPHQL_ENDPOINT
    
    @classmethod
    def get_graphql_headers(cls) -> dict:
        """Get GraphQL headers with authentication if available"""
        headers = {'Content-Type': 'application/json'}
        
        if cls.HASURA_API_TOKEN:
            headers['Authorization'] = f"Bearer {cls.HASURA_API_TOKEN}"
        
        return headers
    
    @classmethod
    def get_current_endpoint_info(cls) -> dict:
        """Get information about the current endpoint configuration"""
        return {
            'endpoint': cls.get_graphql_endpoint(),
            'has_auth_token': bool(cls.HASURA_API_TOKEN)
        }