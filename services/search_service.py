"""
Search service for handling search-related business logic
"""
import logging
from typing import List, Dict, Any, Optional
from config import Config
from cache import cached
from models.search import SearchResult
from models.common import APIResponse

# Import the appropriate API based on configuration
from api_v2 import grid_api_v2 as api_client

logger = logging.getLogger(__name__)


class SearchService:
    """Service for search-related operations"""
    
    def __init__(self):
        pass
    
    @cached(prefix="search_profiles", ttl=180)  # Cache for 3 minutes
    def search_profiles(self, search_term: str, filters: Dict[str, Any] = None, 
                       limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Search for profiles with optional filters
        
        Args:
            search_term: Search term for profile names or asset tickers
            filters: Additional filters to apply
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            Dictionary containing search results or error information
        """
        try:
            if self.use_new_api:
                response = api_client.search_profiles(search_term, limit, offset)
                
                if not response.success:
                    logger.error(f"Search failed for term '{search_term}': {response.errors}")
                    return {
                        'success': False,
                        'error': response.errors[0] if response.errors else 'Unknown error',
                        'profiles': [],
                        'total_count': 0
                    }
                
                search_result = response.data['search_result']
                return {
                    'success': True,
                    'profiles': search_result.get_profiles_list(),
                    'total_count': search_result.total_count,
                    'raw_result': search_result
                }
            
                    'FILTERS': filters or {}
                
                # Add search term to filters
                if search_term:
                    user_data['FILTERS']['profileNameSearch'] = search_term
                    user_data['FILTERS']['profileNameSearch_query'] = search_term
                
                profiles = legacy_api.get_profiles(user_data)
                
                return {
                    'success': True,
                    'profiles': profiles[:limit],
                    'total_count': len(profiles),
                    'raw_result': None
                }
                
        except Exception as e:
            logger.error(f"Error searching profiles with term '{search_term}': {e}")
            return {
                'success': False,
                'error': str(e),
                'profiles': [],
                'total_count': 0
            }
    
    def search_with_legacy_filters(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search using legacy filter format for backward compatibility
        
        Args:
            user_data: User data containing filters in legacy format
            
        Returns:
            Dictionary containing search results
        """
        try:
            if self.use_new_api:
                # Convert legacy filters to new format
                search_term = ""
                filters = user_data.get('FILTERS', {})
                
                # Extract search term from filters
                if 'profileNameSearch_query' in filters:
                    search_term = filters['profileNameSearch_query']
                elif 'profileNameSearch' in filters:
                    search_term = filters['profileNameSearch']
                
                # For now, use basic search - can be expanded to handle more filters
                return self.search_profiles(search_term)
            
                
                return {
                    'success': True,
                    'profiles': profiles,
                    'total_count': len(profiles)
                }
                
        except Exception as e:
            logger.error(f"Error in legacy filter search: {e}")
            return {
                'success': False,
                'error': str(e),
                'profiles': [],
                'total_count': 0
            }
    
    def validate_search_term(self, search_term: str) -> bool:
        """
        Validate search term
        
        Args:
            search_term: Search term to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not search_term:
            return False
        
        # Remove whitespace and check length
        cleaned_term = search_term.strip()
        
        if len(cleaned_term) == 0:
            return False
        
        # Minimum length check
        if len(cleaned_term) < 2:
            return False
        
        # Maximum length check
        if len(cleaned_term) > 100:
            return False
        
        return True
    
    def format_search_results_summary(self, results: Dict[str, Any]) -> str:
        """
        Format search results into a summary string
        
        Args:
            results: Search results dictionary
            
        Returns:
            Formatted summary string
        """
        if not results.get('success'):
            return f"Search failed: {results.get('error', 'Unknown error')}"
        
        total_count = results.get('total_count', 0)
        profiles = results.get('profiles', [])
        
        if total_count == 0:
            return "No profiles found matching your search criteria."
        
        displayed_count = min(len(profiles), 20)  # Limit display to 20
        
        if total_count == displayed_count:
            return f"Found {total_count} profile{'s' if total_count != 1 else ''}."
        else:
            return f"Found {total_count} profile{'s' if total_count != 1 else ''}, showing first {displayed_count}."
    
    def get_search_suggestions(self, partial_term: str) -> List[str]:
        """
        Get search suggestions based on partial term
        
        Args:
            partial_term: Partial search term
            
        Returns:
            List of suggested search terms
        """
        # This is a placeholder for future implementation
        # Could be implemented with a separate suggestions API or cached popular searches
        suggestions = []
        
        if len(partial_term) >= 2:
            # Basic suggestions based on common patterns
            common_terms = [
                "DeFi", "NFT", "DEX", "Solana", "Ethereum", "Bitcoin",
                "Lending", "Trading", "Wallet", "Bridge", "Oracle"
            ]
            
            suggestions = [
                term for term in common_terms 
                if term.lower().startswith(partial_term.lower())
            ]
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def get_popular_searches(self) -> List[str]:
        """
        Get list of popular search terms
        
        Returns:
            List of popular search terms
        """
        # This could be implemented with analytics data
        # For now, return some common terms
        return [
            "Solana",
            "DeFi",
            "NFT",
            "DEX",
            "Lending"
        ]
    
    def clear_search_cache(self, search_term: str = None):
        """
        Clear search cache for specific term or all searches
        
        Args:
            search_term: Specific search term to clear, or None for all
        """
        try:
            if search_term:
                # Clear specific search cache
                self.search_profiles.cache_delete(search_term)
                logger.info(f"Cleared cache for search term '{search_term}'")
            else:
                # Clear all search cache
                self.search_profiles.cache_clear()
                logger.info("Cleared all search cache")
        except Exception as e:
            logger.error(f"Error clearing search cache: {e}")
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """
        Get search analytics data
        
        Returns:
            Dictionary containing search analytics
        """
        # Placeholder for analytics implementation
        return {
            "total_searches": 0,
            "popular_terms": self.get_popular_searches(),
            "cache_hit_rate": 0.0
        }


# Global service instance
search_service = SearchService()