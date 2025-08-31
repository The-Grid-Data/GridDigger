# GridDigger Feature Designs & Implementation Plans

## 🎯 Feature 1: Enhanced Product & Asset Loading from Expanded Menu

### Current State Analysis
- Expanded profiles show basic product/asset lists as text
- No interactive elements for detailed product/asset information
- Limited to displaying names only
- No way to explore individual products or assets

### Proposed Enhancement

#### 1.1 Interactive Product Buttons
```
Current: *Products:* Product A, Product B, Product C (+2 more)
New:     *Products:* [Product A] [Product B] [Product C] [View All]
```

**Implementation Plan:**
- Add product buttons to `ExpandedFormatter` in `services/profile_formatter.py`
- Create new callback handlers for product details
- Implement product detail formatting with comprehensive information

#### 1.2 Interactive Asset Buttons
```
Current: *Assets:* Token A, Token B, Token C (+5 more)
New:     *Assets:* [Token A] [Token B] [Token C] [View All]
```

**Implementation Plan:**
- Add asset buttons to expanded profile view
- Create asset detail handlers with market data integration
- Implement asset-specific information display

#### 1.3 Detailed Product View
When user clicks a product button:
```
📦 Product Details: [Product Name]

*Type:* DeFi Protocol
*Status:* Active
*Launch Date:* 2023-05-15
*Description:* Comprehensive product description...

*URLs:*
🌐 Website    📖 Documentation    📱 App

*Related Assets:* [Token A] [Token B]

[← Back to Profile] [View Other Products]
```

#### 1.4 Detailed Asset View
When user clicks an asset button:
```
🪙 Asset Details: [Token Name] (SYMBOL)

*Type:* Utility Token
*Standard:* SPL Token
*Status:* Active
*Description:* Token description and utility...

*Market Info:*
💰 Current Price: $X.XX (if available)
📊 Market Cap: $X.XX (if available)
📈 24h Change: +X.XX% (if available)

*URLs:*
🌐 Website    📊 Explorer    💱 Trade

[← Back to Profile] [View Other Assets]
```

### Technical Implementation

#### 1.5 New Formatter Classes
```python
# services/product_formatter.py
class ProductFormatter(ProfileFormatter):
    def format_product_detail(self, product_data: ProductData) -> FormattedProfile
    def format_product_list(self, products: List[ProductData]) -> FormattedProfile

# services/asset_formatter.py  
class AssetFormatter(ProfileFormatter):
    def format_asset_detail(self, asset_data: AssetData) -> FormattedProfile
    def format_asset_list(self, assets: List[AssetData]) -> FormattedProfile
```

#### 1.6 New Handler Functions
```python
# handlers/products.py (NEW FILE)
async def handle_product_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE)
async def handle_product_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE)

# handlers/assets.py (NEW FILE)
async def handle_asset_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE)
async def handle_asset_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE)
```

#### 1.7 Enhanced Data Models
```python
# models/product_data.py (NEW FILE)
@dataclass
class ProductData:
    id: str
    name: str
    product_type: Optional[ProductType]
    status: Optional[ProductStatus]
    launch_date: Optional[str]
    description: Optional[str]
    urls: List[UrlData]
    related_assets: List[str]

# models/asset_data.py (NEW FILE)
@dataclass
class AssetData:
    id: str
    name: str
    ticker: str
    asset_type: Optional[AssetType]
    standard: Optional[str]
    description: Optional[str]
    market_data: Optional[MarketData]
    urls: List[UrlData]
```

---

## 🎯 Feature 2: Solana Filter Removal

### Current State Analysis
- Solana filter is enabled by default (`solana_filter_toggle: True`)
- Takes up valuable UI space in filter menu
- May not be relevant for current use case
- Hardcoded to filter ID 22

### Removal Plan

#### 2.1 Code Changes Required
```python
# handlers/utils.py - Remove from keyboard
# Line 39: Remove solana toggle button
# Line 30: Remove solana_toggle_text variable
# Lines 308-315: Remove toggle_solana_filter function

# handlers/profiles.py - Remove handler
# Lines 44-48: Remove solana callback handling

# api.py - Remove from get_profiles
# Lines 121-122: Remove automatic solana filter addition
```

