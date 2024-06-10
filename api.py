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


# Function to apply filters and send GraphQL query
def apply_filters(filter_name, value):
    where_clause = filters_config["profile_filters"].get(filter_name)
    if where_clause:
        # Construct full GraphQL request
        query = f"query {{ profiles (where: {where_clause.replace('value', str(value))}) {{ name id }} }}"

        # Send the GraphQL request
        response = requests.post(url, headers=headers, json={'query': query})
        response_data = response.json()

        # Log the request and response
        logging.info(f"Query: {query}")
        logging.info(f"Response: {response_data}")

        return response_data
    else:
        logging.warning(f"Filter '{filter_name}' not found.")
        return None


# Function to fetch data for all filters_queries
def fetch_all_filter_queries():
    results = {}
    for filter_name, query in filters_config["filters_queries"].items():
        # Construct GraphQL query
        full_query = f"query {{ {query} }}"

        # Send the GraphQL request
        response = requests.post(url, headers=headers, json={'query': full_query})
        response_data = response.json()

        # Log the request and response
        logging.info(f"Query: {full_query}")
        logging.info(f"Response: {response_data}")

        # Store the results
        results[filter_name] = response_data

    return results


# # Example values to be used for generating dynamic requests
# example_values = {
#     "profileType": 1,
#     "profileSector": 10,
#     "entities": 11
# }
#
# # Apply filters and fetch data
# for filter_name, value in example_values.items():
#     apply_filters(filter_name, value)
#
# # Fetch data for all filters_queries
# all_filter_queries_data = fetch_all_filter_queries()

# Print the fetched data
#print(json.dumps(all_filter_queries_data, indent=2))
def get_profiles(data):
    example_values = {
        "profileNameSearch": data["profileNameSearch"] if data.get("profileNameSearch") else "",
    }

    # Apply filters and fetch data
    for filter_name, value in example_values.items():
        return apply_filters(filter_name, value)["data"]["profiles"]



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