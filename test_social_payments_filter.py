#!/usr/bin/env python3

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import api

def test_social_payments_filter():
    """Test the specific Social Payments filter that the user reported"""
    
    print("🔍 Testing Social Payments Filter")
    print("=" * 50)
    
    # The correct ID for Social Payments from the test results
    social_payments_id = "id1752072092-lwEcx8nsSFij2fNjzESn7Q"
    
    print(f"Testing productTypes with Social Payments ID: {social_payments_id}")
    
    try:
        # Apply the filter using the API
        data = {
            "FILTERS": {
                "productTypes_query": social_payments_id
            },
            "inc_search": False
        }
        
        results = api.get_profiles(data)
        count = len(results) if results else 0
        
        if count > 0:
            print(f"✅ Found {count} results for Social Payments!")
            # Show first few results
            for i, profile in enumerate(results[:5]):
                print(f"   {i+1}. {profile.get('slug', 'N/A')} (ID: {profile.get('id', 'N/A')})")
            if count > 5:
                print(f"   ... and {count - 5} more")
        else:
            print("❌ No results found for Social Payments")
            
    except Exception as e:
        print(f"❌ Error: {e}")

    # Let's also test a few other product types with their correct IDs
    print(f"\n🔍 Testing other product types...")
    print("-" * 40)
    
    test_product_types = [
        ("AI Agent", "4220"),
        ("Game", "36"),
        ("DEX Aggregator", "26"),
        ("Decentralised Exchange", "25"),
        ("L1", "15"),
        ("L2", "16"),
    ]
    
    for product_name, product_id in test_product_types:
        try:
            data = {
                "FILTERS": {
                    "productTypes_query": product_id
                },
                "inc_search": False
            }
            
            results = api.get_profiles(data)
            count = len(results) if results else 0
            print(f"   {product_name} (ID: {product_id}): {count} results")
            
        except Exception as e:
            print(f"   {product_name} (ID: {product_id}): Error - {e}")

if __name__ == "__main__":
    test_social_payments_filter()