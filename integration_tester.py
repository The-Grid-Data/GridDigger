"""
Integration Tester for GridDigger Bot Logic
Tests the complete user interaction flow including filtering and profile display
"""
import logging
from typing import Dict, List, Any
import api
from handlers.utils import generate_applied_filters_text, create_main_menu_filter_keyboard

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationTester:
    """Test complete user interaction flows"""
    
    def __init__(self):
        self.test_results = []
    
    def test_basic_search_flow(self) -> Dict:
        """Test the basic search flow that was failing"""
        logger.info("🔍 Testing Basic Search Flow (User types 'Solana')")
        
        try:
            # Simulate user data when they type "Solana"
            user_data = {
                "FILTERS": {
                    "profileNameSearch": "Solana",
                    "profileNameSearch_query": "Solana"
                },
                "inc_search": False
            }
            
            # Test the exact call that was failing
            results = api.get_profiles(user_data)
            logger.info(f"✅ api.get_profiles() returned: {type(results)} with {len(results) if results else 0} items")
            
            # Test null safety
            results_count = len(results) if results is not None else 0
            logger.info(f"✅ Null-safe len() call: {results_count}")
            
            # Test filter text generation
            filter_text = generate_applied_filters_text(user_data)
            logger.info(f"✅ Filter text generated: '{filter_text}'")
            
            # Test keyboard creation
            keyboard = create_main_menu_filter_keyboard(user_data, results_count)
            logger.info(f"✅ Keyboard created with {len(keyboard.inline_keyboard)} rows")
            
            return {
                'success': True,
                'test_name': 'Basic Search Flow',
                'results_count': results_count,
                'results_type': type(results).__name__,
                'filter_text': filter_text,
                'keyboard_rows': len(keyboard.inline_keyboard)
            }
            
        except Exception as e:
            logger.error(f"❌ Basic Search Flow failed: {e}")
            return {
                'success': False,
                'test_name': 'Basic Search Flow',
                'error': str(e)
            }
    
    def test_empty_search_flow(self) -> Dict:
        """Test empty search handling"""
        logger.info("🔍 Testing Empty Search Flow")
        
        try:
            # Simulate user data with empty search
            user_data = {
                "FILTERS": {
                    "profileNameSearch": "",
                    "profileNameSearch_query": ""
                },
                "inc_search": False
            }
            
            results = api.get_profiles(user_data)
            results_count = len(results) if results is not None else 0
            
            logger.info(f"✅ Empty search returned {results_count} results")
            
            return {
                'success': True,
                'test_name': 'Empty Search Flow',
                'results_count': results_count,
                'results_type': type(results).__name__
            }
            
        except Exception as e:
            logger.error(f"❌ Empty Search Flow failed: {e}")
            return {
                'success': False,
                'test_name': 'Empty Search Flow',
                'error': str(e)
            }
    
    def test_no_results_flow(self) -> Dict:
        """Test handling when no results are found"""
        logger.info("🔍 Testing No Results Flow")
        
        try:
            # Simulate user data with search that should return no results
            user_data = {
                "FILTERS": {
                    "profileNameSearch": "XYZ123NONEXISTENT",
                    "profileNameSearch_query": "XYZ123NONEXISTENT"
                },
                "inc_search": False
            }
            
            results = api.get_profiles(user_data)
            results_count = len(results) if results is not None else 0
            
            logger.info(f"✅ No results search returned {results_count} results")
            
            return {
                'success': True,
                'test_name': 'No Results Flow',
                'results_count': results_count,
                'results_type': type(results).__name__
            }
            
        except Exception as e:
            logger.error(f"❌ No Results Flow failed: {e}")
            return {
                'success': False,
                'test_name': 'No Results Flow',
                'error': str(e)
            }
    
    def test_filter_combinations(self) -> Dict:
        """Test multiple filter combinations"""
        logger.info("🔍 Testing Filter Combinations")
        
        try:
            # Simulate user data with multiple filters
            user_data = {
                "FILTERS": {
                    "profileNameSearch": "The Grid",
                    "profileNameSearch_query": "The Grid",
                    "profileType_query": "1",
                    "profileType": "Protocol"
                },
                "inc_search": False,
                "solana_filter_toggle": True
            }
            
            results = api.get_profiles(user_data)
            results_count = len(results) if results is not None else 0
            
            logger.info(f"✅ Filter combination returned {results_count} results")
            
            return {
                'success': True,
                'test_name': 'Filter Combinations',
                'results_count': results_count,
                'results_type': type(results).__name__
            }
            
        except Exception as e:
            logger.error(f"❌ Filter Combinations failed: {e}")
            return {
                'success': False,
                'test_name': 'Filter Combinations',
                'error': str(e)
            }
    
    def test_v2_search_integration(self) -> Dict:
        """Test the new V2 search function integration"""
        logger.info("🔍 Testing V2 Search Integration")
        
        try:
            # Test the new V2 search function directly
            results = api.search_profiles_v2("Solana")
            results_count = len(results) if results is not None else 0
            
            logger.info(f"✅ V2 search returned {results_count} results")
            
            # Test profile data retrieval
            if results and len(results) > 0:
                first_profile_id = results[0].get('id')
                if first_profile_id:
                    profile_data = api.get_profile_data_by_id(first_profile_id)
                    logger.info(f"✅ Profile data retrieved: {bool(profile_data)}")
                else:
                    logger.warning("⚠️ No profile ID found in results")
            
            return {
                'success': True,
                'test_name': 'V2 Search Integration',
                'results_count': results_count,
                'results_type': type(results).__name__
            }
            
        except Exception as e:
            logger.error(f"❌ V2 Search Integration failed: {e}")
            return {
                'success': False,
                'test_name': 'V2 Search Integration',
                'error': str(e)
            }
    
    def test_error_handling(self) -> Dict:
        """Test error handling scenarios"""
        logger.info("🔍 Testing Error Handling")
        
        try:
            # Test with malformed user data
            user_data = {}  # Empty data
            
            results = api.get_profiles(user_data)
            results_count = len(results) if results is not None else 0
            
            logger.info(f"✅ Error handling returned {results_count} results")
            
            # Test with None data
            try:
                results_none = api.get_profiles(None)
                logger.error("❌ Should have failed with None data")
                return {
                    'success': False,
                    'test_name': 'Error Handling',
                    'error': 'Should have failed with None data'
                }
            except Exception:
                logger.info("✅ Properly handled None data")
            
            return {
                'success': True,
                'test_name': 'Error Handling',
                'results_count': results_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error Handling test failed: {e}")
            return {
                'success': False,
                'test_name': 'Error Handling',
                'error': str(e)
            }
    
    def run_all_tests(self) -> Dict:
        """Run all integration tests"""
        logger.info("🚀 Starting Integration Tests...")
        
        tests = []
        
        # Critical user flow tests
        logger.info("\n🔥 CRITICAL USER FLOW TESTS")
        tests.append(self.test_basic_search_flow())
        tests.append(self.test_empty_search_flow())
        tests.append(self.test_no_results_flow())
        
        # Advanced functionality tests
        logger.info("\n⚡ ADVANCED FUNCTIONALITY TESTS")
        tests.append(self.test_filter_combinations())
        tests.append(self.test_v2_search_integration())
        tests.append(self.test_error_handling())
        
        # Compile results
        passed = sum(1 for test in tests if test['success'])
        failed = len(tests) - passed
        
        # Log results
        logger.info(f"\n📊 INTEGRATION TEST RESULTS:")
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
            else:
                if 'results_count' in test:
                    logger.info(f"      Results: {test['results_count']}")
        
        return {
            'total_tests': len(tests),
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / len(tests)) * 100,
            'all_passed': failed == 0,
            'detailed_results': tests
        }

def main():
    """Main function to run integration tests"""
    print("🧪 GridDigger Integration Tester")
    print("=" * 50)
    
    tester = IntegrationTester()
    results = tester.run_all_tests()
    
    print(f"\n🎯 INTEGRATION TEST SUMMARY:")
    print(f"   Total Tests: {results['total_tests']}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Success Rate: {results['success_rate']:.1f}%")
    
    if results['all_passed']:
        print(f"\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("   The bot should handle user interactions properly.")
        return True
    else:
        print(f"\n⚠️ {results['failed']} integration tests failed.")
        print("   Some user flows may not work correctly.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)