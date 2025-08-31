"""
Profile-related data models
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from .common import URL, Social, Asset, Product, Entity


@dataclass
class ProfileSector:
    """Profile sector model"""
    id: Optional[int] = None
    name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProfileSector':
        """Create ProfileSector from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name')
        )


@dataclass
class ProfileType:
    """Profile type model"""
    id: Optional[int] = None
    name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProfileType':
        """Create ProfileType from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name')
        )


@dataclass
class ProfileStatus:
    """Profile status model"""
    id: Optional[int] = None
    name: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProfileStatus':
        """Create ProfileStatus from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name')
        )


@dataclass
class ProfileInfo:
    """Profile information model for new GraphQL structure"""
    name: str
    tag_line: Optional[str] = None
    description_short: Optional[str] = None
    description_long: Optional[str] = None
    logo: Optional[str] = None
    founding_date: Optional[datetime] = None
    slug: Optional[str] = None
    profile_sector: Optional[ProfileSector] = None
    profile_type: Optional[ProfileType] = None
    profile_status: Optional[ProfileStatus] = None
    urls: List[URL] = None
    
    def __post_init__(self):
        if self.urls is None:
            self.urls = []
    
    @property
    def main_url(self) -> Optional[str]:
        """Get the main website URL"""
        if not self.urls:
            return None
        
        # Look for main/website URL first
        for url in self.urls:
            if url.url_type and url.url_type.lower() in ['main', 'website', 'homepage']:
                return url.url
        
        # Return first URL if no main URL found
        return self.urls[0].url if self.urls else None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProfileInfo':
        """Create ProfileInfo from dictionary"""
        founding_date = None
        if data.get('foundingDate'):
            try:
                founding_date = datetime.fromisoformat(data['foundingDate'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        urls = []
        if data.get('urls'):
            urls = [URL.from_dict(url_data) for url_data in data['urls']]
        
        return cls(
            name=data.get('name', ''),
            tag_line=data.get('tagLine'),
            description_short=data.get('descriptionShort'),
            description_long=data.get('descriptionLong'),
            logo=data.get('logo'),
            founding_date=founding_date,
            slug=data.get('slug'),
            profile_sector=ProfileSector.from_dict(data['profileSector']) if data.get('profileSector') else None,
            profile_type=ProfileType.from_dict(data['profileType']) if data.get('profileType') else None,
            profile_status=ProfileStatus.from_dict(data['profileStatus']) if data.get('profileStatus') else None,
            urls=urls
        )


@dataclass
class ProfileRoot:
    """Root data containing related entities"""
    assets: List[Asset] = None
    socials: List[Social] = None
    entities: List[Entity] = None
    products: List[Product] = None
    
    def __post_init__(self):
        if self.assets is None:
            self.assets = []
        if self.socials is None:
            self.socials = []
        if self.entities is None:
            self.entities = []
        if self.products is None:
            self.products = []
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProfileRoot':
        """Create ProfileRoot from dictionary"""
        assets = []
        if data.get('assets'):
            assets = [Asset.from_dict(asset_data) for asset_data in data['assets']]
        
        socials = []
        if data.get('socials'):
            socials = [Social.from_dict(social_data) for social_data in data['socials']]
        
        entities = []
        if data.get('entities'):
            entities = [Entity.from_dict(entity_data) for entity_data in data['entities']]
        
        products = []
        if data.get('products'):
            products = [Product.from_dict(product_data) for product_data in data['products']]
        
        return cls(
            assets=assets,
            socials=socials,
            entities=entities,
            products=products
        )


@dataclass
class Profile:
    """Complete profile model combining ProfileInfo and ProfileRoot"""
    id: Optional[str] = None
    slug: Optional[str] = None
    profile_info: Optional[ProfileInfo] = None
    root: Optional[ProfileRoot] = None
    
    @property
    def name(self) -> str:
        """Get profile name"""
        return self.profile_info.name if self.profile_info else ''
    
    @property
    def description_short(self) -> Optional[str]:
        """Get short description"""
        return self.profile_info.description_short if self.profile_info else None
    
    @property
    def main_url(self) -> Optional[str]:
        """Get main URL"""
        return self.profile_info.main_url if self.profile_info else None
    
    @property
    def logo(self) -> Optional[str]:
        """Get logo URL"""
        return self.profile_info.logo if self.profile_info else None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Profile':
        """Create Profile from dictionary"""
        profile_info = None
        if data.get('profileInfos') and len(data['profileInfos']) > 0:
            profile_info_data = data['profileInfos'][0]
            profile_info = ProfileInfo.from_dict(profile_info_data)
        
        root = None
        if profile_info and data.get('profileInfos', [{}])[0].get('root'):
            root = ProfileRoot.from_dict(data['profileInfos'][0]['root'])
        
        return cls(
            id=data.get('id'),
            slug=data.get('slug'),
            profile_info=profile_info,
            root=root
        )
    
    def to_legacy_format(self) -> dict:
        """Convert to legacy format for backward compatibility"""
        if not self.profile_info:
            return {}
        
        return {
            'id': self.id,
            'name': self.profile_info.name,
            'urlMain': self.profile_info.main_url,
            'foundingDate': self.profile_info.founding_date.isoformat() if self.profile_info.founding_date else None,
            'descriptionShort': self.profile_info.description_short,
            'descriptionLong': self.profile_info.description_long,
            'tagLine': self.profile_info.tag_line,
            'logo': self.profile_info.logo,
            'slug': self.profile_info.slug,
            'profileType': {'name': self.profile_info.profile_type.name} if self.profile_info.profile_type else None,
            'profileSector': {'name': self.profile_info.profile_sector.name} if self.profile_info.profile_sector else None,
            'profileStatus': {'name': self.profile_info.profile_status.name} if self.profile_info.profile_status else None,
            'assets': [{'name': asset.name} for asset in self.root.assets] if self.root else [],
            'socials': [{'url': social.url} for social in self.root.socials] if self.root else [],
            'entities': [{'name': entity.name} for entity in self.root.entities] if self.root else [],
            'products': [{'name': product.name} for product in self.root.products] if self.root else []
        }