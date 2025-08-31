"""
Tests for service layer components
"""
import unittest
from unittest.mock import Mock, patch, MagicMock

from services.profile_service import ProfileService
from services.search_service import SearchService
from services.filter_service import FilterService
from models.common import APIResponse


class TestProfileService(unittest.TestCase):
    """Test cases for ProfileService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = ProfileService()
    
    @patch('services.profile_service.api_client')
    def test_get_profile_by_id_success(self, mock_api):
        """Test successful profile retrieval"""
        # Mock profile object
        mock_profile = Mock()
        mock_profile.to_legacy_format.return_value = {
            'id': '1',
            'name': 'Test Profile',
            'descriptionShort': 'Test description'
        }
        
        # Mock API response
        mock_response = APIResponse.success_response({'profile': mock_profile})
        mock_api.get_profile_by_id.return_value = mock_response
        
        result = self.service.get_profile_by_id('1')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['profile']['name'], 'Test Profile')
        mock_api.get_profile_by_id.assert_called_once_with('1')
    
    @patch('services.profile_service.api_client')
    def test_get_profile_by_id_error(self, mock_api):
        """Test profile retrieval with error"""
        # Mock API error response
        mock_response = APIResponse.error_response(['Profile not found'])
        mock_api.get_profile_by_id.return_value = mock_response
        
        result = self.service.get_profile_by_id('999')
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Profile not found')
        self.assertIsNone(result['profile'])
    
    def test_format_profile_message_basic(self):
        """Test basic profile message formatting"""
        profile_data = {
            'name': 'Test Profile',
            'profileSector': {'name': 'DeFi'},
            'descriptionShort': 'Test description'
        }
        
        message = self.service.format_profile_message(profile_data)
        
        self.assertIn('*Name:* Test Profile', message)
        self.assertIn('*Sector:* DeFi', message)
        self.assertIn('*Description:* Test description', message)
    
    def test_format_profile_message_expanded(self):
        """Test expanded profile message formatting"""
        profile_data = {
            'id': '1',
            'name': 'Test Profile',
            'profileSector': {'name': 'DeFi'},
            'profileType': {'name': 'Company'},
            'profileStatus': {'name': 'Active'},
            'descriptionLong': 'Long test description',
            'products': [{'name': 'Product 1'}, {'name': 'Product 2'}],
            'assets': [{'name': 'Asset 1'}]
        }
        
        message = self.service.format_profile_message(profile_data, expanded=True)
        
        self.assertIn('*ID:* 1', message)
        self.assertIn('*Type:* Company', message)
        self.assertIn('*Status:* Active', message)
        self.assertIn('*Products:* Product 1, Product 2', message)
        self.assertIn('*Assets:* Asset 1', message)
    
    def test_get_profile_urls(self):
        """Test profile URL extraction"""
        profile_data = {
            'urlMain': 'https://example.com',
            'urlDocumentation': 'https://docs.example.com',
            'socials': [
                {'url': 'https://twitter.com/example'},
                {'url': 'https://discord.gg/example'}
            ]
        }
        
        urls = self.service.get_profile_urls(profile_data)
        
        self.assertEqual(len(urls), 4)
        self.assertEqual(urls[0]['name'], 'Website')
        self.assertEqual(urls[0]['url'], 'https://example.com')
        self.assertEqual(urls[1]['name'], 'Documentation')
        self.assertEqual(urls[2]['name'], 'Social')
    
    def test_validate_profile_id(self):
        """Test profile ID validation"""
        # Valid IDs
        self.assertTrue(self.service.validate_profile_id('123'))
        self.assertTrue(self.service.validate_profile_id('test-profile'))
        
        # Invalid IDs
        self.assertFalse(self.service.validate_profile_id(''))
        self.assertFalse(self.service.validate_profile_id(None))
        self.assertFalse(self.service.validate_profile_id('   '))
        self.assertFalse(self.service.validate_profile_id('x' * 101))


class TestSearchService(unittest.TestCase):
    """Test cases for SearchService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = SearchService()
    
    @patch('services.search_service.api_client')
    def test_search_profiles_success(self, mock_api):
        """Test successful profile search"""
        # Mock search result
        mock_search_result = Mock()
        mock_search_result.get_profiles_list.return_value = [
            {'id': '1', 'name': 'Profile 1'},
            {'id': '2', 'name': 'Profile 2'}
        ]
        mock_search_result.total_count = 2
        
        # Mock API response
        mock_response = APIResponse.success_response({'search_result': mock_search_result})
        mock_api.search_profiles.return_value = mock_response
        
        result = self.service.search_profiles('test')
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['profiles']), 2)
        self.assertEqual(result['total_count'], 2)
        mock_api.search_profiles.assert_called_once_with('test', 20, 0)
    
    @patch('services.search_service.api_client')
    def test_search_profiles_error(self, mock_api):
        """Test profile search with error"""
        # Mock API error response
        mock_response = APIResponse.error_response(['Search failed'])
        mock_api.search_profiles.return_value = mock_response
        
        result = self.service.search_profiles('test')
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Search failed')
        self.assertEqual(len(result['profiles']), 0)
    
    def test_validate_search_term(self):
        """Test search term validation"""
        # Valid terms
        self.assertTrue(self.service.validate_search_term('test'))
        self.assertTrue(self.service.validate_search_term('DeFi'))
        self.assertTrue(self.service.validate_search_term('Solana Protocol'))
        
        # Invalid terms
        self.assertFalse(self.service.validate_search_term(''))
        self.assertFalse(self.service.validate_search_term(None))
        self.assertFalse(self.service.validate_search_term('   '))
        self.assertFalse(self.service.validate_search_term('a'))  # Too short
        self.assertFalse(self.service.validate_search_term('x' * 101))  # Too long
    
    def test_format_search_results_summary(self):
        """Test search results summary formatting"""
        # Successful results
        results = {
            'success': True,
            'total_count': 5,
            'profiles': [{'id': '1'}, {'id': '2'}]
        }
        
        summary = self.service.format_search_results_summary(results)
        self.assertIn('Found 5 profiles', summary)
        
        # No results
        results = {
            'success': True,
            'total_count': 0,
            'profiles': []
        }
        
        summary = self.service.format_search_results_summary(results)
        self.assertIn('No profiles found', summary)
        
        # Error
        results = {
            'success': False,
            'error': 'Search failed'
        }
        
        summary = self.service.format_search_results_summary(results)
        self.assertIn('Search failed', summary)
    
    def test_get_search_suggestions(self):
        """Test search suggestions"""
        suggestions = self.service.get_search_suggestions('De')
        self.assertIn('DeFi', suggestions)
        
        suggestions = self.service.get_search_suggestions('a')
        self.assertEqual(len(suggestions), 0)  # Too short
    
    def test_get_popular_searches(self):
        """Test popular searches retrieval"""
        popular = self.service.get_popular_searches()
        self.assertIsInstance(popular, list)
        self.assertGreater(len(popular), 0)


