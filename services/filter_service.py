"""
Filter service for handling filter-related business logic
"""
import logging
from typing import List, Dict, Any, Optional
from config import Config
from cache import cached

# Import the appropriate API based on configuration
from api_v2 import grid_api_v2 as api_client

logger = logging.getLogger(__name__)


class FilterService:
    """Service for filter-related operations"""
    
    def __init__(self):
        pass
    
    @cached(prefix="filter_options", ttl=600)  # Cache for 10 minutes
    def get_filter_options(self, filter_type: str) -> Dict[str, Any]:
        """
        Get available options for a specific filter type
        
        Args:
            filter_type: Type of filter (profileTypes, profileSectors, etc.)
            
        Returns:
            Dictionary containing filter options or error information
        """
        try:
            if self.use_new_api:
                response = api_client.get_filter_options(filter_type)
                
                if not response.success:
                    logger.error(f"Failed to fetch filter options for {filter_type}: {response.errors}")
                    return {
                        'success': False,
                        'error': response.errors[0] if response.errors else 'Unknown error',
                        'options': []
                    }
                
                return {
                    'success': True,
                    'options': response.data['options'],
                    'count': len(response.data['options'])
                }
            
                    
                
                return {
                    'success': True,
                    'options': options,
                    'count': len(options)
                }
                
        except Exception as e:
            logger.error(f"Error fetching filter options for {filter_type}: {e}")
            return {
                'success': False,
                'error': str(e),
                'options': []
            }
    
    def get_sub_filters(self, filter_category: str) -> List[Dict[str, Any]]:
        """
        Get sub-filters for a specific category
        
        Args:
            filter_category: Category of filters (profile, product, asset, entity)
            
        Returns:
            List of sub-filter definitions
        """
        try:
            if self.use_new_api:
                # Define sub-filters for new API structure
                sub_filters_map = {
                    'profile': [
                        {'label': 'Profile Name', 'type': 'searchable', 'query': 'profileNameSearch'},
                        {'label': 'Profile Type', 'type': 'multiple', 'query': 'profileTypes'},
                        {'label': 'Profile Sector', 'type': 'multiple', 'query': 'profileSectors'},
                        {'label': 'Profile Status', 'type': 'multiple', 'query': 'profileStatuses'}
                    ],
                    'product': [
                        {'label': 'Product Type', 'type': 'multiple', 'query': 'productTypes'},
                        {'label': 'Product Status', 'type': 'multiple', 'query': 'productStatuses'}
                    ],
                    'asset': [
                        {'label': 'Ticker', 'type': 'searchable', 'query': 'assetTickers'},
                        {'label': 'Asset Type', 'type': 'multiple', 'query': 'assetTypes'},
                        {'label': 'Asset Standard', 'type': 'multiple', 'query': 'assetStandards'}
                    ],
                    'entity': [
                        {'label': 'Entity Type', 'type': 'multiple', 'query': 'entityTypes'},
                        {'label': 'Entity Name', 'type': 'searchable', 'query': 'entityName'}
                    ]
                }
                
                return sub_filters_map.get(filter_category, [])
            
                
        except Exception as e:
            logger.error(f"Error getting sub-filters for {filter_category}: {e}")
            return []
    
    def validate_filter_value(self, filter_type: str, value: Any) -> bool:
        """
        Validate filter value
        
        Args:
            filter_type: Type of filter
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        if value is None:
            return False
        
        # String filters
        if filter_type in ['profileNameSearch', 'entityName', 'assetTickers']:
            if not isinstance(value, str):
                return False
            
            cleaned_value = value.strip()
            if len(cleaned_value) == 0:
                return False
            
            if len(cleaned_value) > 100:
                return False
            
            return True
        
        # ID-based filters
        if filter_type in ['profileTypes', 'profileSectors', 'profileStatuses', 
                          'productTypes', 'productStatuses', 'assetTypes', 
                          'assetStandards', 'entityTypes']:
            if isinstance(value, str):
                try:
                    int(value)
                    return True
                except ValueError:
                    return False
            elif isinstance(value, int):
                return value > 0
            
            return False
        
        return True
    
    def format_applied_filters(self, filters: Dict[str, Any]) -> str:
        """
        Format applied filters into a readable string
        
        Args:
            filters: Dictionary of applied filters
            
        Returns:
            Formatted string describing applied filters
        """
        if not filters:
            return "No filters applied"
        
        try:
            filter_descriptions = []
            
            for key, value in filters.items():
                if key.endswith('_query'):
                    continue  # Skip query versions
                
                if value is None or value == "":
                    continue
                
                # Format different filter types
                if key == 'profileNameSearch':
                    filter_descriptions.append(f"Name: {value}")
                elif key == 'entityName':
                    filter_descriptions.append(f"Entity: {value}")
                elif key == 'assetTickers':
                    filter_descriptions.append(f"Ticker: {value}")
                else:
                    # For ID-based filters, show the display name if available
                    filter_descriptions.append(f"{key}: {value}")
            
            if not filter_descriptions:
                return "No filters applied"
            
            return "\n".join(filter_descriptions)
            
        except Exception as e:
            logger.error(f"Error formatting applied filters: {e}")
            return "Error formatting filters"
    
    def reset_filters(self, user_data: Dict[str, Any]) -> bool:
        """
        Reset all filters in user data
        
        Args:
            user_data: User data dictionary to reset
            
        Returns:
            True if filters were reset, False if already empty
        """
        try:
            filters = user_data.get('FILTERS', {})
            
            if not filters:
                return False
            
            user_data['FILTERS'] = {}
            return True
            
        except Exception as e:
            logger.error(f"Error resetting filters: {e}")
            return False
    
    def toggle_filter_option(self, user_data: Dict[str, Any], option_name: str) -> bool:
        """
        Toggle a boolean filter option
        
        Args:
            user_data: User data dictionary
            option_name: Name of the option to toggle
            
        Returns:
            New state of the option
        """
        try:
            current_state = user_data.get(option_name, False)
            new_state = not current_state
            user_data[option_name] = new_state
            
            logger.debug(f"Toggled {option_name}: {current_state} -> {new_state}")
            return new_state
            
        except Exception as e:
            logger.error(f"Error toggling filter option {option_name}: {e}")
            return False
    
    def get_filter_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about filter usage
        
        Returns:
            Dictionary containing filter statistics
        """
        # Placeholder for analytics implementation
        return {
            "most_used_filters": [
                "profileNameSearch",
                "profileSectors",
                "profileTypes"
            ],
            "total_filter_queries": 0,
            "cache_hit_rate": 0.0
        }
    
    def clear_filter_cache(self, filter_type: str = None):
        """
        Clear filter cache for specific type or all filters
        
        Args:
            filter_type: Specific filter type to clear, or None for all
        """
        try:
            if filter_type:
                # Clear specific filter cache
                self.get_filter_options.cache_delete(filter_type)
                logger.info(f"Cleared cache for filter type '{filter_type}'")
            else:
                # Clear all filter cache
                self.get_filter_options.cache_clear()
                logger.info("Cleared all filter cache")
        except Exception as e:
            logger.error(f"Error clearing filter cache: {e}")
    
    def build_filter_keyboard_data(self, user_data: Dict[str, Any], 
                                  results_count: int) -> Dict[str, Any]:
        """
        Build data for filter keyboard display
        
        Args:
            user_data: User data containing current filters
            results_count: Number of results found with current filters
            
        Returns:
            Dictionary containing keyboard data
        """
        try:
            filters = user_data.get('FILTERS', {})
            
            # Determine filter states
            profile_active = any(key in filters for key in 
                               ['profileNameSearch', 'profileTypes', 'profileSectors', 'profileStatuses'])
            product_active = any(key in filters for key in 
                               ['productTypes', 'productStatuses'])
            asset_active = any(key in filters for key in 
                             ['assetTickers', 'assetTypes', 'assetStandards'])
            entity_active = any(key in filters for key in 
                              ['entityTypes', 'entityName'])
            
            return {
                'results_count': results_count,
                'display_count': min(results_count, 20),
                'filters_active': {
                    'profile': profile_active,
                    'product': product_active,
                    'asset': asset_active,
                    'entity': entity_active
                },
                'solana_filter': user_data.get('solana_filter_toggle', True),
                'inc_search': user_data.get('inc_search', False),
                'applied_filters_text': self.format_applied_filters(filters)
            }
            
        except Exception as e:
            logger.error(f"Error building filter keyboard data: {e}")
            return {
                'results_count': 0,
                'display_count': 0,
                'filters_active': {
                    'profile': False,
                    'product': False,
                    'asset': False,
                    'entity': False
                },
                'solana_filter': True,
                'inc_search': False,
                'applied_filters_text': "Error loading filters"
            }


# Global service instance
filter_service = FilterService()