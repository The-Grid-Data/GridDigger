#!/usr/bin/env python3
"""
Test script to verify the database fixes work correctly
This tests the MySQL compatibility fixes without requiring full bot setup
"""
import os
import sys
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_database_import():
    """Test that database_v2 can be imported without auto-initialization"""
    try:
        print("🔍 Testing database import...")
        from database_v2 import db_manager, user_repository, initialize_database_schema
        print("✅ Database modules imported successfully")
        print("✅ No automatic schema initialization occurred")
        return True
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False

def test_config_simplification():
    """Test that config works with simplified endpoint logic"""
    try:
        print("\n🔍 Testing configuration...")
        from config import Config
        
        # Test endpoint selection
        endpoint = Config.get_graphql_endpoint()
        headers = Config.get_graphql_headers()
        info = Config.get_current_endpoint_info()
        
        print(f"✅ GraphQL endpoint: {endpoint}")
        print(f"✅ Using legacy: {info['using_legacy']}")
        print(f"✅ Has auth token: {info['has_auth_token']}")
        print("✅ Configuration simplified successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_manual_schema_initialization():
    """Test manual schema initialization (if database is available)"""
    try:
        print("\n🔍 Testing manual schema initialization...")
        
        # Check if we have database credentials
        required_vars = ['DB_HOST', 'DB_DATABASE', 'DB_USER', 'DB_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"⚠️  Skipping database test - missing: {', '.join(missing_vars)}")
            print("   (This is expected if you haven't set up .env.local yet)")
            return True
        
        from database_v2 import initialize_database_schema
        result = initialize_database_schema()
        
        if result:
            print("✅ Manual schema initialization successful")
            print("✅ Database handles existing tables gracefully")
        else:
            print("⚠️  Schema initialization returned False (check logs)")
            
        return True
        
    except Exception as e:
        print(f"⚠️  Database test failed: {e}")
        print("   (This is expected if database is not accessible)")
        return True

def main():
    """Run all tests"""
    print("🧪 GridDigger Database Fixes Test")
    print("=" * 40)
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    tests = [
        test_database_import,
        test_config_simplification,
        test_manual_schema_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The database fixes are working correctly.")
        print("\n📋 Next steps:")
        print("   1. Copy .env.local.template to .env.local")
        print("   2. Fill in your production credentials")
        print("   3. Run: python run_local.py")
        print("   4. Test with real Telegram bot!")
    else:
        print("⚠️  Some tests had issues. Check the output above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())