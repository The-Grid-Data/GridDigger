#!/usr/bin/env python3

import sys
import os
import json
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import api
from config import Config

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def test_product_filters():
    """Test product filters specifically"""
    
    print("🔍 Testing Product Filters")
    print("=" * 50)
    
    # Test cases for product filters
    test_cases = [
        # Test productTypes filter with different values
        ("productTypes", "1"),  # Try ID 1
        ("productTypes", "2"),  # Try ID 2
        ("productTypes", "3"),  # Try ID 3
        ("productTypes", "4"),  # Try ID 4
        ("productTypes", "5"),  # Try ID 5
        ("productStatuses", "1"),  # Try product status
        ("productStatuses", "2"),  # Try product status
    ]
    
    for filter_name, value in test_cases:
        print(f"\n🧪 Testing {filter_name} = {value}")
        print("-" * 30)
        
        try:
            # Apply the filter using the API
            data = {
                "FILTERS": {
                    f"{filter_name}_query": value
                },
                "inc_search": False
            }
            
            results = api.get_profiles(data)
            count = len(results) if results else 0
            
            if count > 0:
                print(f"✅ Found {count} results")
                # Show first few results
                for i, profile in enumerate(results[:3]):
                    print(f"   {i+1}. {profile.get('slug', 'N/A')} (ID: {profile.get('id', 'N/A')})")
                if count > 3:
                    print(f"   ... and {count - 3} more")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Now let's check what product types are available
    print(f"\n🔍 Checking available product types...")
    print("-" * 40)
    
    try:
        # Get available product types using the API
        options = api.fetch_filter_options(api.filters_config["filters_queries"]["productTypes"])
        if options:
            print(f"Available Product Types ({len(options)}):")
            for pt in options:
                print(f"   ID {pt['id']}: {pt['name']}")
        else:
            print("❌ Could not fetch product types")
            
    except Exception as e:
        print(f"❌ Error fetching product types: {e}")
    
    # Check product statuses too
    print(f"\n🔍 Checking available product statuses...")
    print("-" * 40)
    
    try:
        # Get available product statuses using the API
        options = api.fetch_filter_options(api.filters_config["filters_queries"]["productStatuses"])
        if options:
            print(f"Available Product Statuses ({len(options)}):")
            for ps in options:
                print(f"   ID {ps['id']}: {ps['name']}")
        else:
            print("❌ Could not fetch product statuses")
            
    except Exception as e:
        print(f"❌ Error fetching product statuses: {e}")

    # Let's also check if there are any profiles with products at all
    print(f"\n🔍 Checking profiles with products...")
    print("-" * 40)
    
    try:
        # Test with no filters to see if we can get any profiles
        data = {"FILTERS": {}, "inc_search": False}
        all_profiles = api.get_profiles(data)
        
        if all_profiles:
            print(f"Total profiles available: {len(all_profiles)}")
            
            # Check a few profiles to see if they have products
            profiles_with_products = []
            for profile in all_profiles[:20]:  # Check first 20 profiles
                if 'products' in profile and profile['products']:
                    profiles_with_products.append(profile)
            
            print(f"Profiles with products (from first 20): {len(profiles_with_products)}")
            for profile in profiles_with_products[:5]:  # Show first 5
                print(f"   {profile['slug']} (ID: {profile['id']})")
                for product in profile.get('products', [])[:2]:  # Show first 2 products
                    pt = product.get('productType', {})
                    ps = product.get('productStatus', {})
                    print(f"     - Product ID {product.get('id', 'N/A')}: Type={pt.get('name', 'N/A')} (ID: {pt.get('id', 'N/A')}), Status={ps.get('name', 'N/A')} (ID: {ps.get('id', 'N/A')})")
        else:
            print("❌ No profiles found at all")
            
    except Exception as e:
        print(f"❌ Error fetching profiles: {e}")

if __name__ == "__main__":
    test_product_filters()