#### 2.2 Migration Strategy
1. **Phase 1**: Make Solana filter optional (default off)
2. **Phase 2**: Remove from UI but keep backend logic
3. **Phase 3**: Complete removal of Solana filter code

---

## 🎯 Feature 3: Enhanced Inc Search Functionality

### Current State Analysis
- Inc search toggles between `profileNameSearch` and `profileDeepSearch`
- Implementation is described as "cheap hack" in comments
- Limited user understanding of what "Inc search" means
- No clear indication of search scope

### Improvement Plan

#### 3.1 Better Naming & UX
```
Current: "Inc search" (unclear)
New:     "🔍 Deep Search" or "📖 Search Descriptions"
```

#### 3.2 Enhanced Implementation
```python
# handlers/utils.py - Improved toggle
def toggle_deep_search(data):
    """Toggle between name-only and description search"""
    data.setdefault('deep_search_enabled', False)
    data['deep_search_enabled'] = not data['deep_search_enabled']
    
    # Update search query type based on toggle
    if 'profileNameSearch_query' in data.get('FILTERS', {}):
        search_term = data['FILTERS']['profileNameSearch_query']
        if data['deep_search_enabled']:
            data['FILTERS']['profileDeepSearch_query'] = search_term
            del data['FILTERS']['profileNameSearch_query']
        else:
            data['FILTERS']['profileNameSearch_query'] = search_term
            if 'profileDeepSearch_query' in data['FILTERS']:
                del data['FILTERS']['profileDeepSearch_query']
```

#### 3.3 User Feedback
```
When toggled ON:  "🔍 Deep search enabled - searching names and descriptions"
When toggled OFF: "📝 Quick search enabled - searching names only"
```

---

## 🎯 Feature 4: Watchlist/Favorites System

### Architecture Design

#### 4.1 Database Schema
```sql
-- New table for user watchlists
CREATE TABLE user_watchlists (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    profile_id VARCHAR(255) NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE KEY unique_user_profile (user_id, profile_id),
    INDEX idx_user_id (user_id),
    INDEX idx_profile_id (profile_id)
);

-- User preferences table
CREATE TABLE user_preferences (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    notification_preferences JSON,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 4.2 New Service Layer
```python
# services/watchlist_service.py (NEW FILE)
class WatchlistService:
    def add_to_watchlist(self, user_id: int, profile_id: str, notes: str = None) -> bool
    def remove_from_watchlist(self, user_id: int, profile_id: str) -> bool
    def get_user_watchlist(self, user_id: int) -> List[WatchlistItem]
    def is_in_watchlist(self, user_id: int, profile_id: str) -> bool
    def get_watchlist_count(self, user_id: int) -> int
```

#### 4.3 Enhanced Profile Display
```python
# Add star button to profile cards
# services/profile_formatter.py - Enhanced buttons
def _create_profile_buttons(self, profile_id: str, user_id: int) -> List[List[InlineKeyboardButton]]:
    buttons = []
    
    # Expand button
    buttons.append([InlineKeyboardButton("Expand", callback_data=f"expand_{profile_id}")])
    
    # Watchlist button (star/unstar based on current status)
    if watchlist_service.is_in_watchlist(user_id, profile_id):
        buttons.append([InlineKeyboardButton("⭐ Remove from Watchlist", callback_data=f"unstar_{profile_id}")])
    else:
        buttons.append([InlineKeyboardButton("☆ Add to Watchlist", callback_data=f"star_{profile_id}")])
    
    return buttons
