# GridDigger Core Functionality & State Flow Documentation

## 🎯 Bot Overview

GridDigger is a Telegram bot that provides access to The Grid ID database through an interactive conversation flow. Users can search, filter, and explore blockchain project profiles through a series of menus and commands.

## 🚀 Entry Points

### Primary Commands
- `/start` - Initialize bot and show welcome message
- `/filter` - Enter the main filtering interface
- `/help` - Show help information
- `/open_source` - Show open source information

### Direct Text Input
- Any text message (not a command) triggers the main filter search

## 🔄 Core State Flow

### State Machine Overview
The bot uses a `ConversationHandler` with the following states:

```
FILTER_MAIN → FILTER_SUB → FILTER_CHOICES → FILTER_FILLING
     ↑                                            ↓
     └────────────── (fallbacks) ←────────────────┘
```

### State Definitions
```python
# handlers/__init__.py
FILTER_MAIN = 0      # Main filter menu
FILTER_SUB = 1       # Sub-filter selection
FILTER_CHOICES = 2   # Filter option choices
FILTER_FILLING = 3   # Text input for filters
```

## 📱 User Journey Flow

### 1. Initial Interaction

#### Entry via `/start` command
```
User: /start
Bot:  🚀 Welcome to GridDigger!
      
      GridDigger provides access to The Grid ID database...
      
      Use /filter to start searching or just type any search term.
```

#### Entry via `/filter` command or text
```
User: /filter  (or any text like "Solana")
Bot:  Applied filters:
      profileNameSearch: [user_input]
      
      Found results: X
      
      [Show profiles (X)] 
      [🔄Reset filters]
      [🟢Profile filters] [🟢Product filters]
      [🟢Asset filters] [🟢Entity filters]  
      [✔️Solana filter] [Inc search]
```

### 2. Main Filter Menu (FILTER_MAIN)

#### Current State Data Structure
```python
user_data = {
    'FILTERS': {
        'profileNameSearch_query': 'user_search_term',
        # Additional filters added as user navigates
    },
    'inc_search': False,  # Toggle for deep search
    'solana_filter_toggle': True,  # Solana-only filter
    'filter_type': 'profile'  # Current filter category
}
```

#### Available Actions
1. **Show profiles** - Display search results
2. **Reset filters** - Clear all applied filters
3. **Profile filters** - Enter profile-specific filtering
4. **Product filters** - Enter product-specific filtering
5. **Asset filters** - Enter asset-specific filtering
6. **Entity filters** - Enter entity-specific filtering
7. **Solana filter toggle** - Enable/disable Solana-only results
8. **Inc search toggle** - Switch between name-only and description search

### 3. Sub-Filter Selection (FILTER_SUB)

When user selects a filter category (e.g., "Profile filters"):

```
Bot: 🟢 Profile Filters

     Select a filter type:
     
     [Profile Type] [Profile Sector] [Profile Status]
     [Profile Name Search]
     
     [← Back] [Reset Profile Filters] [Show profiles (X)]
```

#### Filter Categories & Options

##### Profile Filters
- **Profile Type**: DeFi, NFT, Gaming, Infrastructure, etc.
- **Profile Sector**: Various blockchain sectors
- **Profile Status**: Active, Inactive, Development, etc.
- **Profile Name Search**: Text-based name search

##### Product Filters  
- **Product Type**: Protocol, Application, Tool, etc.
- **Product Status**: Live, Beta, Development, etc.

##### Asset Filters
- **Asset Type**: Token, NFT, etc.
- **Asset Standards**: SPL, ERC-20, etc.
- **Asset Tickers**: Token symbol search

##### Entity Filters
- **Entity Type**: Company, DAO, Foundation, etc.
- **Entity Name**: Organization name search

### 4. Filter Choices (FILTER_CHOICES)

When user selects a specific filter (e.g., "Profile Type"):

```
Bot: Select Profile Type:

     [DeFi Protocol] [NFT Project] [Gaming]
     [Infrastructure] [Developer Tools] [Exchange]
     [Wallet] [Analytics] [Other]
     
     [← Back] [Reset] [Show profiles (X)]
```

### 5. Text Input (FILTER_FILLING)

For text-based filters (e.g., "Profile Name Search"):

