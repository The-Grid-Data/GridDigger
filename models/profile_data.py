"""
Enhanced profile data models with null safety built-in
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class ProfileSector:
    """Profile sector information"""
    id: Optional[str] = None
    name: str = "Unknown"


@dataclass
class ProfileType:
    """Profile type information"""
    id: Optional[str] = None
    name: str = "Unknown"


@dataclass
class ProfileStatus:
    """Profile status information"""
    id: Optional[str] = None
    name: str = "Unknown"


@dataclass
class ProfileURL:
    """Profile URL information"""
    url: str
    url_type: str = "Unknown"
    url_type_id: Optional[str] = None


@dataclass
class Asset:
    """Asset information"""
    id: Optional[str] = None
    name: str = "Unknown"
    ticker: Optional[str] = None
    description: Optional[str] = None
    asset_type: Optional[str] = None
    asset_status: Optional[str] = None


@dataclass
class Product:
    """Product information"""
    id: Optional[str] = None
    name: str = "Unknown"
    description: Optional[str] = None
    launch_date: Optional[str] = None
    is_main_product: bool = False
    product_type: Optional[str] = None
    product_status: Optional[str] = None


@dataclass
class Entity:
    """Entity information"""
    id: Optional[str] = None
    name: str = "Unknown"
    trade_name: Optional[str] = None
    entity_type: Optional[str] = None
    country: Optional[str] = None


@dataclass
class ProfileData:
    """Core profile data structure with null safety built-in"""
    id: str
    name: str = "Unknown"
    slug: str = ""
    description_short: Optional[str] = None
    description_long: Optional[str] = None
    tag_line: Optional[str] = None
    logo: Optional[str] = None
    founding_date: Optional[str] = None
    
    # Related entities (with null safety built-in)
    sector: Optional[ProfileSector] = None
    profile_type: Optional[ProfileType] = None
    status: Optional[ProfileStatus] = None
    urls: List[ProfileURL] = field(default_factory=list)
    assets: List[Asset] = field(default_factory=list)
    products: List[Product] = field(default_factory=list)
    entities: List[Entity] = field(default_factory=list)
    
    @classmethod
    def from_api_response(cls, raw_data: Dict[str, Any], profile_id: str = None) -> 'ProfileData':
        """Create ProfileData from API response with null safety"""
        if not raw_data:
            return cls(id=profile_id or "", name="Unknown")
        
        # Use provided profile_id first, then try to extract from API response
        if not profile_id:
            profile_id = raw_data.get('id', '')
            if not profile_id and raw_data.get('root', {}).get('id'):
                profile_id = raw_data['root']['id']
        
        # Ensure we have a valid profile_id
        if not profile_id:
            profile_id = ""
        
        # Extract sector information safely
        sector = None
        if raw_data.get('profileSector'):
            sector_data = raw_data['profileSector']
            sector = ProfileSector(
                id=sector_data.get('id'),
                name=sector_data.get('name', 'Unknown')
            )
        
        # Extract profile type safely
        profile_type = None
        if raw_data.get('profileType'):
            type_data = raw_data['profileType']
            profile_type = ProfileType(
                id=type_data.get('id'),
                name=type_data.get('name', 'Unknown')
            )
        
        # Extract status safely
        status = None
        if raw_data.get('profileStatus'):
            status_data = raw_data['profileStatus']
            status = ProfileStatus(
                id=status_data.get('id'),
                name=status_data.get('name', 'Unknown')
            )
        
        # Extract URLs safely
        urls = []
        if raw_data.get('urls') and isinstance(raw_data['urls'], list):
            for url_data in raw_data['urls']:
                if url_data and url_data.get('url'):
                    url_type_name = "Unknown"
                    if url_data.get('urlType') and url_data['urlType'].get('name'):
                        url_type_name = url_data['urlType']['name']
                    
                    urls.append(ProfileURL(
                        url=url_data['url'],
                        url_type=url_type_name,
                        url_type_id=url_data.get('urlType', {}).get('id')
                    ))
        
        # Extract root data safely
        root_data = raw_data.get('root', {})
        
        # Extract assets safely
        assets = []
        if root_data.get('assets') and isinstance(root_data['assets'], list):
            for asset_data in root_data['assets']:
                if asset_data:
                    assets.append(Asset(
                        id=asset_data.get('id'),
                        name=asset_data.get('name', 'Unknown'),
                        ticker=asset_data.get('ticker'),
                        description=asset_data.get('description'),
                        asset_type=asset_data.get('assetType', {}).get('name') if asset_data.get('assetType') else None,
                        asset_status=asset_data.get('assetStatus', {}).get('name') if asset_data.get('assetStatus') else None
                    ))
        
        # Extract products safely
        products = []
        if root_data.get('products') and isinstance(root_data['products'], list):
            for product_data in root_data['products']:
                if product_data:
                    products.append(Product(
                        id=product_data.get('id'),
                        name=product_data.get('name', 'Unknown'),
                        description=product_data.get('description'),
                        launch_date=product_data.get('launchDate'),
                        is_main_product=product_data.get('isMainProduct', False),
                        product_type=product_data.get('productType', {}).get('name') if product_data.get('productType') else None,
                        product_status=product_data.get('productStatus', {}).get('name') if product_data.get('productStatus') else None
                    ))
        
        # Extract entities safely
        entities = []
        if root_data.get('entities') and isinstance(root_data['entities'], list):
            for entity_data in root_data['entities']:
                if entity_data:
                    entities.append(Entity(
                        id=entity_data.get('id'),
                        name=entity_data.get('name', 'Unknown'),
                        trade_name=entity_data.get('tradeName'),
                        entity_type=entity_data.get('entityType', {}).get('name') if entity_data.get('entityType') else None,
                        country=entity_data.get('country', {}).get('name') if entity_data.get('country') else None
                    ))
        
        return cls(
            id=profile_id,
            name=raw_data.get('name', 'Unknown'),
            slug=raw_data.get('slug', ''),
            description_short=raw_data.get('descriptionShort'),
            description_long=raw_data.get('descriptionLong'),
            tag_line=raw_data.get('tagLine'),
            logo=raw_data.get('logo'),
            founding_date=raw_data.get('foundingDate'),
            sector=sector,
            profile_type=profile_type,
            status=status,
            urls=urls,
            assets=assets,
            products=products,
            entities=entities
        )


@dataclass
class FormattedProfile:
    """Formatted profile ready for display"""
    message_text: str
    buttons: List[List] = field(default_factory=list)  # List of button rows
    has_media: bool = False
    media_url: Optional[str] = None
    
    def get_inline_keyboard_markup(self):
        """Convert buttons to InlineKeyboardMarkup"""
        from telegram import InlineKeyboardMarkup
        return InlineKeyboardMarkup(self.buttons) if self.buttons else None