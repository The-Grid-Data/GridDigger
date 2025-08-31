#!/usr/bin/env python3
"""
Simple webhook test script for local testing
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv('.env')

def test_webhook_server():
    """Test the webhook server endpoints"""
    base_url = os.getenv('WEBHOOK_URL', 'http://localhost:5000')
    token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    print(f"🧪 Testing webhook server at {base_url}")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Webhook configured: {data.get('webhook_configured')}")
            print(f"   Bot loop running: {data.get('bot_loop_running')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test webhook endpoint with a sample update
    try:
        webhook_url = f"{base_url}/{token}"
        sample_update = {
            "update_id": 12345,
            "message": {
                "message_id": 1,
                "date": 1234567890,
                "chat": {
                    "id": 123456789,
                    "type": "private"
                },
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "Test"
                },
                "text": "/start"
            }
        }
        
        response = requests.post(
            webhook_url,
            json=sample_update,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Webhook endpoint test passed")
            print(f"   Response: {data.get('status')}")
        else:
            print(f"❌ Webhook endpoint test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook endpoint error: {e}")
        return False
    
    print("🎉 All webhook tests passed!")
    return True

if __name__ == "__main__":
    print("🔧 Webhook Server Test")
    print("=" * 30)
    print("Make sure the webhook server is running first:")
    print("  python run_local.py  (with MODE=webhook)")
    print()
    
    input("Press Enter when the server is running...")
    test_webhook_server()