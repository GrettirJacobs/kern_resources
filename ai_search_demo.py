"""
Demo of how an AI model could use the resource search API.

This script simulates an AI model using the search API to find resources
based on user queries and incorporate them into its responses.
"""

import requests
import json
import re

# Configuration
API_BASE_URL = "http://localhost:8082/api"

def search_resources(query, limit=5):
    """Search for resources using the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/search", params={
            "q": query,
            "limit": limit
        })
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: API returned status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error searching resources: {str(e)}")
        return None

def get_resource(resource_id):
    """Get a resource by ID."""
    try:
        response = requests.get(f"{API_BASE_URL}/resource/{resource_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: API returned status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting resource: {str(e)}")
        return None

def format_resource_for_ai(resource):
    """Format a resource for inclusion in an AI response."""
    if not resource:
        return ""
    
    formatted = f"Name: {resource['name']}\n"
    
    if resource.get('description'):
        formatted += f"Description: {resource['description']}\n"
    
    if resource.get('phone'):
        formatted += f"Phone: {resource['phone']}\n"
    
    if resource.get('email'):
        formatted += f"Email: {resource['email']}\n"
    
    if resource.get('url'):
        formatted += f"Website: {resource['url']}\n"
    
    if resource.get('address'):
        formatted += f"Address: {resource['address']}\n"
    
    if resource.get('eligibility_criteria'):
        formatted += f"Eligibility: {resource['eligibility_criteria']}\n"
    
    if resource.get('application_process'):
        formatted += f"Application Process: {resource['application_process']}\n"
    
    if resource.get('documents_required'):
        formatted += f"Documents Required: {resource['documents_required']}\n"
    
    if resource.get('cost'):
        formatted += f"Cost: {resource['cost']}\n"
    
    if resource.get('hours_of_operation'):
        formatted += f"Hours: {resource['hours_of_operation']}\n"
    
    if resource.get('languages_supported'):
        formatted += f"Languages: {resource['languages_supported']}\n"
    
    return formatted

def simulate_ai_response(user_query):
    """Simulate an AI response that incorporates resource search results."""
    # Extract potential search terms from the user query
    # This is a simple example - a real AI would use more sophisticated NLP
    search_terms = []
    
    # Look for food-related terms
    if re.search(r'\b(food|meal|hungry|eat|nutrition)\b', user_query, re.IGNORECASE):
        search_terms.append("food")
    
    # Look for housing-related terms
    if re.search(r'\b(housing|shelter|homeless|rent|apartment)\b', user_query, re.IGNORECASE):
        search_terms.append("housing")
    
    # Look for medical-related terms
    if re.search(r'\b(medical|doctor|health|clinic|hospital)\b', user_query, re.IGNORECASE):
        search_terms.append("medical")
    
    # Look for financial-related terms
    if re.search(r'\b(money|financial|cash|assistance|aid)\b', user_query, re.IGNORECASE):
        search_terms.append("financial assistance")
    
    # If no specific terms were found, use the whole query
    if not search_terms:
        search_terms = [user_query]
    
    # Search for resources using the extracted terms
    all_resources = []
    for term in search_terms:
        print(f"Searching for resources related to: {term}")
        result = search_resources(term)
        
        if result and result.get('success') and result.get('resources'):
            all_resources.extend(result.get('resources'))
    
    # Deduplicate resources
    seen_ids = set()
    unique_resources = []
    for resource in all_resources:
        if resource['id'] not in seen_ids:
            seen_ids.add(resource['id'])
            unique_resources.append(resource)
    
    # Generate the AI response
    response = f"I found some resources that might help with your query about '{user_query}':\n\n"
    
    if unique_resources:
        for i, resource in enumerate(unique_resources[:3], 1):
            response += f"Resource {i}:\n"
            response += format_resource_for_ai(resource)
            response += "\n"
        
        if len(unique_resources) > 3:
            response += f"I found {len(unique_resources)} resources in total. These are just the top 3 most relevant ones.\n"
    else:
        response += "I couldn't find any specific resources matching your query. Please try a different search term or contact Kern County services directly for assistance."
    
    return response

def main():
    """Main function to demonstrate the AI search capability."""
    print("AI Resource Search Demo")
    print("======================")
    print("This demo simulates how an AI model could use the resource search API")
    print("to find resources based on user queries and incorporate them into its responses.")
    print()
    print("Type 'exit' to quit.")
    print()
    
    while True:
        user_query = input("User: ")
        
        if user_query.lower() in ['exit', 'quit', 'bye']:
            break
        
        ai_response = simulate_ai_response(user_query)
        print("\nAI Assistant:")
        print(ai_response)
        print()

if __name__ == "__main__":
    main()
