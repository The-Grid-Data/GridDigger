import json
import requests
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

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


# Function to generate GraphQL query for a given filter
def generate_query(filter_name, value):
    where_clause = filters_config["profile_filters"].get(filter_name)
    if where_clause:
        # Construct full GraphQL request
        query = f"query {{ profiles (where: {where_clause.replace('value', str(value))}) {{ name id }} }}"
        return query
    else:
        logging.warning(f"Filter '{filter_name}' not found.")
        return None


# Example values to be used for generating dynamic requests
example_values = {
    "profileType": 1,
    "profileSector": 10,
    "entities": 11
}

# Generate and send GraphQL requests for each filter
for filter_name, value in example_values.items():
    # Generate GraphQL query
    query = generate_query(filter_name, value)
    if query is None:
        continue

    # Send the GraphQL request
    response = requests.post(url, headers=headers, json={'query': query})

    # Log the request and response
    logging.info(f"Query: {query}")
    logging.info(f"Response: {response.json()}")
