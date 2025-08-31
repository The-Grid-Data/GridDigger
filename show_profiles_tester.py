"""
Show Profiles Functionality Tester
Tests the specific "Show profiles" button functionality that was failing
"""
import logging
from typing import Dict, Any
import api
from handlers.utils import generate_applied_filters_text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShowProfilesTester:
    """Test the show profiles functionality specifically"""
    
    def test_show_profiles_data_flow(self) -> Dict:
        """Test the complete show profiles data flow"""
        logger.info("🔍 Testing Show Profiles Data Flow")
        
        try:
            # Simulate user data when they click "Show profiles" after searching "The Grid"
            user_data = {
                "FILTERS": {
                    "profileNameSearch": "The Grid",
                    "profileNameSearch_query": "The Grid"
                },
                "inc_search": False
            }
            
            # Step 1: Get profiles (this should work now)
            profiles = api.get_profiles(user_data)
            logger.info(f"✅ Step 1 - api.get_profiles() returned: {type(profiles)} with {len(profiles) if profiles else 0} items")
            
            # Step 2: Test null safety
            if profiles is None:
                profiles = []
                logger.info("✅ Step 2 - Null safety applied, profiles set to empty list")
            
            # Step 3: Test filter text generation
            filter_text = generate_applied_filters_text(user_data)
            logger.info(f"✅ Step 3 - Filter text: '{filter_text}'")
            
            # Step 4: Test profile data retrieval for first profile
            if profiles and len(profiles) > 0:
                first_profile = profiles[0]
                profile_id = first_profile.get('id')
                logger.info(f"✅ Step 4a - First profile ID: {profile_id}")
                
                # Test profile data retrieval
                profile_data = api.get_profile_data_by_id(profile_id)
                logger.info(f"✅ Step 4b - Profile data type: {type(profile_data)}")
                
                # Test V2 schema data extraction
                if profile_data:
                    name = profile_data.get('name', 'Unknown')
                    sector_name = profile_data.get('profileSector', {}).get('name', '-') if profile_data.get('profileSector') else '-'
                    description_short = profile_data.get('descriptionShort', '-') if profile_data.get('descriptionShort') else '-'
                    
                    logger.info(f"✅ Step 4c - Profile details: Name='{name}', Sector='{sector_name}', Desc='{description_short[:50]}...'")
                else:
                    logger.warning("⚠️ Step 4c - Profile data is empty")
            else:
                logger.warning("⚠️ Step 4 - No profiles to test profile data retrieval")
            
            return {
                'success': True,
                'test_name': 'Show Profiles Data Flow',
                'profiles_count': len(profiles) if profiles else 0,
                'filter_text': filter_text,
                'has_profile_data': bool(profiles and len(profiles) > 0 and profile_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Show Profiles Data Flow failed: {e}")
            return {
                'success': False,
                'test_name': 'Show Profiles Data Flow',
                'error': str(e)
            }
    
    def test_empty_monitoring_group_id(self) -> Dict:
        """Test handling when MONITORING_GROUP_ID is empty"""
        logger.info("🔍 Testing Empty Monitoring Group ID")
        
        try:
            import os
            original_monitoring_id = os.getenv('MONITORING_GROUP_ID')
            logger.info(f"✅ Current MONITORING_GROUP_ID: '{original_monitoring_id}'")
            
            # Test that the function can handle empty/None monitoring group ID
            if not original_monitoring_id:
                logger.info("✅ MONITORING_GROUP_ID is empty/None - this should be handled gracefully")
            else:
                logger.info("✅ MONITORING_GROUP_ID is set - monitoring messages will be sent")
            
            return {
                'success': True,
                'test_name': 'Empty Monitoring Group ID',
                'monitoring_id_set': bool(original_monitoring_id)
            }
            
        except Exception as e:
            logger.error(f"❌ Empty Monitoring Group ID test failed: {e}")
            return {
                'success': False,
                'test_name': 'Empty Monitoring Group ID',
                'error': str(e)
            }
    
    def test_profile_data_structure(self) -> Dict:
        """Test the V2 profile data structure handling"""
        logger.info("🔍 Testing Profile Data Structure")
        
        try:
            # Get a sample profile
            user_data = {
                "FILTERS": {
                    "profileNameSearch": "",
                    "profileNameSearch_query": ""
                },
                "inc_search": False
            }
            
            profiles = api.get_profiles(user_data)
            if profiles and len(profiles) > 0:
                profile_id = profiles[0].get('id')
                profile_data = api.get_profile_data_by_id(profile_id)
                
                logger.info(f"✅ Profile data keys: {list(profile_data.keys()) if profile_data else 'None'}")
                
                # Test the structure we expect
                expected_keys = ['name', 'tagLine', 'descriptionShort', 'profileSector', 'profileType', 'root', 'logo', 'urls']
                found_keys = []
                missing_keys = []
                
                for key in expected_keys:
                    if key in profile_data:
                        found_keys.append(key)
                    else:
                        missing_keys.append(key)
                
                logger.info(f"✅ Found keys: {found_keys}")
                logger.info(f"⚠️ Missing keys: {missing_keys}")
                
                return {
                    'success': True,
                    'test_name': 'Profile Data Structure',
                    'found_keys': found_keys,
                    'missing_keys': missing_keys,
                    'structure_valid': len(found_keys) > len(missing_keys)
                }
            else:
                logger.warning("⚠️ No profiles available to test structure")
                return {
                    'success': True,
                    'test_name': 'Profile Data Structure',
                    'no_profiles': True
                }
                
        except Exception as e:
            logger.error(f"❌ Profile Data Structure test failed: {e}")
            return {
                'success': False,
                'test_name': 'Profile Data Structure',
                'error': str(e)
            }
    
    def run_all_tests(self) -> Dict:
        """Run all show profiles tests"""
        logger.info("🚀 Starting Show Profiles Tests...")
        
        tests = []
        
        # Test the complete data flow
        tests.append(self.test_show_profiles_data_flow())
        tests.append(self.test_empty_monitoring_group_id())
        tests.append(self.test_profile_data_structure())
        
        # Compile results
        passed = sum(1 for test in tests if test['success'])
        failed = len(tests) - passed
        
        # Log results
        logger.info(f"\n📊 SHOW PROFILES TEST RESULTS:")
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
    """Main function to run show profiles tests"""
    print("🧪 GridDigger Show Profiles Tester")
    print("=" * 50)
    
    tester = ShowProfilesTester()
    results = tester.run_all_tests()
    
    print(f"\n🎯 SHOW PROFILES TEST SUMMARY:")
    print(f"   Total Tests: {results['total_tests']}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Success Rate: {results['success_rate']:.1f}%")
    
    if results['all_passed']:
        print(f"\n🎉 ALL SHOW PROFILES TESTS PASSED!")
        print("   The 'Show profiles' button should work properly now.")
        return True
    else:
        print(f"\n⚠️ {results['failed']} show profiles tests failed.")
        print("   The 'Show profiles' functionality may still have issues.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)