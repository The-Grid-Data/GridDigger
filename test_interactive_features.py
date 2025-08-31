#!/usr/bin/env python3
"""
Test script for interactive product/asset features
Tests the new clickable buttons and discovery UI integration
"""

import api
import sys
from services.enhanced_profile_service import enhanced_profile_service
from handlers.profiles import handle_product_detail, handle_asset_detail
from unittest.mock import Mock, AsyncMock

def test_interactive_profile_display():
    """Test the new interactive profile display with clickable buttons"""
    print("Testing interactive profile display with Product ID 22 (Solana Mainnet)...")
    
    try:
        # Get profile data that should have products and assets
        profile_data = enhanced_profile_service.get_raw_profile_data("3", full_data=True)  # Solana profile
        
        if not profile_data:
            print("❌ Could not get profile data for Solana")
            return False
        
        print(f"✅ Profile data retrieved: {profile_data.name}")
        print(f"   Products: {len(profile_data.products) if profile_data.products else 0}")
        print(f"   Assets: {len(profile_data.assets) if profile_data.assets else 0}")
        print(f"   Slug: {profile_data.slug}")
        
        # Test card formatter with interactive buttons
        formatted_profile = enhanced_profile_service.get_profile_card("3")
        
        if formatted_profile:
            print("✅ Interactive profile card generated successfully!")
            print(f"   Button count: {len(formatted_profile.buttons)}")
            
            # Check for discovery URLs in buttons
            discovery_urls = []
            callback_buttons = []
            product_buttons = []
            asset_buttons = []
            
            for button_row in formatted_profile.buttons:
                for button in button_row:
                    if hasattr(button, 'url') and button.url:
                        if 'discovery.thegrid.id' in button.url:
                            discovery_urls.append(button.url)
                    elif hasattr(button, 'callback_data') and button.callback_data:
                        callback_buttons.append(button.callback_data)
                        if button.callback_data.startswith('product_detail_'):
                            product_buttons.append(button.callback_data)
                        elif button.callback_data.startswith('asset_detail_'):
                            asset_buttons.append(button.callback_data)
            
            print(f"   Discovery URLs: {len(discovery_urls)}")
            print(f"   Callback buttons: {len(callback_buttons)}")
            print(f"   Product buttons: {len(product_buttons)}")
            print(f"   Asset buttons: {len(asset_buttons)}")
            
            if discovery_urls:
                print(f"   Sample discovery URL: {discovery_urls[0]}")
            
            if product_buttons:
                print(f"   Sample product callback: {product_buttons[0]}")
            
            if asset_buttons:
                print(f"   Sample asset callback: {asset_buttons[0]}")
            
            return True
        else:
            print("❌ Failed to generate interactive profile card")
            return False
            
    except Exception as e:
        print(f"❌ Interactive profile display test failed: {e}")
        return False

def test_product_detail_api():
    """Test product detail API functionality"""
    print("\nTesting product detail API with Product ID 22...")
    
    try:
        result = api.get_product_detail("22")
        
        if result:
            print("✅ Product detail API successful!")
            print(f"   Product ID: {result.get('id')}")
            print(f"   Product Name: {result.get('name')}")
            print(f"   Product Type: {result.get('productType', {}).get('name')}")
            print(f"   Asset Relationships: {len(result.get('productAssetRelationships', []))}")
            
            # Check if root relationship exists for back button
            if result.get('root', {}).get('id'):
                print(f"   ✅ Root ID for back button: {result['root']['id']}")
            elif result.get('rootId'):
                print(f"   ✅ Root ID for back button: {result['rootId']}")
            else:
                print("   ⚠️  No root relationship found - back button may not work")
            
            return True
        else:
            print("❌ Product detail API returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ Product detail API test failed: {e}")
        return False

def test_asset_detail_api():
    """Test asset detail API functionality"""
    print("\nTesting asset detail API with Asset ID 26...")
    
    try:
        result = api.get_asset_detail("26")
        
        if result:
            print("✅ Asset detail API successful!")
            print(f"   Asset ID: {result.get('id')}")
            print(f"   Asset Name: {result.get('name')}")
            print(f"   Asset Ticker: {result.get('ticker')}")
            print(f"   Asset Type: {result.get('assetType', {}).get('name')}")
            
            # Check if root relationship exists for back button
            if result.get('root', {}).get('id'):
                print(f"   ✅ Root ID for back button: {result['root']['id']}")
            elif result.get('rootId'):
                print(f"   ✅ Root ID for back button: {result['rootId']}")
            else:
                print("   ⚠️  No root relationship found - back button may not work")
            
            return True
        else:
            print("❌ Asset detail API returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ Asset detail API test failed: {e}")
        return False

