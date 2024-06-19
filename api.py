# api.py

import json
import requests
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)

# Load environment variables from .env file
load_dotenv(".env")

# Define the GraphQL endpoint and headers
url = os.getenv("GRAPHQL_ENDPOINT")
headers = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {os.getenv('HASURA_API_TOKEN')}"
}

# Load filter definitions from JSON file
with open('filters.json', 'r') as f:
    filters_config = json.load(f)




def apply_filters(filters):
    combined_clauses = {}
    for filter_name, value in filters:
        where_clause = filters_config["profile_filters"].get(filter_name)
        if where_clause:
            clause = where_clause.replace('value', f'{value}')
            field = clause.split(":")[0].strip()
            if field in combined_clauses:
                combined_clauses[field].append(clause)
            else:
                combined_clauses[field] = [clause]
        else:
            logging.warning(f"Filter '{filter_name}' not found.")

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
        query = f"query queryName {{ profiles (where: {where_clause}) {{ name id }} }}"
        print("GraphQL Query:", query)  # Debug statement
        response = requests.post(url, headers=headers, json={'query': query})
        response_data = response.json()
        logging.info(f"Query: {query}")
        logging.info(f"Response: {response_data}")
        return response_data
    else:
        logging.warning("No valid filters found.")
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
    # Initialize a dictionary to hold filter names and values
    data.setdefault("FILTERS", {})

    filters = {}

    for key, value in data["FILTERS"].items():
        if key.endswith('_id'):
            filter_name = key.replace('_id', '')
            filters[filter_name] = value
    print("filters", filters)

    if not filters:
        filters = {
            "profileNameSearch": "",
            #"profileType": 1,
        }

    filters_list = [(filter_name, value) for filter_name, value in filters.items()]

    filtered_profiles = apply_filters(filters_list)
    print("filters_list", filtered_profiles)
    return filtered_profiles['data']['profiles'] #here

def get_profile_data_by_id(profile_id):
    query = f"""
    query {{
        profiles(where: {{ id: {{ _eq: {profile_id} }} }}) {{
            name
            id
            profileSector {{ name }}
            products {{ name }}
            assets {{ name }}
            tagLine
            descriptionShort
            logo
            urlMain
            urlDocumentation
            socials {{ url }}
        }}
    }}
    """
    response = requests.post(url, headers=headers, json={'query': query})
    response_data = response.json()
    if 'errors' in response_data:
        logging.error(f"GraphQL query error: {response_data['errors']}")
        return {}
    profile_data = response_data.get('data', {}).get('profiles', [])
    return profile_data[0] if profile_data else {}


def get_full_profile_data_by_id(profile_id):
    query = f"""
    query {{
        profiles(where: {{ id: {{ _eq: {profile_id} }} }}) {{
            name
            id
            profileSector {{ name }}
            products {{ name }}
            assets {{ name }}
            tagLine
            descriptionShort
            descriptionLong
            logo
            urlMain
            urlDocumentation
            socials {{ url }}
        }}
    }}
    """
    response = requests.post(url, headers=headers, json={'query': query})
    response_data = response.json()
    if 'errors' in response_data:
        logging.error(f"GraphQL query error: {response_data['errors']}")
        return {}
    profile_data = response_data.get('data', {}).get('profiles', [])
    return profile_data[0] if profile_data else {}


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