```
Bot: Enter profile name to search for:

User: Solana Labs

Bot: Applied filters:
     profileNameSearch: Solana Labs
     
     Found results: 5
     [Show profiles (5)] [🔄Reset filters] ...
```

### 6. Results Display

When user clicks "Show profiles":

```
Bot: Showing profiles with applied filters:
     profileNameSearch: Solana Labs
     profileType: DeFi Protocol

     [Profile Card 1 with Expand button]
     [Profile Card 2 with Expand button]
     [Profile Card 3 with Expand button]
     ...
```

## 📋 Profile Display System

### Profile Card Format
```
*Name:* Solana Labs
*Sector:* Infrastructure  
*Description:* Building the fastest blockchain...
*Products:* Solana Blockchain, Solana Pay (+2 more)
*Assets:* SOL, USDC (+1 more)
*Type:* Infrastructure

[Expand]
```

### Expanded Profile Format
```
*ID:* 254
*Name:* Solana Labs
*Sector:* Infrastructure
*Type:* Infrastructure Company
*Status:* Active
*Founding Date:* 2017-01-01
*Slug:* solana-labs
*Long Description:* Comprehensive description...
*Tag Line:* Building for scale
*Main Product Type:* Solana Blockchain, Solana Pay
*Issued Assets:* SOL, USDC

🌐 Website    📖 Documentation    💱 Exchange

[← Back]
```

## 🔄 Callback Handling System

### Callback Data Patterns
```python
# Main menu callbacks
'show'                    # Show profile results
'reset_all'              # Reset all filters
'profile_filters'        # Enter profile filter submenu
'product_filters'        # Enter product filter submenu
'asset_filters'          # Enter asset filter submenu
'entity_filters'         # Enter entity filter submenu
'solana_filter_toggle'   # Toggle Solana filter
'inc_search'             # Toggle incremental search

# Profile interaction callbacks
'expand_{profile_id}'         # Expand profile details
'back_to_card_{profile_id}'   # Return to card view

# Filter-specific callbacks
'reset_{filter_type}_filters'     # Reset specific filter category
'show_{filter_type}_filters'      # Show results for filter category
'{filter_name}_{option_id}'       # Select specific filter option
```

### Handler Mapping
```python
# handlers/setup.py
ConversationHandler(
    entry_points=[
        CommandHandler("filter", filter),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filter_main_text)
    ],
    states={
        FILTER_MAIN: [CallbackQueryHandler(handle_filter_main_callback)],
        FILTER_SUB: [CallbackQueryHandler(handle_filter_sub_callback)],
        FILTER_CHOICES: [CallbackQueryHandler(handle_filter_choices_callback)],
        FILTER_FILLING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filter_filling_text)]
    },
    fallbacks=[
        CommandHandler("filter", filter),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filter_main_text)
    ]
)

# Additional handlers outside conversation
CallbackQueryHandler(expand_profile_callback, pattern=r'^expand_')
CallbackQueryHandler(expand_profile_callback, pattern=r'^back_to_card_')
```

## 🗄️ Data Flow Architecture

### Search Process
```
1. User Input → handlers/commands.py or handlers/filters.py
2. Input Processing → handlers/utils.py (generate filters)
3. API Call → api.py (get_profiles function)
4. Data Retrieval → GraphQL query to The Grid database
5. Profile Formatting → services/enhanced_profile_service.py
6. Display → handlers/utils.py (send_profile_message)
```

### Profile Expansion Process
```
1. User clicks "Expand" → handlers/profiles.py (expand_profile_callback)
2. Profile ID extraction → callback_data parsing
3. Data Retrieval → enhanced_profile_service.get_expanded_profile()
4. Formatting → services/profile_formatter.py (ExpandedFormatter)
5. Display → Update message with expanded content and back button
```

### Back Navigation Process
```
1. User clicks "← Back" → handlers/profiles.py (expand_profile_callback)
2. Callback detection → 'back_to_card_' pattern matching
3. Card Retrieval → enhanced_profile_service.get_profile_card()
4. Formatting → services/profile_formatter.py (CardFormatter)
5. Display → Update message back to card format
```

## 🔍 Search & Filter Logic

### Search Types
1. **Quick Search** (`profileNameSearch`): Searches profile names only
2. **Deep Search** (`profileDeepSearch`): Searches names and descriptions
3. **Asset Search**: Searches by asset ticker symbols

