"""
Tests for the new GraphQL API client
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import json

from api_v2 import GraphQLClient, GridAPIv2
from models.common import APIResponse
from models.search import SearchResult
from models.profile import Profile


class TestGraphQLClient(unittest.TestCase):
    """Test cases for GraphQLClient"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = GraphQLClient()
    
    @patch('api_v2.requests.Session')
    def test_create_session(self, mock_session_class):
        """Test session creation with proper configuration"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        client = GraphQLClient()
        
        # Verify session was configured
        mock_session.mount.assert_called()
        mock_session.headers.update.assert_called()
    
    @patch('api_v2.requests.Session.post')
    def test_execute_query_success(self, mock_post):
        """Test successful query execution"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'test': 'result'}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        query = "query { test }"
        result = self.client.execute_query(query)
        
        self.assertTrue(result.success)
        self.assertEqual(result.data['data']['test'], 'result')
    
    @patch('api_v2.requests.Session.post')
    def test_execute_query_graphql_error(self, mock_post):
        """Test query execution with GraphQL errors"""
        # Mock response with GraphQL errors
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'errors': [{'message': 'Test error'}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        query = "query { test }"
        result = self.client.execute_query(query)
        
        self.assertFalse(result.success)
        self.assertIn('Test error', result.errors)
    
    @patch('api_v2.requests.Session.post')
    def test_execute_query_network_error(self, mock_post):
        """Test query execution with network error"""
        # Mock network error
        mock_post.side_effect = Exception("Network error")
        
        query = "query { test }"
        result = self.client.execute_query(query)
        
        self.assertFalse(result.success)
        self.assertIn('Unexpected error occurred', result.errors)


class TestGridAPIv2(unittest.TestCase):
    """Test cases for GridAPIv2"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api = GridAPIv2()
    
    @patch('api_v2.GraphQLClient.execute_query')
    def test_search_profiles_success(self, mock_execute):
        """Test successful profile search"""
        # Mock successful API response
        mock_response = APIResponse.success_response({
            'data': {
                'roots': [
                    {
                        'id': '1',
                        'slug': 'test-profile',
                        'profileInfos': [
                            {
                                'name': 'Test Profile',
                                'descriptionShort': 'Test description',
                                'logo': 'https://example.com/logo.png',
                                'urls': []
                            }
                        ]
                    }
                ]
            }
        })
        mock_execute.return_value = mock_response
        
        result = self.api.search_profiles("test")
        
        self.assertTrue(result.success)
        self.assertIn('search_result', result.data)
        self.assertEqual(len(result.data['search_result'].roots), 1)
    
    @patch('api_v2.GraphQLClient.execute_query')
    def test_search_profiles_error(self, mock_execute):
        """Test profile search with error"""
        # Mock error response
        mock_response = APIResponse.error_response(['API Error'])
        mock_execute.return_value = mock_response
        
        result = self.api.search_profiles("test")
        
        self.assertFalse(result.success)
        self.assertEqual(result.errors[0], 'API Error')
    
    @patch('api_v2.GraphQLClient.execute_query')
    def test_get_profile_by_id_success(self, mock_execute):
        """Test successful profile retrieval"""
        # Mock successful API response
        mock_response = APIResponse.success_response({
            'data': {
                'profileInfos': [
                    {
                        'name': 'Test Profile',
                        'descriptionShort': 'Test description',
                        'descriptionLong': 'Long test description',
                        'logo': 'https://example.com/logo.png',
                        'urls': [],
                        'profileSector': {'name': 'DeFi'},
                        'profileType': {'name': 'Company'},
                        'profileStatus': {'name': 'Active'},
                        'root': {
                            'id': '1',
                            'slug': 'test-profile',
                            'assets': [],
                            'socials': [],
                            'entities': [],
                            'products': []
                        }
                    }
                ]
            }
        })
        mock_execute.return_value = mock_response
        
        result = self.api.get_profile_by_id("1")
        
        self.assertTrue(result.success)
        self.assertIn('profile', result.data)
        self.assertEqual(result.data['profile'].name, 'Test Profile')
    
    @patch('api_v2.GraphQLClient.execute_query')
    def test_get_profile_by_id_not_found(self, mock_execute):
        """Test profile retrieval when profile not found"""
        # Mock empty response
        mock_response = APIResponse.success_response({
            'data': {
                'profileInfos': []
            }
        })
        mock_execute.return_value = mock_response
        
        result = self.api.get_profile_by_id("999")
        
        self.assertFalse(result.success)
        self.assertIn('Profile not found', result.errors)
    
    @patch('api_v2.GraphQLClient.execute_query')
    def test_get_filter_options_success(self, mock_execute):
        """Test successful filter options retrieval"""
        # Mock successful API response
        mock_response = APIResponse.success_response({
            'data': {
                'profileTypes': [
                    {'id': 1, 'name': 'Company'},
                    {'id': 2, 'name': 'Protocol'}
                ]
            }
        })
        mock_execute.return_value = mock_response
        
        result = self.api.get_filter_options('profileTypes')
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.data['options']), 2)
        self.assertEqual(result.data['options'][0]['name'], 'Company')
    
    def test_get_filter_options_invalid_type(self):
        """Test filter options with invalid filter type"""
        result = self.api.get_filter_options('invalid_filter')
        
        self.assertFalse(result.success)
        self.assertIn('Invalid filter type', result.errors)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility functions"""
    
    @patch('api_v2.grid_api_v2.search_profiles')
    def test_search_thegrid_v2(self, mock_search):
        """Test backward compatible search function"""
        from api_v2 import search_thegrid_v2
        
        # Mock search result
        mock_search_result = SearchResult()
        mock_search_result.roots = []
        
        mock_response = APIResponse.success_response({
            'search_result': mock_search_result
        })
        mock_search.return_value = mock_response
        
        result = search_thegrid_v2("test")
        
        self.assertIsInstance(result, list)
        mock_search.assert_called_once_with("test", 20)
    
    @patch('api_v2.grid_api_v2.get_profile_by_id')
    def test_fetch_thegrid_v2(self, mock_get_profile):
        """Test backward compatible profile fetch function"""
        from api_v2 import fetch_thegrid_v2
        
        # Mock profile
        mock_profile = Mock()
        mock_profile.to_legacy_format.return_value = {'id': '1', 'name': 'Test'}
        
        mock_response = APIResponse.success_response({
            'profile': mock_profile
        })
        mock_get_profile.return_value = mock_response
        
        result = fetch_thegrid_v2("1")
        
        self.assertEqual(result['id'], '1')
        self.assertEqual(result['name'], 'Test')
        mock_get_profile.assert_called_once_with("1")


if __name__ == '__main__':
    unittest.main()