```

#### 4.4 Watchlist Management Commands
```python
# handlers/watchlist.py (NEW FILE)
async def show_watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE)
async def handle_star_callback(update: Update, context: ContextTypes.DEFAULT_TYPE)
async def handle_unstar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE)
async def clear_watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE)
```

#### 4.5 New Bot Commands
```
/watchlist - Show your saved profiles
/clearwatchlist - Clear all watchlist items
/watchlistcount - Show number of saved profiles
```

---

## 🎯 Feature 5: User Profile Management System

### User Settings Architecture

#### 5.1 User Preferences Management
```python
# services/user_service.py (NEW FILE)
class UserService:
    def get_user_profile(self, user_id: int) -> UserProfile
    def update_user_preferences(self, user_id: int, preferences: dict) -> bool
    def set_notification_preferences(self, user_id: int, notifications: dict) -> bool
    def get_user_statistics(self, user_id: int) -> UserStats
```

#### 5.2 User Settings Menu
```
⚙️ User Settings

👤 Profile Information
   Name: John Doe (@johndoe)
   Member since: Jan 2024
   
📊 Usage Statistics
   Searches performed: 1,234
   Profiles viewed: 567
   Watchlist items: 23
   
🔔 Notification Preferences
   ✅ Watchlist updates
   ❌ New profile alerts
   ✅ System announcements
   
📱 Display Preferences
   🖼️ Show profile images: ON
   📝 Compact mode: OFF
   🔍 Default search: Quick search
   
[Edit Profile] [Notification Settings] [Export Data]
```

#### 5.3 New Commands
```
/settings - Open user settings menu
/profile - Show your profile information
/stats - Show your usage statistics
/notifications - Manage notification preferences
/export - Export your data (watchlist, preferences)
```

---

## 🎯 Feature 6: Additional Functionality Suggestions

### 6.1 Advanced Search Features
- **Search History**: Remember recent searches
- **Saved Searches**: Save complex filter combinations
- **Search Suggestions**: Auto-complete and suggestions
- **Bulk Operations**: Select multiple profiles for batch actions

### 6.2 Social Features
- **Profile Sharing**: Share profiles with other users
- **Comments & Reviews**: User-generated content on profiles
- **Rating System**: Community ratings for profiles
- **Discussion Threads**: Profile-specific discussions

### 6.3 Analytics & Insights
- **Trending Profiles**: Most viewed/searched profiles
- **Market Insights**: Data-driven analysis
- **Comparative Analysis**: Side-by-side profile comparisons
- **Custom Reports**: Personalized data exports

### 6.4 Integration Features
- **Calendar Integration**: Track important dates
- **Price Alerts**: Notifications for asset price changes
- **Portfolio Tracking**: Track your investments
- **External API Integration**: Connect with other services

### 6.5 Advanced UI Features
- **Dark Mode**: Theme preferences
- **Custom Layouts**: Personalized display options
- **Keyboard Shortcuts**: Power user features
- **Voice Commands**: Voice-activated search

---

## 🚀 Implementation Priority

### Phase 1 (Immediate - Next 2 weeks)
1. ✅ Enhanced Product & Asset Loading
2. ✅ Solana Filter Removal
3. ✅ Inc Search Improvements

### Phase 2 (Short-term - Next month)
4. ✅ Watchlist/Favorites System
5. ✅ Basic User Profile Management

### Phase 3 (Medium-term - Next quarter)
6. ✅ Advanced Search Features
7. ✅ Analytics & Insights
8. ✅ Social Features

### Phase 4 (Long-term - Future)
9. ✅ Integration Features
10. ✅ Advanced UI Features

---

## 📋 Technical Requirements

### Database Changes
- New tables: `user_watchlists`, `user_preferences`, `search_history`
- Indexes for performance optimization
- Migration scripts for existing users

### API Enhancements
- New endpoints for user management
- Enhanced product/asset data retrieval
- Caching strategies for user data

### Security Considerations
- User data privacy and GDPR compliance
- Rate limiting for new features
- Input validation and sanitization
- Secure data export functionality

### Performance Optimization
- Efficient database queries for user data
- Caching strategies for frequently accessed data
- Pagination for large datasets
- Background processing for heavy operations

---

*This document serves as the comprehensive feature design and implementation roadmap for GridDigger's next evolution.*