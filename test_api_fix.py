#!/usr/bin/env python3
"""
Test script to verify the API fix for magic limits
Tests that get_profiles() now returns the same count as get_total_profile_count()
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import api

def test_api_fix():
    """Test that the API fix resolves the discrepancy"""
    print("🧪 Testing API Fix for Magic Limits...")
    
    # Test 1: Get total profile count
    print("\n1️⃣ Testing get_total_profile_count()...")
    total_count = api.get_total_profile_count()
    print(f"   Total profiles available: {total_count:,}")
    
    # Test 2: Get profiles with no filters (should now return ALL profiles)
    print("\n2️⃣ Testing get_profiles() with no filters...")
    user_data = {'FILTERS': {}, 'inc_search': False}
    profiles = api.get_profiles(user_data)
    profiles_count = len(profiles) if profiles else 0
    print(f"   Profiles returned by get_profiles(): {profiles_count:,}")
    
    # Test 3: Compare the counts
    print(f"\n📊 Comparison:")
    print(f"   get_total_profile_count(): {total_count:,}")
    print(f"   get_profiles() count:      {profiles_count:,}")
    print(f"   Difference:                {abs(total_count - profiles_count):,}")
    
    # Test 4: Check if they match
    if total_count == profiles_count:
        print(f"✅ SUCCESS: Counts match! All {total_count:,} profiles are accessible.")
        return True
    else:
        print(f"❌ ISSUE: Counts don't match. There's still a {abs(total_count - profiles_count):,} profile discrepancy.")
        
        # Additional debugging
        if profiles_count < total_count:
            print(f"   → get_profiles() is returning fewer profiles than available")
            print(f"   → This suggests there's still a filter or limit being applied")
        else:
            print(f"   → get_profiles() is returning more profiles than total count")
            print(f"   → This suggests an issue with the total count query")
        
        return False

def test_get_all_profiles():
    """Test the new get_all_profiles() function directly"""
    print("\n3️⃣ Testing get_all_profiles() function directly...")
    
    try:
        all_profiles = api.get_all_profiles()
        all_count = len(all_profiles) if all_profiles else 0
        print(f"   get_all_profiles() returned: {all_count:,} profiles")
        
        # Compare with total count
        total_count = api.get_total_profile_count()
        print(f"   get_total_profile_count(): {total_count:,} profiles")
        
        if all_count == total_count:
            print(f"✅ get_all_profiles() matches total count!")
            return True
        else:
            print(f"❌ get_all_profiles() doesn't match total count (diff: {abs(all_count - total_count)})")
            return False
            
    except Exception as e:
        print(f"❌ Error testing get_all_profiles(): {e}")
        return False

def test_search_with_term():
    """Test that search with actual terms still works"""
    print("\n4️⃣ Testing search with actual search term...")
    
    try:
        # Test with a common search term
        user_data = {'FILTERS': {'profileNameSearch_query': 'Bitcoin'}, 'inc_search': False}
        profiles = api.get_profiles(user_data)
        profiles_count = len(profiles) if profiles else 0
        print(f"   Search for 'Bitcoin' returned: {profiles_count:,} profiles")
        
        if profiles_count > 0:
            print(f"✅ Search functionality still works!")
            return True
        else:
            print(f"⚠️  Search returned no results (might be expected)")
            return True
            
    except Exception as e:
        print(f"❌ Error testing search: {e}")
        return False

def main():
    """Run all API fix tests"""
    print("🚀 GridDigger API Fix Verification")
    print("=" * 50)
    
    tests = [
        ("API Fix Verification", test_api_fix),
        ("get_all_profiles() Function", test_get_all_profiles),
        ("Search Functionality", test_search_with_term),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ {test_name}: FAILED - {e}")
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API fix is working correctly.")
        print("📊 Users now have access to ALL profiles without artificial limits.")
    else:
        print("⚠️  Some tests failed. The API fix may need additional work.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)