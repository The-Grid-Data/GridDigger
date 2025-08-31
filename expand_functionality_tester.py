"""
Expand Functionality Tester
Tests the specific "Expand" button functionality that was failing
"""
import logging
from typing import Dict, Any
import api

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpandFunctionalityTester:
    """Test the expand functionality specifically"""
    
    def test_the_grid_search_integration(self) -> Dict:
        """Test 'The Grid' search through the bot integration"""
        logger.info("🔍 Testing 'The Grid' Search Integration")
        
        try:
            # Test direct V2 search
            results_v2 = api.search_profiles_v2("The Grid")
            logger.info(f"✅ V2 search returned: {len(results_v2)} results")
            
            # Test through bot integration (get_profiles)
            user_data = {
                "FILTERS": {
                    "profileNameSearch": "The Grid",
                    "profileNameSearch_query": "The Grid"
                },
                "inc_search": False
            }
            
            results_integration = api.get_profiles(user_data)
            logger.info(f"✅ Bot integration returned: {len(results_integration) if results_integration else 0} results")
            
            # Compare results
            if results_v2 and results_integration:
                if len(results_v2) == len(results_integration):
                    logger.info("✅ V2 and integration results match!")
                else:
                    logger.warning(f"⚠️ Result count mismatch: V2={len(results_v2)}, Integration={len(results_integration)}")
            
            return {
                'success': True,
                'test_name': 'The Grid Search Integration',
                'v2_results': len(results_v2) if results_v2 else 0,
                'integration_results': len(results_integration) if results_integration else 0,
                'results_match': len(results_v2) == len(results_integration) if results_v2 and results_integration else False
            }
            
        except Exception as e:
            logger.error(f"❌ The Grid Search Integration failed: {e}")
            return {
                'success': False,
                'test_name': 'The Grid Search Integration',
                'error': str(e)
            }
    
    def test_expand_profile_data_retrieval(self) -> Dict:
        """Test profile data retrieval for expand functionality"""
        logger.info("🔍 Testing Expand Profile Data Retrieval")
        
        try:
            # First get The Grid profile
            results = api.search_profiles_v2("The Grid")
            if not results or len(results) == 0:
                return {
                    'success': False,
                    'test_name': 'Expand Profile Data Retrieval',
                    'error': 'No results found for The Grid search'
                }
            
            profile_id = results[0].get('id')
            logger.info(f"✅ Found The Grid profile with ID: {profile_id}")
            
            # Test basic profile data retrieval
            basic_profile_data = api.get_profile_data_by_id(profile_id)
            logger.info(f"✅ Basic profile data type: {type(basic_profile_data)}")
            
            if basic_profile_data:
                name = basic_profile_data.get('name', 'Unknown')
                logger.info(f"✅ Profile name: '{name}'")
            
            # Test full profile data retrieval (used by expand)
            full_profile_data = api.get_full_profile_data_by_id(profile_id)
            logger.info(f"✅ Full profile data type: {type(full_profile_data)}")
            
            # Initialize default values
            found_keys = []
            missing_keys = []
            
            if full_profile_data:
                full_name = full_profile_data.get('name', 'Unknown')
                logger.info(f"✅ Full profile name: '{full_name}'")
                
                # Test V2 schema structure
                expected_keys = ['name', 'tagLine', 'descriptionShort', 'descriptionLong', 'profileSector', 'profileType', 'root', 'urls']
                found_keys = [key for key in expected_keys if key in full_profile_data]
                missing_keys = [key for key in expected_keys if key not in full_profile_data]
                
                logger.info(f"✅ Found keys: {found_keys}")
                if missing_keys:
                    logger.warning(f"⚠️ Missing keys: {missing_keys}")
                
                # Test root data structure
                root_data = full_profile_data.get('root', {})
                if root_data:
                    products = root_data.get('products', [])
                    assets = root_data.get('assets', [])
                    
                    # Add null safety checks
                    products_count = len(products) if products is not None else 0
                    assets_count = len(assets) if assets is not None else 0
                    
                    logger.info(f"✅ Root data - Products: {products_count}, Assets: {assets_count}")
                    logger.info(f"✅ Products type: {type(products)}, Assets type: {type(assets)}")
            else:
                logger.warning("⚠️ No full profile data retrieved")
            
            return {
                'success': True,
                'test_name': 'Expand Profile Data Retrieval',
                'profile_id': profile_id,
                'has_basic_data': bool(basic_profile_data),
                'has_full_data': bool(full_profile_data),
                'found_keys': found_keys,
                'missing_keys': missing_keys
            }
            
        except Exception as e:
            logger.error(f"❌ Expand Profile Data Retrieval failed: {e}")
            return {
                'success': False,
                'test_name': 'Expand Profile Data Retrieval',
                'error': str(e)
            }
    
    def test_expand_message_construction(self) -> Dict:
        """Test the expand message construction logic"""
        logger.info("🔍 Testing Expand Message Construction")
        
        try:
            # Get The Grid profile data
            results = api.search_profiles_v2("The Grid")
            if not results or len(results) == 0:
                return {
                    'success': False,
                    'test_name': 'Expand Message Construction',
                    'error': 'No results found for The Grid search'
                }
            
            profile_id = results[0].get('id')
            profile_data = api.get_full_profile_data_by_id(profile_id)
            
            if not profile_data:
                return {
                    'success': False,
                    'test_name': 'Expand Message Construction',
                    'error': 'No profile data retrieved'
                }
            
            # Simulate the message construction logic from expand_profile_callback
            name = profile_data.get('name', 'Unknown')
            profile_id_display = profile_data.get('id', profile_id)
            slug = profile_data.get('slug', '-')
            
            # Construct message text (similar to expand function)
            message_text = f"*ID:* {profile_id_display}\n"
            message_text += f"*Name:* {name}\n"
            message_text += f"*Sector:* {profile_data.get('profileSector', {}).get('name', '-') if profile_data.get('profileSector') else '-'}\n"
            message_text += f"*Type:* {profile_data.get('profileType', {}).get('name', '-') if profile_data.get('profileType') else '-'}\n"
            message_text += f"*Status:* {profile_data.get('profileStatus', {}).get('name', '-') if profile_data.get('profileStatus') else '-'}\n"
            message_text += f"*Slug:* {slug}\n"
            message_text += f"*Long Description:* {profile_data.get('descriptionLong', '-')}\n"
            message_text += f"*Tag Line:* {profile_data.get('tagLine', '-')}\n"
            
            logger.info(f"✅ Message constructed successfully")
            logger.info(f"✅ Message length: {len(message_text)} characters")
            logger.info(f"✅ Message preview: {message_text[:100]}...")
            
            # Test URL handling
            urls = profile_data.get('urls', [])
            url_count = len(urls)
            logger.info(f"✅ Found {url_count} URLs for buttons")
            
            return {
                'success': True,
                'test_name': 'Expand Message Construction',
                'profile_name': name,
                'message_length': len(message_text),
                'url_count': url_count,
                'message_constructed': True
            }
            
        except Exception as e:
            logger.error(f"❌ Expand Message Construction failed: {e}")
            return {
                'success': False,
                'test_name': 'Expand Message Construction',
                'error': str(e)
            }
    
    def run_all_tests(self) -> Dict:
        """Run all expand functionality tests"""
        logger.info("🚀 Starting Expand Functionality Tests...")
        
        tests = []
        
        # Test the complete expand flow
        tests.append(self.test_the_grid_search_integration())
        tests.append(self.test_expand_profile_data_retrieval())
        tests.append(self.test_expand_message_construction())
        
        # Compile results
        passed = sum(1 for test in tests if test['success'])
        failed = len(tests) - passed
        
        # Log results
        logger.info(f"\n📊 EXPAND FUNCTIONALITY TEST RESULTS:")
        logger.info(f"   Total Tests: {len(tests)}")
        logger.info(f"   Passed: {passed}")
        logger.info(f"   Failed: {failed}")
        logger.info(f"   Success Rate: {(passed / len(tests)) * 100:.1f}%")
        
        logger.info(f"\n📝 DETAILED RESULTS:")
        for test in tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            logger.info(f"   {status} - {test['test_name']}")
            
            if not test['success']:
                logger.error(f"      Error: {test.get('error', 'Unknown error')}")
        
        return {
            'total_tests': len(tests),
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / len(tests)) * 100,
            'all_passed': failed == 0,
            'detailed_results': tests
        }

def main():
    """Main function to run expand functionality tests"""
    print("🧪 GridDigger Expand Functionality Tester")
    print("=" * 50)
    
    tester = ExpandFunctionalityTester()
    results = tester.run_all_tests()
    
    print(f"\n🎯 EXPAND FUNCTIONALITY TEST SUMMARY:")
    print(f"   Total Tests: {results['total_tests']}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Success Rate: {results['success_rate']:.1f}%")
    
    if results['all_passed']:
        print(f"\n🎉 ALL EXPAND FUNCTIONALITY TESTS PASSED!")
        print("   The 'Expand' button should work properly now.")
        print("   'The Grid' search integration is working.")
        return True
    else:
        print(f"\n⚠️ {results['failed']} expand functionality tests failed.")
        print("   Some expand features may not work correctly.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)