# FTS5 Search API for AI Integration

**Date:** June 12, 2024  
**Focus:** Documentation of the FTS5 search API for AI integration

## Overview

The Kern Resources FTS5 Search API provides a powerful way for AI models to search for resources in the Kern Resources database. This document outlines how AI models can use the API to find relevant resources based on user queries.

## API Endpoints

### Search Resources

```
GET /api/search?q={query}&limit={limit}&offset={offset}
```

Parameters:
- `q`: Search query (required)
- `limit`: Maximum number of results to return (default: 10)
- `offset`: Number of results to skip (default: 0)

Example:
```
GET /api/search?q=food&limit=5
```

Response:
```json
{
  "success": true,
  "query": "food",
  "total": 86,
  "limit": 5,
  "offset": 0,
  "resources": [
    {
      "id": 5,
      "name": "Catholic Charities – Bakersfield Community Services",
      "description": "Offers emergency food pantry services, rental and utility assistance, clothing vouchers, and case management.",
      "url": "https://ccdof.org/our-services/food-pantry/",
      "phone": "661-281-2130",
      "email": "avorhees@ccdof.org",
      "address": "Office: 825 Chester Ave | Food Pantry: 809 Chester Ave, Bakersfield, CA",
      "eligibility_criteria": "Low-income individuals and families in crisis | documentation required",
      "application_process": "",
      "documents_required": "",
      "cost": "",
      "hours_of_operation": "Mon–Fri 8:30am–3:30pm (closed 12–1pm)",
      "languages_supported": "",
      "is_active": true,
      "is_verified": false
    },
    ...
  ]
}
```

### Get Resource by ID

```
GET /api/resource/{resource_id}
```

Parameters:
- `resource_id`: ID of the resource to retrieve

Example:
```
GET /api/resource/5
```

Response:
```json
{
  "success": true,
  "resource": {
    "id": 5,
    "name": "Catholic Charities – Bakersfield Community Services",
    "description": "Offers emergency food pantry services, rental and utility assistance, clothing vouchers, and case management.",
    ...
    "categories": [
      {
        "id": 1,
        "name": "Food",
        "description": "Food assistance resources"
      },
      ...
    ]
  }
}
```

## AI Integration Examples

### Example 1: Basic Search

```python
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
```

### Example 2: Extract Search Terms from User Query

```python
def extract_search_terms(user_query):
    """Extract potential search terms from a user query."""
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
    
    return search_terms
```

### Example 3: Format Resources for AI Response

```python
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
```

### Example 4: Complete AI Integration

```python
def generate_ai_response(user_query):
    """Generate an AI response that incorporates resource search results."""
    # Extract search terms from the user query
    search_terms = extract_search_terms(user_query)
    
    # Search for resources using the extracted terms
    all_resources = []
    for term in search_terms:
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
```

## Best Practices for AI Integration

1. **Extract Relevant Search Terms**
   - Use NLP techniques to extract relevant search terms from user queries
   - Consider multiple potential search terms for complex queries
   - Use a fallback to the full query if no specific terms are identified

2. **Handle Multiple Resources**
   - Deduplicate resources if searching for multiple terms
   - Limit the number of resources included in responses
   - Provide a summary of the total number of resources found

3. **Format Resources Appropriately**
   - Include the most relevant information for each resource
   - Format the information in a clear and readable way
   - Highlight the most important details based on the user's query

4. **Provide Context and Guidance**
   - Explain why the resources are relevant to the user's query
   - Provide guidance on how to use or contact the resources
   - Suggest follow-up questions or additional search terms

5. **Handle No Results Gracefully**
   - Provide helpful suggestions when no resources are found
   - Suggest alternative search terms
   - Offer general information about available services

## Future Enhancements

1. **Synonym Expansion**
   - Automatically expand search queries to include synonyms
   - Example: "food" would also search for "meal", "nutrition", etc.

2. **Resource Relationships**
   - Include related resources in API responses
   - Example: If a food bank is returned, also include nearby transportation services

3. **Geographic Search**
   - Allow searching for resources near a specific location
   - Example: "food banks near Bakersfield"

4. **Specialized AI Endpoints**
   - Create endpoints specifically designed for AI consumption
   - Include additional metadata and context

5. **Authentication and Rate Limiting**
   - Implement API key authentication for AI access
   - Add rate limiting to prevent abuse

## Conclusion

The FTS5 Search API provides a powerful way for AI models to find relevant resources in the Kern Resources database. By following the best practices outlined in this document, AI models can provide helpful and accurate information to users about available resources in Kern County.
