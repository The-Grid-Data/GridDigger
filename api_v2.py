"""
New GraphQL API client for GridDigger Telegram Bot
Implements the new endpoint structure with improved error handling and performance
"""
import json
import logging
import time
from typing import Optional, List, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Config
from models.search import SearchResult, SearchQuery
from models.profile import Profile
from models.common import APIResponse

# Set up logging
logger = logging.getLogger(__name__)


class GraphQLClient:
    """Enhanced GraphQL client with connection pooling and retry logic"""
    
    def __init__(self):
        self.endpoint = Config.get_graphql_endpoint()
        self.headers = Config.get_graphql_headers()
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create HTTP session with connection pooling and retry strategy"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=Config.MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=Config.CONNECTION_POOL_SIZE,
            pool_maxsize=Config.CONNECTION_POOL_SIZE,
            max_retries=retry_strategy
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(self.headers)
        
        return session
    
    def execute_query(self, query: str, variables: Optional[Dict] = None) -> APIResponse:
        """Execute GraphQL query with error handling and logging"""
        start_time = time.time()
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            logger.debug(f"Executing GraphQL query: {query[:100]}...")
            
            response = self.session.post(
                self.endpoint,
                json=payload,
                timeout=Config.REQUEST_TIMEOUT
            )
            
            execution_time = time.time() - start_time
            logger.debug(f"Query executed in {execution_time:.2f}s")
            
            response.raise_for_status()
            data = response.json()
            
            # Check for GraphQL errors
            if 'errors' in data:
                error_messages = [error.get('message', 'Unknown error') for error in data['errors']]
                logger.error(f"GraphQL errors: {error_messages}")
                return APIResponse.error_response(
                    errors=error_messages,
                    message="GraphQL query failed"
                )
            
            return APIResponse.success_response(
                data=data,
                message=f"Query executed successfully in {execution_time:.2f}s"
            )
            
        except requests.exceptions.Timeout:
            logger.error(f"Query timeout after {Config.REQUEST_TIMEOUT}s")
            return APIResponse.error_response(
                errors=["Request timeout"],
                message="Query took too long to execute"
            )
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return APIResponse.error_response(
                errors=["Connection failed"],
                message="Unable to connect to GraphQL endpoint"
            )
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return APIResponse.error_response(
                errors=[f"HTTP {response.status_code}"],
                message="Server returned an error"
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return APIResponse.error_response(
                errors=["Invalid response format"],
                message="Server returned invalid JSON"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return APIResponse.error_response(
                errors=["Unexpected error occurred"],
                message=str(e)
            )


class GridAPIv2:
    """New Grid API client implementing the migration plan"""
    
    def __init__(self):
        self.client = GraphQLClient()
        
    def search_profiles(self, search_term: str, limit: int = 20, offset: int = 0) -> APIResponse:
        """
        Search for profiles using the new GraphQL endpoint
        
        Args:
            search_term: Search term for profile names or asset tickers
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            APIResponse containing SearchResult or error information
        """
        query = SearchQuery(
            search_term=search_term,
            limit=limit,
            offset=offset
        )
        
        graphql_query = query.build_query()
        
        response = self.client.execute_query(graphql_query)
        
        if not response.success:
            return response
        
        try:
            search_result = SearchResult.from_dict(response.data)
            return APIResponse.success_response(
                data={'search_result': search_result},
                message=f"Found {search_result.total_count} results"
            )
        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
            return APIResponse.error_response(
                errors=["Failed to parse search results"],
                message=str(e)
            )
    
    def get_profile_by_id(self, profile_id: str) -> APIResponse:
        """
        Get detailed profile information by ID
        
        Args:
            profile_id: Profile ID or slug
            
        Returns:
            APIResponse containing Profile or error information
        """
        query = """
        query getProfileData($profileId: String!) {
            profileInfos(
                limit: 1, 
                offset: 0, 
                where: {
                    _or: [
                        {root: {id: {_eq: $profileId}}},
                        {root: {slug: {_eq: $profileId}}}
                    ]
                }
            ) {
                name
                tagLine
                descriptionShort
                descriptionLong
                logo
                foundingDate
                slug
                profileSector { 
                    id
                    name 
                }
                profileType { 
                    id
                    name 
                }
                profileStatus { 
                    id
                    name 
                }
                urls(order_by: {urlTypeId: Asc}) {
                    url
                    urlType { name }
                }
                root {
                    id
                    slug
                    assets {
                        id
                        name
                        ticker
                        assetType { name }
                        assetStandardSupport { name }
                    }
                    socials {
                        url
                        platform
                    }
                    entities {
                        id
                        name
                        entityType { name }
                        country { Name }
                    }
                    products {
                        id
                        name
                        launchDate
                        productType { name }
                        productStatus { name }
                    }
                }
            }
        }
        """
        
        variables = {'profileId': profile_id}
        response = self.client.execute_query(query, variables)
        
        if not response.success:
            return response
        
        try:
            profile_data = response.data.get('data', {}).get('profileInfos', [])
            
            if not profile_data:
                return APIResponse.error_response(
                    errors=["Profile not found"],
                    message=f"No profile found with ID: {profile_id}"
                )
            
            # Reconstruct the profile data structure
            profile_info = profile_data[0]
            root_data = profile_info.get('root', {})
            
            # Create the expected structure for Profile.from_dict
            structured_data = {
                'id': root_data.get('id'),
                'slug': root_data.get('slug'),
                'profileInfos': [profile_info]
            }
            
            profile = Profile.from_dict(structured_data)
            
            return APIResponse.success_response(
                data={'profile': profile},
                message="Profile retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error parsing profile data: {e}")
            return APIResponse.error_response(
                errors=["Failed to parse profile data"],
                message=str(e)
            )
    
    def get_filter_options(self, filter_type: str) -> APIResponse:
        """
        Get available options for a specific filter type
        
        Args:
            filter_type: Type of filter (profileTypes, profileSectors, etc.)
            
        Returns:
            APIResponse containing filter options
        """
        # Map filter types to GraphQL queries
        filter_queries = {
            'profileTypes': 'profileTypes { id name }',
            'profileSectors': 'profileSectors { id name }',
            'profileStatuses': 'profileStatuses { id name }',
            'productTypes': 'productTypes { id name }',
            'productStatuses': 'productStatus { id name }',
            'assetTypes': 'assetTypes { id name }',
            'assetStandards': 'assetStandardSupport { id name }',
            'entityTypes': 'entityTypes { id name }'
        }
        
        if filter_type not in filter_queries:
            return APIResponse.error_response(
                errors=["Invalid filter type"],
                message=f"Filter type '{filter_type}' is not supported"
            )
        
        query = f"query {{ {filter_queries[filter_type]} }}"
        
        response = self.client.execute_query(query)
        
        if not response.success:
            return response
        
        try:
            filter_data = response.data.get('data', {}).get(filter_type, [])
            return APIResponse.success_response(
                data={'options': filter_data},
                message=f"Retrieved {len(filter_data)} {filter_type} options"
            )
        except Exception as e:
            logger.error(f"Error parsing filter options: {e}")
            return APIResponse.error_response(
                errors=["Failed to parse filter options"],
                message=str(e)
            )


# Global API instance
grid_api_v2 = GridAPIv2()


# Backward compatibility functions
def search_thegrid_v2(search_term: str, limit: int = 20) -> List[dict]:
    """
    Search function with backward compatibility
    Returns list of profiles in legacy format
    """
    response = grid_api_v2.search_profiles(search_term, limit)
    
    if not response.success:
        logger.error(f"Search failed: {response.errors}")
        return []
    
    search_result = response.data['search_result']
    return search_result.get_profiles_list()


def fetch_thegrid_v2(profile_id: str) -> dict:
    """
    Fetch profile function with backward compatibility
    Returns profile in legacy format
    """
    response = grid_api_v2.get_profile_by_id(profile_id)
    
    if not response.success:
        logger.error(f"Profile fetch failed: {response.errors}")
        return {}
    
    profile = response.data['profile']
    return profile.to_legacy_format()


def get_filter_options_v2(filter_type: str) -> List[dict]:
    """
    Get filter options with backward compatibility
    """
    response = grid_api_v2.get_filter_options(filter_type)
    
    if not response.success:
        logger.error(f"Filter options fetch failed: {response.errors}")
        return []
    
    return response.data['options']