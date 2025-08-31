# V2 Schema Implementation Plan

## Immediate Implementation Tasks

### 1. Update `filters.json` - Basic Search Configuration

**File**: `filters.json`

**Changes Required**:

```json
// Line 20: Change root field
"root": "roots",

// Lines 21-22: Update basic search filters
"profileNameSearch": "_or: {profileInfos: {name: {_contains: \"value\"}}, assets: {ticker: {_contains: \"value\"}}}",
"profileDeepSearch": "_or: {profileInfos: {name: {_contains: \"value\"}}, assets: {ticker: {_contains: \"value\"}}}",

// Line 23: Update Solana filter (simplified for now)
"solana_profiles_only": "profileInfos: {root: {products: {id: {_eq: value}}}}",
```

### 2. Update `api.py` - Core Search Functions

**File**: `api.py`

#### A. Update `apply_filters()` function (Lines 46-47):

**Current**:
```python
root_field = filters_config["profile_filters"].get("root", "profiles")
query = f"query queryName {{ {root_field} (where: {where_clause}) {{ name id }} }}"
```

**Update to**:
```python
root_field = filters_config["profile_filters"].get("root", "roots")
query = f"query queryName {{ {root_field} (where: {where_clause}) {{ id slug }} }}"
```

#### B. Update `get_profiles()` function (Line 112):

**Current**:
```python
return filtered_profiles.get('data', {}).get('profiles', [])
```

**Update to**:
```python
return filtered_profiles.get('data', {}).get('roots', [])
```

#### C. Create new search function for V2:

**Add new function**:
```python
def search_profiles_v2(search_term=""):
    """
    Basic search using V2 schema structure
    Uses the SearchForProfileNameOrAssetTicker query pattern
    """
    query = f"""
    query SearchForProfileNameOrAssetTicker {{
      roots(
        where: {{_or: {{profileInfos: {{name: {{_contains: "{search_term}"}}}}, assets: {{ticker: {{_contains: "{search_term}"}}}}}}}}
      ) {{
        id
        slug
      }}
    }}
    """
    
    response = requests.post(url, headers=headers, json={'query': query})
    response_data = response.json()
    
    if 'errors' in response_data:
        logging.error(f"GraphQL query error: {response_data['errors']}")
        return []
    
    return response_data.get('data', {}).get('roots', [])
```

### 3. Update Profile Data Retrieval Functions

#### A. Update `get_profile_data_by_id()` function:

**Replace entire function with**:
```python
def get_profile_data_by_id(profile_id):
    """
    Get profile data using V2 schema structure
    Uses profileInfos with root relationships
    """
    query = f"""
    query getProfileData {{
      profileInfos(limit: 1, where: {{root: {{id: {{_eq: {profile_id}}}}}}}) {{
        tagLine
        descriptionShort
        profileSector {{
          name
        }}
        profileType {{
          name
        }}
        root {{
          id
          slug
          assets {{
            ticker
            name
            id
          }}
          products {{
            name
            id
          }}
        }}
        logo
        name
        urls(order_by: {{urlTypeId: Asc}}) {{
          url
          urlType {{
            name
          }}
        }}
      }}
    }}
    """
    
    response = requests.post(url, headers=headers, json={'query': query})
    response_data = response.json()
    
    if 'errors' in response_data:
        logging.error(f"GraphQL query error: {response_data['errors']}")
        return {}
    
    profile_data = response_data.get('data', {}).get('profileInfos', [])
    return profile_data[0] if profile_data else {}
```

#### B. Update `get_full_profile_data_by_id()` function:

