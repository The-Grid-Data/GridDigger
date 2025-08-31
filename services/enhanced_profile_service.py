"""
Enhanced Profile Service - Orchestrates profile operations with formatting
"""
import logging
from typing import Optional
from models.profile_data import ProfileData, FormattedProfile
from services.profile_repository import ProfileRepository
from services.profile_formatter import FormatterFactory

logger = logging.getLogger(__name__)


class EnhancedProfileService:
    """Service that orchestrates profile operations with formatting"""
    
    def __init__(self, repository: ProfileRepository, formatter_factory: FormatterFactory):
        self.repository = repository
        self.formatter_factory = formatter_factory
    
    def get_profile_card(self, profile_id: str) -> Optional[FormattedProfile]:
        """
        Get profile formatted for enhanced card display (includes products and assets)
        
        Args:
            profile_id: Profile ID to fetch and format
            
        Returns:
            FormattedProfile for enhanced card display or None if not found
        """
        try:
            logger.debug(f"Getting enhanced profile card for ID: {profile_id}")
            
            # Validate profile ID
            if not self.repository.validate_profile_id(profile_id):
                logger.warning(f"Invalid profile ID: {profile_id}")
                return None
            
            # Get card-optimized profile data (includes products and assets)
            profile_data = self.repository.get_card_profile(profile_id)
            
            if not profile_data:
                logger.warning(f"Profile not found for card display: {profile_id}")
                return None
            
            # Format for enhanced card display
            formatter = self.formatter_factory.get_formatter('card')
            formatted_profile = formatter.format(profile_data)
            
            logger.info(f"Successfully formatted enhanced profile card for: {profile_data.name}")
            return formatted_profile
            
        except Exception as e:
            logger.error(f"Error getting enhanced profile card for {profile_id}: {e}")
            return None
    
    def get_expanded_profile(self, profile_id: str) -> Optional[FormattedProfile]:
        """
        Get profile formatted for expanded display
        
        Args:
            profile_id: Profile ID to fetch and format
            
        Returns:
            FormattedProfile for expanded display or None if not found
        """
        try:
            logger.debug(f"Getting expanded profile for ID: {profile_id}")
            
            # Validate profile ID
            if not self.repository.validate_profile_id(profile_id):
                logger.warning(f"Invalid profile ID: {profile_id}")
                return None
            
            # Get full profile data
            profile_data = self.repository.get_full_profile(profile_id)
            
            if not profile_data:
                logger.warning(f"Profile not found for expanded display: {profile_id}")
                return None
            
            # Format for expanded display
            formatter = self.formatter_factory.get_formatter('expanded')
            formatted_profile = formatter.format(profile_data)
            
            logger.info(f"Successfully formatted expanded profile for: {profile_data.name}")
            return formatted_profile
            
        except Exception as e:
            logger.error(f"Error getting expanded profile for {profile_id}: {e}")
            return None
    
    def get_compact_profile(self, profile_id: str) -> Optional[FormattedProfile]:
        """
        Get profile formatted for compact display
        
        Args:
            profile_id: Profile ID to fetch and format
            
        Returns:
            FormattedProfile for compact display or None if not found
        """
        try:
            logger.debug(f"Getting compact profile for ID: {profile_id}")
            
            # Validate profile ID
            if not self.repository.validate_profile_id(profile_id):
                logger.warning(f"Invalid profile ID: {profile_id}")
                return None
            
            # Get basic profile data
            profile_data = self.repository.get_basic_profile(profile_id)
            
            if not profile_data:
                logger.warning(f"Profile not found for compact display: {profile_id}")
                return None
            
            # Format for compact display
            formatter = self.formatter_factory.get_formatter('compact')
            formatted_profile = formatter.format(profile_data)
            
            logger.debug(f"Successfully formatted compact profile for: {profile_data.name}")
            return formatted_profile
            
        except Exception as e:
            logger.error(f"Error getting compact profile for {profile_id}: {e}")
            return None
    
    def get_custom_formatted_profile(self, profile_id: str, format_type: str) -> Optional[FormattedProfile]:
        """
        Get profile with custom formatting
        
        Args:
            profile_id: Profile ID to fetch and format
            format_type: Custom format type
            
        Returns:
            FormattedProfile with custom formatting or None if not found
        """
        try:
            logger.debug(f"Getting custom formatted profile for ID: {profile_id}, format: {format_type}")
            
            # Validate profile ID
            if not self.repository.validate_profile_id(profile_id):
                logger.warning(f"Invalid profile ID: {profile_id}")
                return None
            
            # Get appropriate profile data based on format needs
            if format_type in ['expanded', 'detailed']:
                profile_data = self.repository.get_full_profile(profile_id)
            elif format_type == 'card':
                profile_data = self.repository.get_card_profile(profile_id)
            else:
                profile_data = self.repository.get_basic_profile(profile_id)
            
            if not profile_data:
                logger.warning(f"Profile not found for custom format: {profile_id}")
                return None
            
            # Format with custom formatter
            formatter = self.formatter_factory.get_formatter(format_type)
            formatted_profile = formatter.format(profile_data)
            
            logger.debug(f"Successfully formatted profile with {format_type} format for: {profile_data.name}")
            return formatted_profile
            
        except Exception as e:
            logger.error(f"Error getting custom formatted profile for {profile_id}: {e}")
            return None
    
    def get_raw_profile_data(self, profile_id: str, full_data: bool = False) -> Optional[ProfileData]:
        """
        Get raw profile data without formatting
        
        Args:
            profile_id: Profile ID to fetch
            full_data: Whether to fetch full profile data or basic
            
        Returns:
            ProfileData object or None if not found
        """
        try:
            logger.debug(f"Getting raw profile data for ID: {profile_id}, full: {full_data}")
            
            # Validate profile ID
            if not self.repository.validate_profile_id(profile_id):
                logger.warning(f"Invalid profile ID: {profile_id}")
                return None
            
            if full_data:
                return self.repository.get_full_profile(profile_id)
            else:
                return self.repository.get_card_profile(profile_id)
                
        except Exception as e:
            logger.error(f"Error getting raw profile data for {profile_id}: {e}")
            return None
    
    def clear_profile_cache(self, profile_id: Optional[str] = None):
        """
        Clear profile cache
        
        Args:
            profile_id: Specific profile ID to clear, or None for all
        """
        try:
            self.repository.clear_cache(profile_id)
            logger.info(f"Profile cache cleared for: {profile_id or 'all profiles'}")
        except Exception as e:
            logger.error(f"Error clearing profile cache: {e}")
    
    def get_available_formats(self) -> list:
        """Get list of available formatting options"""
        return self.formatter_factory.get_available_formats()
    
    def register_custom_formatter(self, format_name: str, formatter_class):
        """
        Register a custom formatter
        
        Args:
            format_name: Name for the custom format
            formatter_class: Formatter class that inherits from ProfileFormatter
        """
        try:
            self.formatter_factory.register_formatter(format_name, formatter_class)
            logger.info(f"Registered custom formatter: {format_name}")
        except Exception as e:
            logger.error(f"Error registering custom formatter {format_name}: {e}")
            raise


# Create service instances
from services.profile_repository import profile_repository
from services.profile_formatter import formatter_factory

enhanced_profile_service = EnhancedProfileService(profile_repository, formatter_factory)