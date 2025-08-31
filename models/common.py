"""
Common data models shared across the application
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class URL:
    """URL model with type information"""
    url: str
    url_type: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'URL':
        """Create URL from dictionary"""
        return cls(
            url=data.get('url', ''),
            url_type=data.get('urlType', {}).get('name') if data.get('urlType') else None
        )


@dataclass
class Social:
    """Social media link model"""
    url: str
    platform: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Social':
        """Create Social from dictionary"""
        return cls(
            url=data.get('url', ''),
            platform=data.get('platform')
        )


@dataclass
class Asset:
    """Asset model"""
    id: Optional[int] = None
    name: Optional[str] = None
    ticker: Optional[str] = None
    asset_type: Optional[str] = None
    standard: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Asset':
        """Create Asset from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            ticker=data.get('ticker'),
            asset_type=data.get('assetType', {}).get('name') if data.get('assetType') else None,
            standard=data.get('assetStandardSupport', {}).get('name') if data.get('assetStandardSupport') else None
        )


@dataclass
class Product:
    """Product model"""
    id: Optional[int] = None
    name: Optional[str] = None
    product_type: Optional[str] = None
    status: Optional[str] = None
    launch_date: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """Create Product from dictionary"""
        launch_date = None
        if data.get('launchDate'):
            try:
                launch_date = datetime.fromisoformat(data['launchDate'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            product_type=data.get('productType', {}).get('name') if data.get('productType') else None,
            status=data.get('productStatus', {}).get('name') if data.get('productStatus') else None,
            launch_date=launch_date
        )


@dataclass
class Entity:
    """Entity model"""
    id: Optional[int] = None
    name: Optional[str] = None
    entity_type: Optional[str] = None
    country: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Entity':
        """Create Entity from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            entity_type=data.get('entityType', {}).get('name') if data.get('entityType') else None,
            country=data.get('country', {}).get('Name') if data.get('country') else None
        )


@dataclass
class APIResponse:
    """Generic API response wrapper"""
    success: bool
    data: Optional[dict] = None
    errors: Optional[List[str]] = None
    message: Optional[str] = None
    
    @classmethod
    def success_response(cls, data: dict, message: str = None) -> 'APIResponse':
        """Create successful response"""
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def error_response(cls, errors: List[str], message: str = None) -> 'APIResponse':
        """Create error response"""
        return cls(success=False, errors=errors, message=message)