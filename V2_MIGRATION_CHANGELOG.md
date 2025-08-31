# GraphQL V2 Schema Migration Changelog

## Overview
Migration from legacy GraphQL schema to V2 schema structure. The V2 schema uses `roots` and `profileInfos` as primary entities instead of the legacy `profiles` field.

## Key Schema Changes

### Primary Entity Changes
- **Legacy**: `profiles` (root field)
- **V2**: `roots` (for search) and `profileInfos` (for detailed data)

### Search Query Structure
- **Legacy**: Direct profile search
- **V2**: Search through `roots` with nested `profileInfos` and `assets`

## Files Requiring Updates

### 1. `api.py` - Core API Functions

#### Current Issues:
- Uses legacy `profiles` field in all queries
- Hardcoded field names not compatible with V2 schema
- Response parsing expects legacy structure

#### Required Changes:

##### `apply_filters()` function (Lines 20-56):
- **Current**: Uses `profiles` as root field
- **Update**: Use `roots` for search queries
- **New Query Structure**:
  ```graphql
  query SearchForProfileNameOrAssetTicker {
    roots(where: {_or: {profileInfos: {name: {_contains: ""}}, assets: {ticker: {_contains: ""}}}}) {
      id
      slug
    }
  }
  ```

##### `get_profiles()` function (Lines 71-112):
- **Current**: Returns `filtered_profiles.get('data', {}).get('profiles', [])`
- **Update**: Return `filtered_profiles.get('data', {}).get('roots', [])`

##### `get_profile_data_by_id()` function (Lines 115-139):
- **Current**: Uses `profiles(where: {id: {_eq: {profile_id}}})`
- **Update**: Use V2 `getProfileData` query structure with `profileInfos`
- **New Query Structure**: Use the provided `getProfileData` query with variables

##### `get_full_profile_data_by_id()` function (Lines 142-173):
- **Current**: Uses legacy `profiles` field
- **Update**: Use full V2 `getProfileData` query structure

### 2. `filters.json` - Filter Configuration

#### Current Issues:
- `"root": "profiles"` (Line 20) - Invalid in V2 schema
- Filter clauses reference legacy field structure
- Query definitions use legacy field names

#### Required Changes:

##### Root Field Update:
```json
// Current
"root": "profiles"

// Update to
"root": "roots"
```

##### Profile Filters Update (Lines 21-33):
```json
// Current examples
"profileNameSearch": "name: { _ilike: \"%value%\" }"
"solana_profiles_only": "products: {deployedOnProductId: {_eq: value }}"

// Update to V2 structure
"profileNameSearch": "_or: {profileInfos: {name: {_contains: \"value\"}}, assets: {ticker: {_contains: \"value\"}}}"
"solana_profiles_only": "profileInfos: {root: {products: {productDeployments: {smartContractDeployment: {deployedOnProduct: {id: {_eq: value}}}}}}}"
```

##### Filters Queries Update (Lines 3-18):
```json
// Current examples
"profileType": "profileTypes { name id }"
"profileSector": "profileSectors { name id }"

// These may need to be updated based on V2 schema availability
// Need to verify if these fields exist in V2 or require different paths
```

### 3. Response Data Structure Changes

#### Current Response Parsing:
```python
# Legacy structure
response.get('data', {}).get('profiles', [])
```

#### V2 Response Parsing:
```python
# For search queries
response.get('data', {}).get('roots', [])

# For detailed profile data
response.get('data', {}).get('profileInfos', [])
```

## Implementation Priority

### Phase 1: Basic Search (IMMEDIATE)
1. Update `apply_filters()` to use `roots` query
2. Update `filters.json` root field
3. Update basic search filters for name/ticker search
4. Update response parsing in `get_profiles()`

### Phase 2: Profile Data Retrieval
1. Update `get_profile_data_by_id()` with V2 query structure
2. Update `get_full_profile_data_by_id()` with complete V2 query
3. Update response parsing for detailed profile data

### Phase 3: Advanced Filters
1. Map remaining filter types to V2 schema
2. Update complex filter combinations
3. Test all filter combinations

## Data Mapping Notes

### V2 Schema Structure:
- `roots` contains basic identification (id, slug)
- `profileInfos` contains detailed profile information
- Nested relationships: `root.assets`, `root.products`, `root.entities`
- URL structure: `urls(order_by: {urlTypeId: Asc})`

### Key Relationship Changes:
- **Assets**: Now accessed via `root.assets` instead of direct `assets`
- **Products**: Now accessed via `root.products` instead of direct `products`  
- **Entities**: Now accessed via `root.entities` instead of direct `entities`
- **URLs**: Now have structured `urlType` relationships

## Testing Strategy

### Basic Functionality Test:
1. Profile name search
2. Asset ticker search
3. Profile data retrieval by ID
4. Filter combinations

### Validation Points:
- Query syntax validation against V2 schema
- Response data structure validation
- Error handling for missing fields
- Performance comparison with legacy queries

## Rollback Plan

### If Issues Arise:
1. Revert `filters.json` root field to "profiles"
2. Revert query structures in `api.py`
3. Switch back to legacy endpoint in `config.py`
4. Document specific V2 schema issues encountered

## Notes for Future Development

### Schema Documentation Needed:
- Complete V2 field mapping documentation
- Available filter fields in V2 schema
- Performance characteristics of V2 queries
- Rate limiting and authentication requirements

### Potential Optimizations:
- Query result caching for frequently accessed data
- Batch query optimization for multiple profile requests
- Error handling improvements for schema validation failures