"""
Profile Formatter - Strategy pattern for different display formats
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from telegram import InlineKeyboardButton
from models.profile_data import ProfileData, FormattedProfile

logger = logging.getLogger(__name__)


class ProfileFormatter(ABC):
    """Base formatter interface"""
    
    @abstractmethod
    def format(self, profile: ProfileData) -> FormattedProfile:
        """Format profile data for display"""
        pass
    
    @abstractmethod
    def get_supported_fields(self) -> List[str]:
        """Get list of fields this formatter supports"""
        pass


class CardFormatter(ProfileFormatter):
    """Enhanced card format for search results with products and assets"""
    
    def format(self, profile: ProfileData) -> FormattedProfile:
        """Format profile for enhanced card display"""
        try:
            # Escape special characters to prevent Telegram parsing errors
            safe_name = self._escape_markdown_text(profile.name)
            safe_sector = self._escape_markdown_text(profile.sector.name if profile.sector else '-')
            
            message_parts = [
                f"*Name:* {safe_name}",
                f"*Sector:* {safe_sector}",
            ]
            
            # Add short description if available
            if profile.description_short:
                safe_description = self._escape_markdown_text(profile.description_short)
                message_parts.append(f"*Description:* {safe_description}")
            else:
                message_parts.append("*Description:* -")
            
            # Add products count (enhanced feature - buttons will be added below)
            if profile.products:
                valid_products = [p for p in profile.products if p.name and p.name != 'Unknown']
                if valid_products:
                    message_parts.append(f"*Products:* {len(valid_products)} available")
            
            # Add assets count (enhanced feature - buttons will be added below)
            if profile.assets:
                valid_assets = [a for a in profile.assets if a.name and a.name != 'Unknown']
                if valid_assets:
                    message_parts.append(f"*Assets:* {len(valid_assets)} available")
            
            # Add profile type if available
            if profile.profile_type:
                message_parts.append(f"*Type:* {profile.profile_type.name}")
            
            # Create interactive buttons for products and assets
            buttons = []
            
            # Add individual product buttons - SHOW ALL PRODUCTS by default
            if profile.products:
                valid_products = [p for p in profile.products if p.name and p.name != 'Unknown']
                if valid_products:
                    # Show ALL products individually (no limit)
                    for product in valid_products:
                        # Escape product name to prevent button text issues
                        safe_product_name = self._escape_markdown_text(product.name)
                        buttons.append([InlineKeyboardButton(
                            f"🔧 {safe_product_name}",
                            callback_data=f"product_detail_{product.id}"
                        )])
            
            # Add individual asset buttons - SHOW ALL ASSETS by default
            if profile.assets:
                valid_assets = [a for a in profile.assets if a.name and a.name != 'Unknown']
                if valid_assets:
                    # Show ALL assets individually (no limit)
                    for asset in valid_assets:
                        # Escape asset name and ticker to prevent button text issues
                        safe_asset_name = self._escape_markdown_text(asset.name)
                        safe_ticker = self._escape_markdown_text(asset.ticker) if asset.ticker else ""
                        button_text = f"💎 {safe_asset_name} ({safe_ticker})" if safe_ticker else f"💎 {safe_asset_name}"
                        buttons.append([InlineKeyboardButton(
                            button_text,
                            callback_data=f"asset_detail_{asset.id}"
                        )])
            
            # Add profile URLs as buttons (this is where the real URLs should be)
            if profile.urls:
                url_buttons = []
                for url_obj in profile.urls[:3]:  # Limit to 3 URLs for clean UI
                    if url_obj and url_obj.url:
                        url_type = url_obj.url_type.lower() if url_obj.url_type else 'link'
                        
                        # Create appropriate button text based on URL type
                        if 'website' in url_type or 'main' in url_type:
                            button_text = "🌐 Website"
                        elif 'documentation' in url_type or 'docs' in url_type:
                            button_text = "📚 Docs"
                        elif 'whitepaper' in url_type:
                            button_text = "📄 Whitepaper"
                        elif 'blog' in url_type:
                            button_text = "📝 Blog"
                        elif 'social' in url_type or 'twitter' in url_type:
                            button_text = "🐦 Social"
                        elif 'telegram' in url_type:
                            button_text = "💬 Telegram"
                        else:
                            button_text = f"🔗 {url_type.title()}"
                        
                        url_buttons.append(InlineKeyboardButton(button_text, url=url_obj.url))
                
                # Add URL buttons in rows of 2
                for i in range(0, len(url_buttons), 2):
                    buttons.append(url_buttons[i:i+2])
            
            # Add discovery button and expand button at the end
            if profile.slug:
                discovery_url = f"https://discovery.thegrid.id/profiles/{profile.slug}"
                buttons.append([InlineKeyboardButton(f"🔍 Open {profile.name} on Discovery", url=discovery_url)])
            
            buttons.append([InlineKeyboardButton("📋 Expand Profile", callback_data=f"expand_{profile.id}")])
            
            return FormattedProfile(
                message_text="\n".join(message_parts),
                buttons=buttons,
                has_media=bool(profile.logo),
                media_url=profile.logo
            )
            
        except Exception as e:
            logger.error(f"Error formatting enhanced card for profile {profile.id}: {e}")
            return FormattedProfile(
                message_text=f"*Name:* {profile.name}\n*Error:* Unable to format profile",
                buttons=[[InlineKeyboardButton("Expand", callback_data=f"expand_{profile.id}")]]
            )
    
    def _escape_markdown_text(self, text: str) -> str:
        """Escape special markdown characters to prevent Telegram parsing errors"""
        if not text:
            return text
        
        # Escape problematic characters that cause entity parsing errors
        # More comprehensive escaping to prevent "can't find end of entity" errors
        problematic_chars = ['_', '*', '[', ']', '`', '\\', '(', ')']
        
        for char in problematic_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def get_supported_fields(self) -> List[str]:
        return ['name', 'sector', 'description_short', 'products', 'assets', 'profile_type', 'logo']


class ExpandedFormatter(ProfileFormatter):
    """Full detailed format for expand functionality"""
    
    def format(self, profile: ProfileData) -> FormattedProfile:
        """Format profile for expanded display"""
        try:
            message_parts = [
                f"*ID:* {profile.id}",
                f"*Name:* {profile.name}",
                f"*Sector:* {profile.sector.name if profile.sector else '-'}",
                f"*Type:* {profile.profile_type.name if profile.profile_type else '-'}",
                f"*Status:* {profile.status.name if profile.status else '-'}",
            ]
            
            # Add founding date if available
            if profile.founding_date:
                message_parts.append(f"*Founding Date:* {profile.founding_date}")
            
            # Add slug
            message_parts.append(f"*Slug:* {profile.slug or '-'}")
            
            # Add descriptions
            message_parts.append(f"*Long Description:* {profile.description_long or '-'}")
            message_parts.append(f"*Tag Line:* {profile.tag_line or '-'}")
            
            # Add products (null-safe)
            if profile.products:
                product_names = [p.name for p in profile.products if p.name and p.name != 'Unknown']
                if product_names:
                    message_parts.append(f"*Main Product Type:* {', '.join(product_names)}")
                else:
                    message_parts.append("*Main Product Type:* -")
            else:
                message_parts.append("*Main Product Type:* -")
            
            # Add assets (null-safe)
            if profile.assets:
                asset_names = [a.name for a in profile.assets if a.name and a.name != 'Unknown']
                if asset_names:
                    message_parts.append(f"*Issued Assets:* {', '.join(asset_names)}")
                else:
                    message_parts.append("*Issued Assets:* -")
            else:
                message_parts.append("*Issued Assets:* -")
            
            # Generate URL buttons
            buttons = self._create_url_buttons(profile.urls)
            
            # Add discovery button
            if profile.slug:
                discovery_url = f"https://discovery.thegrid.id/profiles/{profile.slug}"
                buttons.append([InlineKeyboardButton(f"🔍 Open {profile.name} on Discovery", url=discovery_url)])
            
            # Add back button at the end
            buttons.append([InlineKeyboardButton("← Back", callback_data=f"back_to_card_{profile.id}")])
            
            return FormattedProfile(
                message_text="\n".join(message_parts),
                buttons=buttons,
                has_media=bool(profile.logo),
                media_url=profile.logo
            )
            
        except Exception as e:
            logger.error(f"Error formatting expanded profile {profile.id}: {e}")
            return FormattedProfile(
                message_text=f"*Name:* {profile.name}\n*Error:* Unable to format expanded profile",
                buttons=[]
            )
    
    def _create_url_buttons(self, urls: List) -> List[List[InlineKeyboardButton]]:
        """Create URL buttons from profile URLs"""
        buttons = []
        
        try:
            for url_obj in urls:
                if not url_obj or not url_obj.url:
                    continue
                
                url = url_obj.url
                url_type = url_obj.url_type.lower() if url_obj.url_type else ''
                
                # Map URL types to button labels
                if 'website' in url_type or 'main' in url_type:
                    buttons.append([InlineKeyboardButton("Website", url=url)])
                elif 'documentation' in url_type or 'docs' in url_type:
                    buttons.append([InlineKeyboardButton("Documentation", url=url)])
                elif 'whitepaper' in url_type:
                    buttons.append([InlineKeyboardButton("Whitepaper", url=url)])
                elif 'blog' in url_type:
                    buttons.append([InlineKeyboardButton("Blog", url=url)])
                elif 'social' in url_type or 'twitter' in url_type or 'telegram' in url_type:
                    buttons.append([InlineKeyboardButton("Social", url=url)])
                else:
                    # Generic button for other URL types
                    button_text = url_type.title() if url_type != 'unknown' else 'Link'
                    buttons.append([InlineKeyboardButton(button_text, url=url)])
            
        except Exception as e:
            logger.error(f"Error creating URL buttons: {e}")
        
        return buttons
    
    def get_supported_fields(self) -> List[str]:
        return [
            'id', 'name', 'sector', 'profile_type', 'status', 'founding_date',
            'slug', 'description_long', 'tag_line', 'products', 'assets', 'urls'
        ]


class CompactFormatter(ProfileFormatter):
    """Ultra-compact format for quick display"""
    
    def format(self, profile: ProfileData) -> FormattedProfile:
        """Format profile for compact display"""
        try:
            message_text = f"*{profile.name}* ({profile.sector.name if profile.sector else 'Unknown'})"
            
            buttons = [[InlineKeyboardButton("Expand", callback_data=f"expand_{profile.id}")]]
            
            return FormattedProfile(
                message_text=message_text,
                buttons=buttons,
                has_media=False
            )
            
        except Exception as e:
            logger.error(f"Error formatting compact profile {profile.id}: {e}")
            return FormattedProfile(
                message_text=f"*{profile.name}*",
                buttons=[]
            )
    
    def get_supported_fields(self) -> List[str]:
        return ['name', 'sector']


class FormatterFactory:
    """Factory for creating formatters with plugin support"""
    
    def __init__(self):
        self._formatters = {
            'card': CardFormatter,
            'expanded': ExpandedFormatter,
            'compact': CompactFormatter
        }
    
    def register_formatter(self, format_name: str, formatter_class: type):
        """Register custom formatter"""
        if not issubclass(formatter_class, ProfileFormatter):
            raise ValueError("Formatter must inherit from ProfileFormatter")
        
        self._formatters[format_name] = formatter_class
        logger.info(f"Registered custom formatter: {format_name}")
    
    def get_formatter(self, format_type: str) -> ProfileFormatter:
        """Get formatter instance"""
        if format_type not in self._formatters:
            logger.warning(f"Unknown format type: {format_type}, using card formatter")
            format_type = 'card'
        
        return self._formatters[format_type]()
    
    def get_available_formats(self) -> List[str]:
        """Get list of available formats"""
        return list(self._formatters.keys())


# Global formatter factory instance
formatter_factory = FormatterFactory()