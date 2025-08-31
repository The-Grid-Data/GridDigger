"""
GraphQL Query Tester for GridDigger V2 Migration
Tests all GraphQL queries to ensure they work with the V2 schema
All variables use String! type consistently
"""
import requests
import json
import logging
from typing import Dict, List, Any
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphQLTester:
    """Test all GraphQL queries for V2 migration"""
    
    def __init__(self):
        self.endpoint = Config.get_graphql_endpoint()
        self.headers = Config.get_graphql_headers()
        self.test_results = []
    
    def execute_query(self, query: str, variables: Dict = None, test_name: str = "") -> Dict:
        """Execute a GraphQL query and return results"""
        try:
            payload = {
                'query': query,
                'variables': variables or {}
            }
            
            logger.info(f"🔍 Testing: {test_name}")
            logger.debug(f"Query: {query[:100]}...")
            logger.debug(f"Variables: {variables}")
            
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Check for GraphQL errors
            if 'errors' in data:
                logger.error(f"GraphQL errors in {test_name}: {data['errors']}")
                return {
                    'success': False,
                    'test_name': test_name,
                    'errors': data['errors'],
                    'data': None,
                    'response_data': data
                }
            
            logger.info(f"✅ {test_name} - SUCCESS")
            return {
                'success': True,
                'test_name': test_name,
                'errors': None,
                'data': data.get('data', {}),
                'response_data': data
            }
            
        except Exception as e:
            logger.error(f"Exception in {test_name}: {str(e)}")
            return {
                'success': False,
                'test_name': test_name,
                'errors': [{'message': str(e)}],
                'data': None,
                'response_data': None
            }
    
    def test_basic_search(self) -> Dict:
        """Test basic search functionality - CRITICAL"""
        query = """
        query SearchForProfileNameOrAssetTicker($searchTerm: String1) {
          roots(
            where: {
              _or: [
                {profileInfos: {name: {_contains: $searchTerm}}},
                {assets: {ticker: {_contains: $searchTerm}}}
              ]
            }
          ) {
            id
            slug
          }
        }
        """
        
        variables = {"searchTerm": "The Grid"}
        return self.execute_query(query, variables, "Basic Search Test")
    
    def test_empty_search(self) -> Dict:
        """Test empty search - should return some results"""
        query = """
        query SearchForProfileNameOrAssetTicker($searchTerm: String1) {
          roots(
            where: {
              _or: [
                {profileInfos: {name: {_contains: $searchTerm}}},
                {assets: {ticker: {_contains: $searchTerm}}}
              ]
            }
            limit: 5
          ) {
            id
            slug
          }
        }
        """
        
        variables = {"searchTerm": ""}
        return self.execute_query(query, variables, "Empty Search Test")
    
    def test_profile_detail(self) -> Dict:
        """Test profile detail retrieval"""
        query = """
        query getProfileData($profileId: String1) {
          profileInfos(limit: 1, where: {root: {id: {_eq: $profileId}}}) {
            name
            tagLine
            descriptionShort
            logo
            profileSector { name }
            profileType { name }
            root {
              id
              slug
              assets {
                ticker
                name
                id
              }
              products {
                name
                id
              }
            }
            urls(order_by: {urlTypeId: Asc}) {
              url
              urlType { name }
            }
          }
        }
        """
        
        variables = {"profileId": "1"}
        return self.execute_query(query, variables, "Profile Detail Test")
    
    def test_profile_by_slug(self) -> Dict:
        """Test profile retrieval by slug"""
        query = """
        query getProfileDataBySlug($profileSlug: String1) {
          profileInfos(limit: 1, where: {root: {slug: {_eq: $profileSlug}}}) {
            name
            tagLine
            descriptionShort
            logo
            root {
              id
              slug
            }
          }
        }
        """
        
        variables = {"profileSlug": "The_Grid"}
        return self.execute_query(query, variables, "Profile By Slug Test")
    
    def test_filter_options(self) -> List[Dict]:
        """Test all filter option queries"""
        tests = []
        
        # Test profile types
        query = "query getProfileTypes { profileTypes { id name } }"
        tests.append(self.execute_query(query, {}, "Profile Types Test"))
        
        # Test profile sectors
        query = "query getProfileSectors { profileSectors { id name } }"
        tests.append(self.execute_query(query, {}, "Profile Sectors Test"))
        
        # Test asset types
        query = "query getAssetTypes { assetTypes { id name } }"
        tests.append(self.execute_query(query, {}, "Asset Types Test"))
        
        # Test profile statuses
        query = "query getProfileStatuses { profileStatuses { id name } }"
        tests.append(self.execute_query(query, {}, "Profile Statuses Test"))
        
        return tests
    
    def test_advanced_filters(self) -> Dict:
        """Test advanced filtering with multiple conditions"""
        query = """
        query searchWithFilters($profileTypeId: String1, $searchTerm: String1) {
          roots(
            where: {
              _and: [
                {profileInfos: {profileType: {id: {_eq: $profileTypeId}}}},
                {_or: [
                  {profileInfos: {name: {_contains: $searchTerm}}},
                  {assets: {ticker: {_contains: $searchTerm}}}
                ]}
              ]
            }
            limit: 10
          ) {
            id
            slug
            profileInfos {
              name
              descriptionShort
              logo
            }
          }
        }
        """
        
        variables = {
            "profileTypeId": "1",
            "searchTerm": "The Grid"
        }
        return self.execute_query(query, variables, "Advanced Filters Test")
    
    def test_full_profile_data(self) -> Dict:
        """Test full profile data retrieval"""
        query = """
        query getFullProfileData($profileId: String1) {
          profileInfos(limit: 1, offset: 0, where: {root: {id: {_eq: $profileId}}}) {
            tagLine
            descriptionShort
            descriptionLong
            profileSector { name }
            profileType { name }
            root {
              assets {
                ticker
                id
                rootId
                name
                icon
                description
                assetType { name id }
                assetStatus { name id }
                urls(order_by: {urlTypeId: Asc}) {
                  url
                  urlType { name id }
                }
              }
              socials {
                name
                socialType { name }
                urls(order_by: {urlTypeId: Asc}) { url }
              }
              products {
                id
                name
                launchDate
                isMainProduct
                description
                productType { name id }
                productStatus { name id }
                urls(order_by: {urlTypeId: Asc}) {
                  url
                  urlType { name id }
                }
              }
              entities {
                id
                name
                tradeName
                entityType { name id }
                country { name id code }
                urls {
                  url
                  urlType { name id }
                }
              }
            }
            profileStatus { name id }
            logo
            name
            urls(order_by: {urlTypeId: Asc}) {
              url
              urlType { name }
            }
          }
        }
        """
        
        variables = {"profileId": "1"}
        return self.execute_query(query, variables, "Full Profile Data Test")
    
    def test_solana_filter(self) -> Dict:
        """Test Solana-specific filtering"""
        query = """
        query getSolanaProfiles($productId: String1) {
          roots(
            where: {
              products: {id: {_eq: $productId}}
            }
            limit: 5
          ) {
            id
            slug
            profileInfos {
              name
              descriptionShort
            }
          }
        }
        """
        
        variables = {"productId": "22"}  # Solana product ID
        return self.execute_query(query, variables, "Solana Filter Test")
    
    def run_all_tests(self) -> Dict:
        """Run all GraphQL tests and return summary"""
        logger.info("🚀 Starting GraphQL V2 Migration Tests...")
        logger.info(f"📡 Endpoint: {self.endpoint}")
        logger.info(f"🔑 Headers: {self.headers}")
        
        # Run all tests
        tests = []
        
        # Critical tests - these must pass for basic functionality
        logger.info("\n🔥 CRITICAL TESTS (Must Pass)")
        tests.append(self.test_basic_search())
        tests.append(self.test_empty_search())
        tests.append(self.test_profile_detail())
        
        # Filter option tests - needed for UI dropdowns
        logger.info("\n📋 FILTER OPTION TESTS")
        tests.extend(self.test_filter_options())
        
        # Advanced functionality tests
        logger.info("\n⚡ ADVANCED TESTS")
        tests.append(self.test_profile_by_slug())
        tests.append(self.test_advanced_filters())
        tests.append(self.test_full_profile_data())
        tests.append(self.test_solana_filter())
        
        # Compile results
        passed = sum(1 for test in tests if test['success'])
        failed = len(tests) - passed
        critical_tests = tests[:3]  # First 3 are critical
        critical_passed = sum(1 for test in critical_tests if test['success'])
        
        # Log results
        logger.info(f"\n📊 TEST RESULTS SUMMARY")
        logger.info(f"   Total Tests: {len(tests)}")
        logger.info(f"   Passed: {passed}")
        logger.info(f"   Failed: {failed}")
        logger.info(f"   Critical Tests Passed: {critical_passed}/3")
        logger.info(f"   Success Rate: {(passed / len(tests)) * 100:.1f}%")
        
        logger.info(f"\n📝 DETAILED RESULTS:")
        for test in tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            logger.info(f"   {status} - {test['test_name']}")
            
            if not test['success']:
                logger.error(f"      Error: {test['errors']}")
                if test.get('response_data'):
                    logger.debug(f"      Response: {json.dumps(test['response_data'], indent=2)}")
        
        return {
            'total_tests': len(tests),
            'passed': passed,
            'failed': failed,
            'critical_passed': critical_passed,
            'success_rate': (passed / len(tests)) * 100,
            'critical_success': critical_passed == 3,
            'detailed_results': tests
        }

def main():
    """Main function to run GraphQL tests"""
    print("🧪 GridDigger GraphQL V2 Migration Tester")
    print("=" * 50)
    
    tester = GraphQLTester()
    results = tester.run_all_tests()
    
    print(f"\n🎯 FINAL TEST SUMMARY:")
    print(f"   Total Tests: {results['total_tests']}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Success Rate: {results['success_rate']:.1f}%")
    print(f"   Critical Tests: {results['critical_passed']}/3")
    
    if not results['critical_success']:
        print(f"\n🚨 CRITICAL FAILURE: {3 - results['critical_passed']} critical tests failed!")
        print("   The bot will not function properly until these are fixed.")
        return False
    elif results['failed'] > 0:
        print(f"\n⚠️  {results['failed']} non-critical tests failed.")
        print("   Basic functionality should work, but some features may be limited.")
        return True
    else:
        print(f"\n🎉 ALL TESTS PASSED! V2 migration queries are working perfectly.")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)