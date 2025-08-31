# api.py

import json
import requests
import logging
from config import Config

# Set up logging
logging.basicConfig(level=logging.WARNING)

# Define the GraphQL endpoint and headers using the new Config class
url = Config.get_graphql_endpoint()
headers = Config.get_graphql_headers()

# Load filter definitions from JSON file
with open('filters.json', 'r') as f:
    filters_config = json.load(f)


def apply_filters(filters):
    print(f"DEBUG: apply_filters called with filters = {filters}")
    combined_clauses = {}
    for filter_name, value in filters:
        where_clause = filters_config["profile_filters"].get(filter_name)
        print(f"DEBUG: filter_name = {filter_name}, value = {value}, where_clause = {where_clause}")
        if where_clause:
            clause = where_clause.replace('value', f'{value}')
            field = clause.split(":")[0].strip()
            if field in combined_clauses:
                combined_clauses[field].append(clause)
            else:
                combined_clauses[field] = [clause]
        else:
            logging.warning(f"Filter '{filter_name}' not found.")

    print(f"DEBUG: combined_clauses = {combined_clauses}")

    if combined_clauses:
        final_clauses = []
        for field, clauses in combined_clauses.items():
            if len(clauses) > 1:
                # Correctly combine clauses without repeating the field name
                combined_field_clause = f"{field}: {{ _and: [{', '.join([clause.split(':', 1)[1].strip() for clause in clauses])}] }}"
            else:
                combined_field_clause = clauses[0]
            final_clauses.append(combined_field_clause)

        combined_where_clause = ", ".join(final_clauses)
        where_clause = f"{{ {combined_where_clause} }}"
        root_field = filters_config["profile_filters"].get("root", "roots")
        query = f"query queryName {{ {root_field} (limit: 10000, where: {where_clause}) {{ id slug }} }}"
        print("DEBUG: GraphQL Query:", query)
        print(f"DEBUG: GraphQL URL: {url}")
        print(f"DEBUG: GraphQL Headers: {headers}")
        
        try:
            response = requests.post(url, headers=headers, json={'query': query})
            print(f"DEBUG: HTTP Status Code: {response.status_code}")
            response_data = response.json()
            print(f"DEBUG: GraphQL Response: {response_data}")
            logging.info(f"Query: {query}")
            logging.info(f"Response: {response_data}")
            return response_data
        except Exception as e:
            logging.error(f"Error making GraphQL request: {e}")
            print(f"DEBUG: Exception in GraphQL request: {e}")
            return None
    else:
        logging.warning("No valid filters found.")
        print("DEBUG: No valid filters found, returning None")
        return None


def fetch_all_filter_queries():
    results = {}
    for filter_name, query in filters_config["filters_queries"].items():
        full_query = f"query {{ {query} }}"
        response = requests.post(url, headers=headers, json={'query': full_query})
        response_data = response.json()
        logging.info(f"Query: {full_query}")
        logging.info(f"Response: {response_data}")
        results[filter_name] = response_data
    return results


def get_profiles(data):
    """
    Enhanced get_profiles function with better V2 integration and null safety
    """
    # Initialize a dictionary to hold filter names and values
    data.setdefault("FILTERS", {})
    data.setdefault("inc_search", False)
    inc_search: bool = data.get('inc_search', False)

    filters = {}

    for key, value in data["FILTERS"].items():
        if key.endswith('_query'):
            # cheap hack to toggle inc_search, but it works. Better approach requires refactoring.
            if key == 'profileNameSearch_query' or key == 'profileDeepSearch_query':
                if key == 'profileNameSearch_query' and inc_search:
                    key = 'profileDeepSearch_query'
                elif key == 'profileDeepSearch_query' and not inc_search:
                    key = 'profileNameSearch_query'
            filter_name = key.replace('_query', '')
            filters[filter_name] = value
    print("filters", filters)

    # Check if this is a simple search that can use V2 function
    if len(filters) == 1 and 'profileNameSearch' in filters:
        search_term = filters['profileNameSearch']
        print(f"DEBUG: Using V2 search for simple search: '{search_term}'")
        try:
            results = search_profiles_v2(search_term)
            print(f"DEBUG: V2 search returned {len(results)} results")
            return results if results is not None else []
        except Exception as e:
            logging.error(f"V2 search failed, falling back to legacy: {e}")
            # Fall through to legacy method

    if data.get('solana_filter_toggle', True) is True:
        filters['solana_profiles_only'] = 22

    if not filters:  # just to prevent errors
        filters = {
            "profileNameSearch": "",
        }

    filters_list = [(filter_name, value) for filter_name, value in filters.items()]
    print(f"DEBUG: filters_list = {filters_list}")

    filtered_profiles = apply_filters(filters_list)
    print(f"DEBUG: apply_filters returned = {filtered_profiles}")
    print(f"DEBUG: type of filtered_profiles = {type(filtered_profiles)}")
    
    if filtered_profiles is None:
        logging.error("apply_filters returned None. Filters list: %s", filters_list)
        return []
    
    if not filtered_profiles:
        logging.warning("Filtered profiles is empty dict/list. Returning an empty list.")
        return []
    
    # Check if response has GraphQL errors
    if 'errors' in filtered_profiles:
        logging.error(f"GraphQL errors in response: {filtered_profiles['errors']}")
        return []
    
    # Check if response has expected structure
    if 'data' not in filtered_profiles:
        logging.error(f"Response missing 'data' key. Response: {filtered_profiles}")
        return []
    
    # Handle case where data is None (GraphQL error case)
    response_data = filtered_profiles.get('data')
    if response_data is None:
        logging.error(f"Response data is None. Full response: {filtered_profiles}")
        return []
    
    if 'roots' not in response_data:
        logging.error(f"Response data missing 'roots' key. Data: {response_data}")
        return []
    
    roots_data = response_data.get('roots')
    # Handle case where roots is None (GraphQL returned null)
    if roots_data is None:
        logging.warning(f"GraphQL returned roots: null, treating as empty results")
        return []
    
    print(f"DEBUG: roots_data = {roots_data}")
    return roots_data


