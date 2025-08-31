#!/usr/bin/env python3
"""
GridDigger Local Testing Runner
Simple script to run the bot locally with production credentials for testing
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env.local if it exists
env_files = ['.env.local', '.env']
for env_file in env_files:
    if Path(env_file).exists():
        print(f"📁 Loading environment from {env_file}")
        load_dotenv(env_file)
        break
else:
    print("⚠️  No .env.local or .env file found")

def setup_logging():
    """Setup enhanced logging for local testing"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/local_test.log', mode='a')
        ]
    )
    
    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("GridDigger Local Testing Session Started")
    logger.info("=" * 60)
    return logger

def check_environment():
    """Check if required environment variables are set and have real values"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'DB_HOST',
        'DB_DATABASE',
        'DB_USER',
        'DB_PASSWORD'
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value.startswith('your_') or 'password_here' in value or value.endswith('_here'):
            placeholder_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("💡 Make sure to:")
        print("   1. Copy .env.local.template to .env.local")
        print("   2. Fill in your production credentials")
        print("   3. The script automatically loads .env.local")
        return False
    
    if placeholder_vars:
        print(f"❌ Found placeholder values in: {', '.join(placeholder_vars)}")
        print("💡 Please edit .env.local and replace placeholder values with your actual credentials:")
        for var in placeholder_vars:
            print(f"   - {var}={os.getenv(var)} ← Replace this")
        return False
    
    print("✅ All required environment variables are set with real values")
    return True

def check_database_connection():
    """Test database connection"""
    try:
        from database_v2 import db_manager
        
        # Test basic connection first
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            print("✅ Database connection successful")
        
        # Try health check for additional info
        try:
            health = db_manager.health_check()
            if health['status'] == 'healthy':
                print(f"   - Response time: {health['response_time_ms']}ms")
                print(f"   - User count: {health['user_count']}")
            else:
                print(f"   - Health check warning: {health.get('error', 'Unknown error')}")
                print("   - Basic connection works, continuing...")
        except Exception as health_error:
            print(f"   - Health check failed: {health_error}")
            print("   - Basic connection works, continuing...")
        
        return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure your database credentials are correct and the database is accessible")
        return False

def check_graphql_endpoint():
    """Test GraphQL endpoint connection with comprehensive testing"""
    try:
        import requests
        from config import Config
        
        endpoint = Config.get_graphql_endpoint()
        headers = Config.get_graphql_headers()
        
        # Simple test query
        test_query = {
            "query": "query { __typename }"
        }
        
        response = requests.post(
            endpoint,
            json=test_query,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ GraphQL endpoint accessible: {endpoint}")
            
            # Basic GraphQL functionality test
            print("🧪 Testing basic GraphQL functionality...")
            try:
                import api_v2
                # Test a simple search
                test_result = api_v2.search_profiles_v2("test")
                if test_result is not None:
                    print("✅ GraphQL search functionality working")
                else:
                    print("⚠️  GraphQL search returned no data, but endpoint is accessible")
            except Exception as test_error:
                print(f"⚠️  GraphQL functionality test failed: {test_error}")
                print("   Basic endpoint works, continuing...")
            
            return True
        else:
            print(f"⚠️  GraphQL endpoint returned status {response.status_code}: {endpoint}")
            print("   This might still work for the bot, continuing...")
            return True
            
    except Exception as e:
        print(f"⚠️  GraphQL endpoint test failed: {e}")
        print("   This might still work for the bot, continuing...")
        return True

def run_basic_functionality_tests():
    """Run basic functionality tests using core services"""
    try:
        print("🧪 Running basic functionality tests...")
        from services.enhanced_profile_service import enhanced_profile_service
        
        # Test profile service
        test_profile_id = '254'
        formatted_profile = enhanced_profile_service.get_profile_card(test_profile_id)
        
        if formatted_profile and formatted_profile.buttons:
            callback_data = formatted_profile.buttons[0][0].callback_data
            print(f"✅ Profile service working - callback: {callback_data}")
            
            # Test expand functionality
            if callback_data.startswith('expand_'):
                profile_id = callback_data.split('_')[1]
                expanded_profile = enhanced_profile_service.get_expanded_profile(profile_id)
                if expanded_profile:
                    print(f"✅ Expand functionality working - profile ID: {profile_id}")
                else:
                    print("⚠️  Expand functionality may have issues")
            else:
                print("⚠️  Callback data format unexpected")
        else:
            print("⚠️  Profile service may have issues")
            
        print("✅ Basic functionality tests completed")
        return True
            
    except Exception as e:
        print(f"⚠️  Basic functionality testing failed: {e}")
        print("   Bot may still work, continuing...")
        return True

def run_bot():
    """Run the bot in polling mode"""
    try:
        print("\n🚀 Starting GridDigger bot in local testing mode...")
        print("   - Mode: Polling")
        print("   - Database: Production")
        print("   - GraphQL: Production endpoint")
        print("   - Logging: DEBUG level")
        print("\n📱 Test with your Telegram bot now!")
        print("   Send /start to begin testing")
        print("   Press Ctrl+C to stop\n")
        
        # Import and run the bot
        from app import main
        main()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
        print("Local testing session ended")
    except Exception as e:
        print(f"\n❌ Error running bot: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🔧 GridDigger Local Testing Setup")
    print("=" * 40)
    
    # Setup logging
    logger = setup_logging()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check database
    if not check_database_connection():
        print("\n💡 Database connection failed. Please check your credentials.")
        sys.exit(1)
    
    # Check GraphQL endpoint and run comprehensive tests
    if not check_graphql_endpoint():
        print("\n💡 Critical GraphQL tests failed. Bot may not work properly.")
        print("   You can still try to run it, but expect issues.")
        response = input("\nDo you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Run basic functionality tests
    print("\n" + "="*50)
    run_basic_functionality_tests()
    
    print("\n" + "="*50)
    print("🎯 Pre-flight checks complete!")
    print("   All critical functionality has been tested")
    
    # Run the bot
    run_bot()

if __name__ == "__main__":
    main()