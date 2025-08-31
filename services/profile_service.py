"""
Profile service for handling profile-related business logic
"""
import logging
from typing import Optional, Dict, Any, List
from config import Config
from cache import cached, cache_profile_detail
from models.profile import Profile
from models.common import APIResponse

# Import the appropriate API based on configuration
from api_v2 import grid_api_v2 as api_client

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for profile-related operations"""
    
    def __init__(self):
        pass
    
    @cached(prefix="profile_detail", ttl=300)  # Cache for 5 minutes
    def get_profile_by_id(self, profile_id: str) -> Dict[str, Any]:
        """
        Get detailed profile information by ID
        
        Args:
            profile_id: Profile ID or slug
            
        Returns:
            Dictionary containing profile data or error information
        """
        try:
            if self.use_new_api:
                response = api_client.get_profile_by_id(profile_id)
                
                if not response.success:
                    logger.error(f"Failed to fetch profile {profile_id}: {response.errors}")
                    return {
                        'success': False,
                        'error': response.errors[0] if response.errors else 'Unknown error',
                        'profile': None
                    }
                
                profile = response.data['profile']
                return {
                    'success': True,
                    'profile': profile.to_legacy_format(),
                    'raw_profile': profile
                }
            
                
                if not profile_data:
                    return {
                        'success': False,
                        'error': 'Profile not found',
                        'profile': None
                    }
                
                return {
                    'success': True,
                    'profile': profile_data,
                    'raw_profile': None
                }
                
        except Exception as e:
            logger.error(f"Error fetching profile {profile_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'profile': None
            }
    
    @cached(prefix="profile_basic", ttl=180)  # Cache for 3 minutes
    def get_basic_profile_by_id(self, profile_id: str) -> Dict[str, Any]:
        """
        Get basic profile information by ID (for profile cards)
        
        Args:
            profile_id: Profile ID or slug
            
        Returns:
            Dictionary containing basic profile data
        """
        try:
            if self.use_new_api:
                # For new API, we can optimize this with a lighter query
                response = api_client.get_profile_by_id(profile_id)
                
                if not response.success:
                    logger.error(f"Failed to fetch basic profile {profile_id}: {response.errors}")
                    return {
                        'success': False,
                        'error': response.errors[0] if response.errors else 'Unknown error',
                        'profile': None
                    }
                
                profile = response.data['profile']
                
                # Return only basic information
                basic_data = {
                    'id': profile.id,
                    'name': profile.name,
                    'descriptionShort': profile.description_short,
                    'logo': profile.logo,
                    'profileSector': {
                        'name': profile.profile_info.profile_sector.name
                    } if profile.profile_info and profile.profile_info.profile_sector else None
                }
                
                return {
                    'success': True,
                    'profile': basic_data
                }
            
                
                if not profile_data:
                    return {
                        'success': False,
                        'error': 'Profile not found',
                        'profile': None
                    }
                
                return {
                    'success': True,
                    'profile': profile_data
                }
                
        except Exception as e:
            logger.error(f"Error fetching basic profile {profile_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'profile': None
            }
    
    def format_profile_message(self, profile_data: Dict[str, Any], expanded: bool = False) -> str:
        """
        Format profile data into a message string
        
        Args:
            profile_data: Profile data dictionary
            expanded: Whether to show expanded information
            
        Returns:
            Formatted message string
        """
        if not profile_data:
            return "Profile data not available"
        
        try:
            message_parts = []
            
            # Basic information
            if profile_data.get('name'):
                message_parts.append(f"*Name:* {profile_data['name']}")
            
            if profile_data.get('profileSector', {}).get('name'):
                message_parts.append(f"*Sector:* {profile_data['profileSector']['name']}")
            
            if not expanded:
                # Short description for card view
                if profile_data.get('descriptionShort'):
                    message_parts.append(f"*Description:* {profile_data['descriptionShort']}")
            else:
                # Expanded information
                if profile_data.get('id'):
                    message_parts.append(f"*ID:* {profile_data['id']}")
                
                if profile_data.get('profileType', {}).get('name'):
                    message_parts.append(f"*Type:* {profile_data['profileType']['name']}")
                
                if profile_data.get('profileStatus', {}).get('name'):
                    message_parts.append(f"*Status:* {profile_data['profileStatus']['name']}")
                
                if profile_data.get('foundingDate'):
                    message_parts.append(f"*Founding Date:* {profile_data['foundingDate']}")
                
                if profile_data.get('slug'):
                    message_parts.append(f"*Slug:* {profile_data['slug']}")
                
                if profile_data.get('tagLine'):
                    message_parts.append(f"*Tag Line:* {profile_data['tagLine']}")
                
                if profile_data.get('descriptionLong'):
                    message_parts.append(f"*Description:* {profile_data['descriptionLong']}")
                
                # Related entities
                if profile_data.get('products'):
                    products = [p.get('name', 'Unknown') for p in profile_data['products'] if p.get('name')]
                    if products:
                        message_parts.append(f"*Products:* {', '.join(products)}")
                
                if profile_data.get('assets'):
                    assets = [a.get('name', 'Unknown') for a in profile_data['assets'] if a.get('name')]
                    if assets:
                        message_parts.append(f"*Assets:* {', '.join(assets)}")
            
            return '\n'.join(message_parts)
            
        except Exception as e:
            logger.error(f"Error formatting profile message: {e}")
            return "Error formatting profile information"
    
    def get_profile_urls(self, profile_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract and format URLs from profile data
        
        Args:
            profile_data: Profile data dictionary
            
        Returns:
            List of URL dictionaries with 'name' and 'url' keys
        """
        urls = []
        
        try:
            # Main website URL
            if profile_data.get('urlMain'):
                urls.append({
                    'name': 'Website',
                    'url': profile_data['urlMain']
                })
            
            # Documentation URL
            if profile_data.get('urlDocumentation'):
                urls.append({
                    'name': 'Documentation',
                    'url': profile_data['urlDocumentation']
                })
            
            # Whitepaper URL
            if profile_data.get('urlWhitepaper'):
                urls.append({
                    'name': 'Whitepaper',
                    'url': profile_data['urlWhitepaper']
                })
            
            # Blog URL
            if profile_data.get('urlBlog'):
                urls.append({
                    'name': 'Blog',
                    'url': profile_data['urlBlog']
                })
            
            # Social URLs
            if profile_data.get('socials'):
                for social in profile_data['socials']:
                    if social.get('url'):
                        urls.append({
                            'name': 'Social',
                            'url': social['url']
                        })
            
            return urls
            
        except Exception as e:
            logger.error(f"Error extracting profile URLs: {e}")
            return []
    
    def validate_profile_id(self, profile_id: str) -> bool:
        """
        Validate profile ID format
        
        Args:
            profile_id: Profile ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not profile_id:
            return False
        
        # Basic validation - can be expanded based on ID format requirements
        if len(profile_id.strip()) == 0:
            return False
        
        # Check for reasonable length
        if len(profile_id) > 100:
            return False
        
        return True
    
    def clear_profile_cache(self, profile_id: str = None):
        """
        Clear profile cache for specific ID or all profiles
        
        Args:
            profile_id: Specific profile ID to clear, or None for all
        """
        try:
            if profile_id:
                # Clear specific profile cache
                self.get_profile_by_id.cache_delete(profile_id)
                self.get_basic_profile_by_id.cache_delete(profile_id)
                logger.info(f"Cleared cache for profile {profile_id}")
            else:
                # Clear all profile cache
                self.get_profile_by_id.cache_clear()
                self.get_basic_profile_by_id.cache_clear()
                logger.info("Cleared all profile cache")
        except Exception as e:
            logger.error(f"Error clearing profile cache: {e}")


# Global service instance
profile_service = ProfileService()