class TestFilterService(unittest.TestCase):
    """Test cases for FilterService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = FilterService()
    
    @patch('services.filter_service.api_client')
    def test_get_filter_options_success(self, mock_api):
        """Test successful filter options retrieval"""
        # Mock API response
        mock_response = APIResponse.success_response({
            'options': [
                {'id': 1, 'name': 'Option 1'},
                {'id': 2, 'name': 'Option 2'}
            ]
        })
        mock_api.get_filter_options.return_value = mock_response
        
        result = self.service.get_filter_options('profileTypes')
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['options']), 2)
        self.assertEqual(result['count'], 2)
        mock_api.get_filter_options.assert_called_once_with('profileTypes')
    
    def test_get_sub_filters(self):
        """Test sub-filters retrieval"""
        sub_filters = self.service.get_sub_filters('profile')
        
        self.assertIsInstance(sub_filters, list)
        self.assertGreater(len(sub_filters), 0)
        
        # Check structure
        for filter_def in sub_filters:
            self.assertIn('label', filter_def)
            self.assertIn('type', filter_def)
            self.assertIn('query', filter_def)
    
    def test_validate_filter_value(self):
        """Test filter value validation"""
        # String filters
        self.assertTrue(self.service.validate_filter_value('profileNameSearch', 'test'))
        self.assertFalse(self.service.validate_filter_value('profileNameSearch', ''))
        self.assertFalse(self.service.validate_filter_value('profileNameSearch', None))
        
        # ID-based filters
        self.assertTrue(self.service.validate_filter_value('profileTypes', '1'))
        self.assertTrue(self.service.validate_filter_value('profileTypes', 1))
        self.assertFalse(self.service.validate_filter_value('profileTypes', 'invalid'))
        self.assertFalse(self.service.validate_filter_value('profileTypes', 0))
    
    def test_format_applied_filters(self):
        """Test applied filters formatting"""
        filters = {
            'profileNameSearch': 'test',
            'profileTypes': 'Company',
            'profileNameSearch_query': 'test'  # Should be ignored
        }
        
        formatted = self.service.format_applied_filters(filters)
        
        self.assertIn('Name: test', formatted)
        self.assertIn('profileTypes: Company', formatted)
        self.assertNotIn('_query', formatted)
    
    def test_reset_filters(self):
        """Test filter reset functionality"""
        user_data = {
            'FILTERS': {
                'profileNameSearch': 'test',
                'profileTypes': '1'
            }
        }
        
        result = self.service.reset_filters(user_data)
        
        self.assertTrue(result)
        self.assertEqual(user_data['FILTERS'], {})
        
        # Test with empty filters
        result = self.service.reset_filters(user_data)
        self.assertFalse(result)
    
    def test_toggle_filter_option(self):
        """Test filter option toggling"""
        user_data = {}
        
        # Toggle from default (False) to True
        result = self.service.toggle_filter_option(user_data, 'test_option')
        self.assertTrue(result)
        self.assertTrue(user_data['test_option'])
        
        # Toggle back to False
        result = self.service.toggle_filter_option(user_data, 'test_option')
        self.assertFalse(result)
        self.assertFalse(user_data['test_option'])
    
    def test_build_filter_keyboard_data(self):
        """Test filter keyboard data building"""
        user_data = {
            'FILTERS': {
                'profileNameSearch': 'test',
                'productTypes': '1'
            },
            'solana_filter_toggle': True,
            'inc_search': False
        }
        
        keyboard_data = self.service.build_filter_keyboard_data(user_data, 10)
        
        self.assertEqual(keyboard_data['results_count'], 10)
        self.assertEqual(keyboard_data['display_count'], 10)
        self.assertTrue(keyboard_data['filters_active']['profile'])
        self.assertTrue(keyboard_data['filters_active']['product'])
        self.assertFalse(keyboard_data['filters_active']['asset'])
        self.assertTrue(keyboard_data['solana_filter'])
        self.assertFalse(keyboard_data['inc_search'])


if __name__ == '__main__':
    unittest.main()