**Replace with the complete V2 query structure provided by the user**:
```python
def get_full_profile_data_by_id(profile_id):
    """
    Get complete profile data using V2 schema
    Uses the full getProfileData query structure
    """
    query = f"""
    query getProfileData {{
      profileInfos(limit: 1, offset: 0, where: {{root: {{id: {{_eq: {profile_id}}}}}}}) {{
        tagLine
        descriptionShort
        descriptionLong
        profileSector {{
          name
        }}
        profileType {{
          name
        }}
        root {{
          assets {{
            ticker
            id
            rootId
            name
            icon
            description
            assetTypeId
            assetStatusId
            assetType {{
              definition
              id
              name
            }}
            assetStatus {{
              name
              id
              definition
            }}
            assetDeployments {{
              id
              deploymentId
              assetId
              smartContractDeployment {{
                id
                deployedOnProduct {{
                  id
                  name
                  root {{
                    slug
                  }}
                }}
                assetStandard {{
                  id
                }}
                smartContracts {{
                  name
                  id
                  deploymentId
                  deploymentDate
                  address
                }}
                deploymentType {{
                  name
                  id
                  definition
                }}
              }}
            }}
            urls(order_by: {{urlTypeId: Asc}}) {{
              url
              urlType {{
                name
                id
                definition
              }}
            }}
          }}
          profileTags {{
            tag {{
              name
              id
            }}
          }}
          socials {{
            name
            socialType {{
              name
            }}
            urls(order_by: {{urlTypeId: Asc}}) {{
              url
            }}
          }}
          products {{
            id
            rootId
            productTypeId
            productStatusId
            name
            launchDate
            isMainProduct
            description
            productType {{
              name
              id
              definition
            }}
            productStatus {{
              name
              id
              definition
            }}
            productDeployments {{
              smartContractDeployment {{
                deployedOnProduct {{
                  id
                  name
                  root {{
                    slug
                  }}
                }}
                assetStandard {{
                  id
                }}
                deploymentType {{
                  name
                }}
                smartContracts {{
                  name
                  id
                  deploymentDate
                  address
                  deploymentId
                }}
                isOfStandardId
                id
              }}
            }}
            supportsProducts {{
              supportsProduct {{
                name
                id
                root {{
                  slug
                }}
              }}
            }}
            supportedBy: supportsProductsBySupportsProductId {{
              product {{
                name
                id
                root {{
                  slug
                }}
              }}
            }}
            urls(order_by: {{urlTypeId: Asc}}) {{
              url
              urlType {{
                name
                id
                definition
              }}
            }}
            productAssetRelationships {{
              assetId
              asset {{
                name
                id
                assetType {{
                  name
                }}
                root {{
                  slug
                }}
              }}
              assetSupportType {{
                name
              }}
              product {{
                name
                id
                description
              }}
            }}
          }}
          entities {{
            id
            name
            tradeName
            taxIdentificationNumber
            localRegistrationNumber
            leiNumber
            dateOfIncorporation
            address
            entityType {{
              name
              id
              definition
            }}
            country {{
              name
              id
              code
            }}
            urls {{
              url
              urlType {{
                name
                id
                definition
              }}
            }}
          }}
        }}
        profileStatus {{
          name
          id
        }}
        mainProduct: root {{
          products(where: {{isMainProduct: {{_eq: "1"}}}}, limit: 1) {{
            productType {{
              name
            }}
          }}
        }}
        logo
        name
        urls(order_by: {{urlTypeId: Asc}}) {{
          url
          urlType {{
            name
          }}
        }}
      }}
    }}
    """
    
    response = requests.post(url, headers=headers, json={'query': query})
    response_data = response.json()
    
    if 'errors' in response_data:
        logging.error(f"GraphQL query error: {response_data['errors']}")
        return {}
    
    profile_data = response_data.get('data', {}).get('profileInfos', [])
    return profile_data[0] if profile_data else {}
```

## Testing Strategy

### Basic Test Cases:
1. **Empty search**: `search_profiles_v2("")` should return basic results
2. **Name search**: `search_profiles_v2("Bitcoin")` should find profiles with Bitcoin in name
3. **Ticker search**: `search_profiles_v2("BTC")` should find assets with BTC ticker
4. **Profile data**: `get_profile_data_by_id(1)` should return profile info
5. **Full profile data**: `get_full_profile_data_by_id(1)` should return complete data

### Error Handling:
- Invalid profile IDs should return empty dict `{}`
- GraphQL errors should be logged and return appropriate empty responses
- Network errors should be handled gracefully

## Implementation Order:

1. **First**: Update `filters.json` with basic V2 structure
2. **Second**: Update `apply_filters()` and `get_profiles()` functions
3. **Third**: Add new `search_profiles_v2()` function
4. **Fourth**: Update profile data retrieval functions
5. **Fifth**: Test basic search functionality
6. **Sixth**: Test profile data retrieval

## Notes for Implementation:

- Keep the original functions as backup (comment them out) until V2 is confirmed working
- Add extensive logging during the transition period
- Test with known profile IDs first
- Verify the V2 endpoint is accessible and returns expected data structure
- Consider adding a feature flag to switch between V1 and V2 queries during testing

## Success Criteria:

- `/filter` command works without errors
- Profile search returns results in expected format
- Profile data retrieval works for valid IDs
- No `'NoneType' object has no attribute 'get'` errors
- GraphQL validation errors are resolved