### Filter Application Logic
```python
# api.py - get_profiles function
def get_profiles(data):
    # Extract filters from user_data
    filters = {}
    for key, value in data["FILTERS"].items():
        if key.endswith('_query'):
            filter_name = key.replace('_query', '')
            filters[filter_name] = value
    
    # Apply Solana filter if enabled (default: True)
    if data.get('solana_filter_toggle', True):
        filters['solana_profiles_only'] = 22
    
    # Convert to GraphQL query
    filtered_profiles = apply_filters(filters_list)
    return filtered_profiles['data']['roots']
```

### GraphQL Query Construction
```python
# api.py - apply_filters function
def apply_filters(filters):
    # Build WHERE clause from filters
    combined_clauses = {}
    for filter_name, value in filters:
        where_clause = filters_config["profile_filters"].get(filter_name)
        # ... clause building logic
    
    # Construct final query with 10,000 result limit
    query = f"query queryName {{ roots (limit: 10000, where: {where_clause}) {{ id slug }} }}"
    
    # Execute GraphQL request
    response = requests.post(url, headers=headers, json={'query': query})
    return response.json()
```

## 🎛️ Configuration & State Management

### User Data Structure
```python
# Complete user_data structure maintained throughout conversation
{
    'FILTERS': {
        'profileNameSearch_query': str,      # Search term
        'profileType_id': int,               # Selected profile type ID
        'profileSector_id': int,             # Selected sector ID
        'profileStatuses_id': int,           # Selected status ID
        'productTypes_id': int,              # Selected product type ID
        'assetTickers_query': str,           # Asset ticker search
        'entityTypes_id': int,               # Selected entity type ID
        'entityName_query': str              # Entity name search
    },
    'inc_search': bool,                      # Deep search toggle
    'solana_filter_toggle': bool,            # Solana filter toggle
    'filter_type': str                       # Current filter category context
}
```

### Filter Configuration
```python
# filters.json - External configuration file
{
    "profile_filters": {
        "profileNameSearch": "profileInfos: {name: {_contains: \"value\"}}",
        "profileType": "profileInfos: {profileTypeId: {_eq: value}}",
        "profileSector": "profileInfos: {profileSectorId: {_eq: value}}",
        "solana_profiles_only": "profileInfos: {profileSectorId: {_eq: value}}",
        "root": "roots"
    },
    "filters_queries": {
        "profileTypes": "profileTypes { id name }",
        "profileSectors": "profileSectors { id name }",
        "profileStatuses": "profileStatuses { id name }"
    },
    "sub_filters": {
        "profile": ["profileTypes", "profileSectors", "profileStatuses"],
        "product": ["productTypes", "productStatuses"],
        "asset": ["assetTypes", "assetStandards"],
        "entity": ["entityTypes"]
    }
}
```

## 🔧 Error Handling & Edge Cases

### Common Error Scenarios
1. **Empty Search Results**: Display "No profiles found" message
2. **API Failures**: Graceful degradation with fallback messages
3. **Invalid Profile IDs**: Handle missing profiles in expand functionality
4. **Network Issues**: Retry logic and timeout handling
5. **Malformed Callbacks**: Validation and error recovery

### Fallback Mechanisms
1. **Service Layer Fallbacks**: Enhanced service → Legacy API → Basic message
2. **Conversation Fallbacks**: Return to main menu on errors
3. **Display Fallbacks**: Text-only display if image loading fails
4. **Search Fallbacks**: V2 API → Legacy API → Empty results

## 📊 Performance Considerations

### Optimization Strategies
1. **Result Limiting**: 10,000 max results per query
2. **Display Limiting**: Show max 20 profiles to user
3. **Caching**: Service layer caching for repeated requests
4. **Connection Pooling**: Efficient database connections
5. **Async Processing**: Non-blocking webhook processing

### Monitoring Points
1. **Search Response Times**: Track API query performance
2. **User Interaction Patterns**: Monitor popular filters and searches
3. **Error Rates**: Track and alert on failure patterns
4. **Resource Usage**: Monitor memory and CPU usage

---

This document provides the complete picture of how GridDigger currently operates, from user interaction to data retrieval and display. It serves as the definitive reference for understanding the bot's core functionality and state management.