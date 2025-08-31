"""
Search-related data models
"""
from dataclasses import dataclass
from typing import List, Optional
from .profile import ProfileInfo


@dataclass
class SearchRoot:
    """Search result root model for new GraphQL structure"""
    id: str
    slug: Optional[str] = None
    profile_infos: List[ProfileInfo] = None
    
    def __post_init__(self):
        if self.profile_infos is None:
            self.profile_infos = []
    
    @property
    def name(self) -> str:
        """Get profile name from first profile info"""
        return self.profile_infos[0].name if self.profile_infos else ''
    
    @property
    def description_short(self) -> Optional[str]:
        """Get short description from first profile info"""
        return self.profile_infos[0].description_short if self.profile_infos else None
    
    @property
    def logo(self) -> Optional[str]:
        """Get logo from first profile info"""
        return self.profile_infos[0].logo if self.profile_infos else None
    
    @property
    def main_url(self) -> Optional[str]:
        """Get main URL from first profile info"""
        return self.profile_infos[0].main_url if self.profile_infos else None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SearchRoot':
        """Create SearchRoot from dictionary"""
        profile_infos = []
        if data.get('profileInfos'):
            profile_infos = [ProfileInfo.from_dict(info) for info in data['profileInfos']]
        
        return cls(
            id=data.get('id', ''),
            slug=data.get('slug'),
            profile_infos=profile_infos
        )
    
    def to_legacy_format(self) -> dict:
        """Convert to legacy search result format"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.main_url,
            'description': self.description_short
        }


@dataclass
class SearchResult:
    """Search results container"""
    roots: List[SearchRoot] = None
    total_count: int = 0
    
    def __post_init__(self):
        if self.roots is None:
            self.roots = []
        if self.total_count == 0:
            self.total_count = len(self.roots)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SearchResult':
        """Create SearchResult from GraphQL response"""
        roots = []
        if data.get('data', {}).get('roots'):
            roots = [SearchRoot.from_dict(root) for root in data['data']['roots']]
        
        return cls(
            roots=roots,
            total_count=len(roots)
        )
    
    def to_legacy_format(self) -> dict:
        """Convert to legacy search result format"""
        profiles = [root.to_legacy_format() for root in self.roots]
        return {
            'body': {
                'search_result': {
                    'profiles': profiles
                }
            }
        }
    
    def get_profiles_list(self) -> List[dict]:
        """Get list of profiles in legacy format"""
        return [root.to_legacy_format() for root in self.roots]


@dataclass
class SearchFilter:
    """Search filter model"""
    field: str
    value: str
    operator: str = "_contains"
    
    def to_graphql_clause(self) -> str:
        """Convert to GraphQL where clause"""
        if self.operator == "_contains":
            return f'{self.field}: {{_contains: "{self.value}"}}'
        elif self.operator == "_eq":
            return f'{self.field}: {{_eq: {self.value}}}'
        elif self.operator == "_ilike":
            return f'{self.field}: {{_ilike: "%{self.value}%"}}'
        else:
            return f'{self.field}: {{{self.operator}: "{self.value}"}}'


@dataclass
class SearchQuery:
    """Search query builder"""
    search_term: Optional[str] = None
    filters: List[SearchFilter] = None
    limit: int = 20
    offset: int = 0
    
    def __post_init__(self):
        if self.filters is None:
            self.filters = []
    
    def add_filter(self, field: str, value: str, operator: str = "_contains"):
        """Add a search filter"""
        self.filters.append(SearchFilter(field, value, operator))
    
    def build_where_clause(self) -> str:
        """Build GraphQL where clause"""
        clauses = []
        
        # Add search term clause
        if self.search_term:
            search_clause = f"""_or: [
                {{profileInfos: {{name: {{_contains: "{self.search_term}"}}}}}},
                {{assets: {{ticker: {{_contains: "{self.search_term}"}}}}}}
            ]"""
            clauses.append(search_clause)
        
        # Add filter clauses
        for filter_obj in self.filters:
            clauses.append(filter_obj.to_graphql_clause())
        
        if clauses:
            return f"where: {{{', '.join(clauses)}}}"
        return ""
    
    def build_query(self) -> str:
        """Build complete GraphQL query"""
        where_clause = self.build_where_clause()
        
        return f"""
        query SearchForProfileNameOrAssetTicker {{
            roots({where_clause}, limit: {self.limit}, offset: {self.offset}) {{
                id
                slug
                profileInfos {{
                    name
                    descriptionShort
                    logo
                    urls(order_by: {{urlTypeId: Asc}}) {{
                        url
                        urlType {{ name }}
                    }}
                }}
            }}
        }}
        """