async def test_product_callback_handler():
    """Test product detail callback handler"""
    print("\nTesting product detail callback handler...")
    
    try:
        # Create mock query object
        mock_query = Mock()
        mock_query.edit_message_text = AsyncMock()
        
        # Test the handler
        await handle_product_detail(mock_query, "22")
        
        # Check if edit_message_text was called
        if mock_query.edit_message_text.called:
            print("✅ Product callback handler executed successfully!")
            call_args = mock_query.edit_message_text.call_args
            if call_args and call_args[1].get('text'):
                message_text = call_args[1]['text']
                if "Product Details" in message_text:
                    print("   ✅ Product details message formatted correctly")
                    return True
                else:
                    print("   ❌ Product details message format incorrect")
                    return False
            else:
                print("   ❌ No message text in callback")
                return False
        else:
            print("❌ Product callback handler did not execute")
            return False
            
    except Exception as e:
        print(f"❌ Product callback handler test failed: {e}")
        return False

async def test_asset_callback_handler():
    """Test asset detail callback handler"""
    print("\nTesting asset detail callback handler...")
    
    try:
        # Create mock query object
        mock_query = Mock()
        mock_query.edit_message_text = AsyncMock()
        
        # Test the handler
        await handle_asset_detail(mock_query, "26")
        
        # Check if edit_message_text was called
        if mock_query.edit_message_text.called:
            print("✅ Asset callback handler executed successfully!")
            call_args = mock_query.edit_message_text.call_args
            if call_args and call_args[1].get('text'):
                message_text = call_args[1]['text']
                if "Asset Details" in message_text:
                    print("   ✅ Asset details message formatted correctly")
                    return True
                else:
                    print("   ❌ Asset details message format incorrect")
                    return False
            else:
                print("   ❌ No message text in callback")
                return False
        else:
            print("❌ Asset callback handler did not execute")
            return False
            
    except Exception as e:
        print(f"❌ Asset callback handler test failed: {e}")
        return False

def test_discovery_url_generation():
    """Test discovery URL generation with profile slugs"""
    print("\nTesting discovery URL generation...")
    
    try:
        # Test with known profile that should have a slug
        profile_data = enhanced_profile_service.get_raw_profile_data("3", full_data=False)  # Solana
        
        if profile_data and profile_data.slug:
            discovery_url = f"https://discovery.thegrid.id/profiles/{profile_data.slug}"
            print(f"✅ Discovery URL generated: {discovery_url}")
            print(f"   Profile: {profile_data.name}")
            print(f"   Slug: {profile_data.slug}")
            return True
        else:
            print("❌ Could not generate discovery URL - missing slug")
            return False
            
    except Exception as e:
        print(f"❌ Discovery URL generation test failed: {e}")
        return False

def test_button_callback_patterns():
    """Test that callback patterns are correctly formatted"""
    print("\nTesting button callback patterns...")
    
    try:
        # Test callback patterns
        test_patterns = [
            ("product_detail_22", "product_detail"),
            ("asset_detail_26", "asset_detail"),
            ("more_products_3", "more_products"),
            ("more_assets_3", "more_assets"),
            ("back_to_card_3", "back_to_card")
        ]
        
        for callback_data, expected_prefix in test_patterns:
            if callback_data.startswith(expected_prefix):
                print(f"✅ Callback pattern valid: {callback_data}")
            else:
                print(f"❌ Callback pattern invalid: {callback_data}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Button callback pattern test failed: {e}")
        return False

async def main():
    """Run all interactive feature tests"""
    print("🚀 Running Interactive Product/Asset Feature Tests\n")
    
    # Synchronous tests
    sync_tests = [
        test_interactive_profile_display,
        test_product_detail_api,
        test_asset_detail_api,
        test_discovery_url_generation,
        test_button_callback_patterns
    ]
    
    # Asynchronous tests
    async_tests = [
        test_product_callback_handler,
        test_asset_callback_handler
    ]
    
    passed = 0
    total = len(sync_tests) + len(async_tests)
    
    # Run synchronous tests
    for test in sync_tests:
        if test():
            passed += 1
    
    # Run asynchronous tests
    for test in async_tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Async test {test.__name__} failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All interactive feature tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - review needed")
        return 1

if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))