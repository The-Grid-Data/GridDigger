"""
Profile Repository - Centralized data access with caching and null safety
"""
import logging
from typing import Optional, Dict, Any
from cache import cached
from models.profile_data import ProfileData
import api

logger = logging.getLogger(__name__)


class ProfileRepository:
    """Repository for profile data access with built-in caching and null safety"""
    
    def __init__(self):
        pass
    
    @cached(prefix="profile_full", ttl=300)  # Cache for 5 minutes
    def get_full_profile(self, profile_id: str) -> Optional[ProfileData]:
        """
        Get complete profile data with null safety built-in
        
        Args:
            profile_id: Profile ID to fetch
            
        Returns:
            ProfileData object or None if not found/error
        """
        try:
            logger.debug(f"Fetching full profile data for ID: {profile_id}")
            
            # Use existing API function but with enhanced error handling
            raw_data = api.get_full_profile_data_by_id(profile_id)
            
            if not raw_data:
                logger.warning(f"No profile data returned for ID: {profile_id}")
                return None
            
            # Convert to our enhanced ProfileData model with null safety
            # Pass the profile_id explicitly since API response doesn't contain it
            profile_data = ProfileData.from_api_response(raw_data, profile_id=profile_id)
            
            logger.debug(f"Successfully converted profile data for: {profile_data.name}")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error fetching profile {profile_id}: {e}")
            return None
    
    @cached(prefix="profile_card", ttl=180)  # Cache for 3 minutes
    def get_card_profile(self, profile_id: str) -> Optional[ProfileData]:
        """
        Get profile data optimized for card display (includes products and assets)
        
        Args:
            profile_id: Profile ID to fetch
            
        Returns:
            ProfileData object with card-optimized info or None if not found/error
        """
        try:
            logger.debug(f"Fetching card profile data for ID: {profile_id}")
            
            # For enhanced cards, we need full data to get products and assets
            # Use the full profile API to get complete information
            raw_data = api.get_full_profile_data_by_id(profile_id)
            
            if not raw_data:
                logger.warning(f"No card profile data returned for ID: {profile_id}")
                return None
            
            # Convert to ProfileData model
            # Pass the profile_id explicitly since API response doesn't contain it
            profile_data = ProfileData.from_api_response(raw_data, profile_id=profile_id)
            
            logger.debug(f"Successfully converted card profile data for: {profile_data.name}")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error fetching card profile {profile_id}: {e}")
            return None

    @cached(prefix="profile_basic", ttl=180)  # Cache for 3 minutes
    def get_basic_profile(self, profile_id: str) -> Optional[ProfileData]:
        """
        Get basic profile data (legacy method for backward compatibility)
        
        Args:
            profile_id: Profile ID to fetch
            
        Returns:
            ProfileData object with basic info or None if not found/error
        """
        try:
            logger.debug(f"Fetching basic profile data for ID: {profile_id}")
            
            # Use existing API function
            raw_data = api.get_profile_data_by_id(profile_id)
            
            if not raw_data:
                logger.warning(f"No basic profile data returned for ID: {profile_id}")
                return None
            
            # Convert to ProfileData model
            # Pass the profile_id explicitly since API response doesn't contain it
            profile_data = ProfileData.from_api_response(raw_data, profile_id=profile_id)
            
            logger.debug(f"Successfully converted basic profile data for: {profile_data.name}")
            return profile_data
            
        except Exception as e:
            logger.error(f"Error fetching basic profile {profile_id}: {e}")
            return None
    
    def clear_cache(self, profile_id: Optional[str] = None):
        """
        Clear profile cache for specific ID or all profiles
        
        Args:
            profile_id: Specific profile ID to clear, or None for all
        """
        try:
            if profile_id:
                # Clear specific profile cache
                self.get_full_profile.cache_delete(profile_id)
                self.get_basic_profile.cache_delete(profile_id)
                self.get_card_profile.cache_delete(profile_id)
                logger.info(f"Cleared cache for profile {profile_id}")
            else:
                # Clear all profile cache
                self.get_full_profile.cache_clear()
                self.get_basic_profile.cache_clear()
                self.get_card_profile.cache_clear()
                logger.info("Cleared all profile cache")
        except Exception as e:
            logger.error(f"Error clearing profile cache: {e}")
    
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
        
        # Basic validation
        if len(profile_id.strip()) == 0:
            return False
        
        # Check for reasonable length
        if len(profile_id) > 100:
            return False
        
        return True


# Global repository instance
profile_repository = ProfileRepository()