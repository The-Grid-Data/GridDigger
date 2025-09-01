#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api import apply_filters

def test_asset_filters():
    print("🔍 Testing Asset Filters")
    print("=" * 50)
    
    # Test different asset filter types
    test_cases = [
        ("assetTickers", "BTC"),
        ("assetTickers", "ETH"),
        ("assetTypes", "1"),  # Assuming numeric ID
        ("assetTypes", "id1234567890-abcdefg"),  # String ID with special chars
        ("assetStandards", "1"),  # Numeric ID
        ("assetStandards", "id1234567890-xyz123"),  # String ID
    ]
    
    for filter_name, value in test_cases:
        print(f"\nTesting {filter_name} with value: {value}")
        print("-" * 40)
        
        try:
            filters_list = [(filter_name, value)]
            print(f"DEBUG: filters_list = {filters_list}")
            
            result = apply_filters(filters_list)
            print(f"DEBUG: apply_filters returned = {type(result)}")
            
            if isinstance(result, dict) and 'data' in result and 'roots' in result['data']:
                roots_data = result['data']['roots']
                if roots_data is not None:
                    print(f"✅ Found {len(roots_data)} results for {filter_name}: {value}")
                    if len(roots_data) > 0:
                        for i, root in enumerate(roots_data[:3]):  # Show first 3
                            print(f"   {i+1}. {root.get('slug', 'N/A')} (ID: {root.get('id', 'N/A')})")
                        if len(roots_data) > 3:
                            print(f"   ... and {len(roots_data) - 3} more")
                    else:
                        print(f"✅ Found 0 results for {filter_name}: {value}")
                else:
                    print(f"⚠️  GraphQL returned null results for {filter_name}: {value}")
            else:
                print(f"❌ Unexpected result format: {result}")
                
        except Exception as e:
            print(f"❌ Error testing {filter_name} with {value}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_asset_filters()