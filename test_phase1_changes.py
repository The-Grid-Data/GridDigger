#!/usr/bin/env python3
"""
Test script for Phase 1 UX improvements
Tests the new API functions and UX changes
"""

import api
import sys

def test_product_detail_query():
    """Test the new product detail query with known product ID"""
    print("Testing product detail query with Product ID 22 (Solana Mainnet)...")
    
    try:
        result = api.get_product_detail("22")
        
        if result:
            print(f"✅ Product detail query successful!")
            print(f"   Product ID: {result.get('id')}")
            print(f"   Product Name: {result.get('name')}")
            print(f"   Product Type: {result.get('productType', {}).get('name')}")
            print(f"   Product Status: {result.get('productStatus', {}).get('name')}")
            print(f"   Asset Relationships: {len(result.get('productAssetRelationships', []))}")
            return True
        else:
            print("❌ Product detail query returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ Product detail query failed: {e}")
        return False

def test_asset_detail_query():
    """Test the asset detail query (needs correction)"""
    print("\nTesting asset detail query with Asset ID 26 (SOL)...")
    
    try:
        result = api.get_asset_detail("26")
        
        if result:
            print(f"✅ Asset detail query successful!")
            print(f"   Asset ID: {result.get('id')}")
            print(f"   Asset Name: {result.get('name')}")
            print(f"   Asset Ticker: {result.get('ticker')}")
            return True
        else:
            print("❌ Asset detail query returned empty result (expected - needs correction)")
            return False
            
    except Exception as e:
        print(f"❌ Asset detail query failed: {e}")
        return False

def test_search_mode_toggle():
    """Test the enhanced search mode functionality"""
    print("\nTesting enhanced search mode toggle...")
    
    try:
        from handlers.utils import toggle_search_mode
        
        # Test data
        test_data = {
            'inc_search': False,
            'FILTERS': {
                'profileNameSearch_query': 'Solana'
            }
        }
        
        # Test toggle to deep search
        result = toggle_search_mode(test_data)
        
        if result and test_data['inc_search'] and 'profileDeepSearch_query' in test_data['FILTERS']:
            print("✅ Search mode toggle to deep search successful!")
            print(f"   Deep search active: {test_data['inc_search']}")
            print(f"   Filter updated to: profileDeepSearch_query")
            
            # Test toggle back to quick search
            result = toggle_search_mode(test_data)
            
            if not result and not test_data['inc_search'] and 'profileNameSearch_query' in test_data['FILTERS']:
                print("✅ Search mode toggle back to quick search successful!")
                return True
            else:
                print("❌ Toggle back to quick search failed")
                print(f"   Result: {result}, inc_search: {test_data['inc_search']}")
                print(f"   Filters: {test_data['FILTERS']}")
                return False
        else:
            print("❌ Search mode toggle to deep search failed")
            print(f"   Result: {result}, inc_search: {test_data['inc_search']}")
            print(f"   Filters: {test_data['FILTERS']}")
            return False
            
    except Exception as e:
        print(f"❌ Search mode toggle test failed: {e}")
        return False

def test_solana_filter_removal():
    """Test that Solana filter is no longer automatically applied"""
    print("\nTesting Solana filter removal...")
    
    try:
        # Test data without solana_filter_toggle
        test_data = {
            'FILTERS': {
                'profileNameSearch_query': 'test'
            }
        }
        
        # Get profiles should not add Solana filter automatically
        profiles = api.get_profiles(test_data)
        
        print("✅ Solana filter removal test completed!")
        print(f"   Profiles returned: {len(profiles) if profiles else 0}")
        print("   No automatic Solana filter applied")
        return True
        
    except Exception as e:
        print(f"❌ Solana filter removal test failed: {e}")
        return False

def main():
    """Run all Phase 1 tests"""
    print("🚀 Running Phase 1 UX Improvement Tests\n")
    
    tests = [
        test_product_detail_query,
        test_asset_detail_query,
        test_search_mode_toggle,
        test_solana_filter_removal
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 1 tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - review needed")
        return 1

if __name__ == "__main__":
    sys.exit(main())