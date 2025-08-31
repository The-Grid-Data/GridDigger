"""
Service layer for GridDigger Telegram Bot
"""
# Import our new enhanced services
from .profile_repository import ProfileRepository, profile_repository
from .profile_formatter import FormatterFactory, formatter_factory
from .enhanced_profile_service import EnhancedProfileService, enhanced_profile_service

# Import existing services for backward compatibility
try:
    from .search_service import SearchService, search_service
except ImportError:
    SearchService = None
    search_service = None

try:
    from .filter_service import FilterService
except ImportError:
    FilterService = None

__all__ = [
    'ProfileRepository',
    'profile_repository',
    'FormatterFactory',
    'formatter_factory',
    'EnhancedProfileService',
    'enhanced_profile_service',
    'SearchService',
    'search_service',
    'FilterService'
]