def search_profiles_v2(search_term=""):
    """
    Basic search using V2 schema structure with String! variables
    Uses the SearchForProfileNameOrAssetTicker query pattern
    """
    query = """
    query SearchForProfileNameOrAssetTicker($searchTerm: String1) {
      roots(
        limit: 10000,
        where: {_or: [{profileInfos: {name: {_contains: $searchTerm}}}, {assets: {ticker: {_contains: $searchTerm}}}]}
      ) {
        id
        slug
      }
    }
    """
    
    variables = {"searchTerm": search_term}
    
    try:
        response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
        response_data = response.json()
        
        if 'errors' in response_data:
            logging.error(f"GraphQL query error: {response_data['errors']}")
            return []
        
        return response_data.get('data', {}).get('roots', [])
    except Exception as e:
        logging.error(f"Error in search_profiles_v2: {e}")
        return []


def get_profile_data_by_id(profile_id):
    """
    Get profile data using V2 schema structure with String! variables
    Uses profileInfos with root relationships
    """
    query = """
    query getProfileData($profileId: String1) {
      profileInfos(limit: 1, where: {root: {id: {_eq: $profileId}}}) {
        tagLine
        descriptionShort
        profileSector {
          name
        }
        profileType {
          name
        }
        root {
          id
          slug
          assets {
            ticker
            name
            id
          }
          products {
            name
            id
          }
        }
        logo
        name
        urls(order_by: {urlTypeId: Asc}) {
          url
          urlType {
            name
          }
        }
      }
    }
    """
    
    variables = {"profileId": str(profile_id)}
    
    try:
        response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
        response_data = response.json()
        
        if 'errors' in response_data:
            logging.error(f"GraphQL query error: {response_data['errors']}")
            return {}
        
        profile_data = response_data.get('data', {}).get('profileInfos', [])
        return profile_data[0] if profile_data else {}
    except Exception as e:
        logging.error(f"Error in get_profile_data_by_id: {e}")
        return {}


def get_full_profile_data_by_id(profile_id):
    """
    Get complete profile data using V2 schema with String! variables
    Uses the full getProfileData query structure
    """
    query = """
    query getFullProfileData($profileId: String1) {
      profileInfos(limit: 1, offset: 0, where: {root: {id: {_eq: $profileId}}}) {
        tagLine
        descriptionShort
        descriptionLong
        profileSector {
          name
        }
        profileType {
          name
        }
        root {
          assets {
            ticker
            id
            rootId
            name
            icon
            description
            assetType {
              name
              id
            }
            assetStatus {
              name
              id
            }
            urls(order_by: {urlTypeId: Asc}) {
              url
              urlType {
                name
                id
              }
            }
          }
          socials {
            name
            socialType {
              name
            }
            urls(order_by: {urlTypeId: Asc}) {
              url
            }
          }
          products {
            id
            name
            launchDate
            isMainProduct
            description
            productType {
              name
              id
            }
            productStatus {
              name
              id
            }
            urls(order_by: {urlTypeId: Asc}) {
              url
              urlType {
                name
                id
              }
            }
          }
          entities {
            id
            name
            tradeName
            entityType {
              name
              id
            }
            country {
              name
              id
              code
            }
            urls {
              url
              urlType {
                name
                id
              }
            }
          }
        }
        profileStatus {
          name
          id
        }
        logo
        name
        urls(order_by: {urlTypeId: Asc}) {
          url
          urlType {
            name
          }
        }
      }
    }
    """
    
    variables = {"profileId": str(profile_id)}
    
    try:
        response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
        response_data = response.json()
        
        if 'errors' in response_data:
            logging.error(f"GraphQL query error: {response_data['errors']}")
            return {}
        
        profile_data = response_data.get('data', {}).get('profileInfos', [])
        return profile_data[0] if profile_data else {}
    except Exception as e:
        logging.error(f"Error in get_full_profile_data_by_id: {e}")
        return {}


def get_sub_filters(filter_type):
    return filters_config["sub_filters"].get(filter_type, [])


def fetch_filter_options(query):
    full_query = f"query {{ {query} }}"
    response = requests.post(url, headers=headers, json={'query': full_query})
    response_data = response.json()
    if 'errors' in response_data:
        logging.error(f"GraphQL query error: {response_data['errors']}")
        return []
    return response_data.get('data', {}).get(query.split()[0], [])

# # Example usage
# filters = [
#     ("profileNameSearch", "Noice"),
#     ("entityTypes", 4),
#     ("entityName", "O"),
# ]
# apply_filters(filters)

#print(len(get_profiles({})))
# # Example usage:
# data = {
#     "FILTERS": {
#         "profileType_id": 8,
#         "profileSector_id": 825
#     }
# }
# all = []
# for filter_name, value in data["FILTERS"].items():
#     all = apply_filters(filter_name, value)["data"]["profiles"]
