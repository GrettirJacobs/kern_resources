# FTS5 Search Implementation for Kern Resources

This document provides comprehensive documentation for the SQLite FTS5 search implementation in the Kern Resources project.

## Overview

The Kern Resources project uses SQLite's FTS5 (Full-Text Search) extension to provide powerful and efficient search capabilities for resource data. This implementation allows for:

- Fast full-text search across multiple fields
- Relevance-based ranking of search results
- Case-insensitive searching
- Automatic indexing of new and updated resources

## Implementation Details

### Database Schema

The FTS5 implementation adds a virtual table to the existing SQLite database:

```sql
CREATE VIRTUAL TABLE resource_fts USING fts5(
    name, 
    description, 
    eligibility_criteria,
    application_process,
    documents_required,
    cost,
    hours_of_operation,
    languages_supported,
    content='resources', 
    content_rowid='id'
)
```

This virtual table is linked to the main `resources` table using the `content` and `content_rowid` options, which specify that the FTS5 table is an external content table that gets its data from the `resources` table, using the `id` column as the row identifier.

### Synchronization Triggers

To keep the FTS5 index in sync with the main `resources` table, we've implemented three triggers:

1. **Insert Trigger** - Adds new resources to the FTS5 index:
```sql
CREATE TRIGGER resources_ai AFTER INSERT ON resources BEGIN
    INSERT INTO resource_fts(rowid, name, description, eligibility_criteria, 
                            application_process, documents_required, cost, 
                            hours_of_operation, languages_supported)
    VALUES (new.id, new.name, new.description, new.eligibility_criteria, 
           new.application_process, new.documents_required, new.cost, 
           new.hours_of_operation, new.languages_supported);
END;
```

2. **Update Trigger** - Updates the FTS5 index when resources are modified:
```sql
CREATE TRIGGER resources_au AFTER UPDATE ON resources BEGIN
    UPDATE resource_fts
    SET name = new.name,
        description = new.description,
        eligibility_criteria = new.eligibility_criteria,
        application_process = new.application_process,
        documents_required = new.documents_required,
        cost = new.cost,
        hours_of_operation = new.hours_of_operation,
        languages_supported = new.languages_supported
    WHERE rowid = old.id;
END;
```

3. **Delete Trigger** - Removes deleted resources from the FTS5 index:
```sql
CREATE TRIGGER resources_ad AFTER DELETE ON resources BEGIN
    DELETE FROM resource_fts WHERE rowid = old.id;
END;
```

### Search API

A dedicated search API has been implemented to provide access to the FTS5 search capabilities:

- **Endpoint**: `/api/search`
- **Method**: GET
- **Parameters**:
  - `q`: Search query (required)
  - `limit`: Maximum number of results to return (default: 10)
  - `offset`: Number of results to skip (default: 0)
- **Response**: JSON object containing search results and metadata

Example query:
```
GET /api/search?q=food&limit=5&offset=0
```

Example response:
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
      ...
    },
    ...
  ]
}
```

### Search Query Implementation

The core search query uses the FTS5 `MATCH` operator:

```sql
SELECT r.id, r.name, r.description, r.url, r.phone, r.email, r.address,
       r.eligibility_criteria, r.application_process, r.documents_required,
       r.cost, r.hours_of_operation, r.languages_supported, r.is_active,
       r.is_verified
FROM resources r
JOIN resource_fts fts ON r.id = fts.rowid
WHERE resource_fts MATCH ?
LIMIT ? OFFSET ?
```

This query joins the main `resources` table with the FTS5 virtual table and uses the `MATCH` operator to find resources that match the search query.

## Setup and Maintenance

### Initial Setup

The FTS5 index is set up using the `setup_fts_index.py` script, which:

1. Creates the FTS5 virtual table
2. Populates it with existing resource data
3. Sets up the synchronization triggers

The script can be run manually:
```
python setup_fts_index.py [database_path]
```

Alternatively, the search API will automatically set up the FTS5 index if it doesn't exist when a search is performed.

### Maintenance

The FTS5 index is automatically maintained through the synchronization triggers. No manual maintenance is required under normal operation.

If the FTS5 index becomes corrupted or needs to be rebuilt, the `setup_fts_index.py` script can be run again to recreate it.

## Performance Considerations

- FTS5 is optimized for search performance and should handle thousands of resources efficiently
- The index size will grow with the number of resources and the amount of text in each resource
- For very large datasets (tens of thousands of resources), consider implementing pagination and caching

## Integration with AI Models

The search API is designed to be easily integrated with AI models. The `ai_search_demo.py` script demonstrates how an AI model could use the search API to find resources based on user queries.

Key integration points:

1. **Extract search terms** from user queries using NLP techniques
2. **Call the search API** with the extracted terms
3. **Format the results** for inclusion in AI responses
4. **Provide context** about the resources to help the user

Example AI integration:
```python
def search_resources(query, limit=5):
    """Search for resources using the API."""
    response = requests.get(f"{API_BASE_URL}/search", params={
        "q": query,
        "limit": limit
    })
    
    if response.status_code == 200:
        return response.json()
    else:
        return None
```

## Future Enhancements

### Short-term Improvements

1. **Integrate FTS5 Search into Main Application**:
   - Update the main application's search functionality to use FTS5
   - Modify the resources_list route to use the same approach

2. **Enhance Search Capabilities**:
   - Add faceted search (filter by category, status, etc.)
   - Implement search highlighting to show where matches occur
   - Add synonym support for common terms

### Long-term Improvements

1. **Advanced Search Features**:
   - Implement geographic search (find resources near a location)
   - Add semantic search capabilities
   - Support for multi-language search

2. **AI-specific Enhancements**:
   - Create specialized endpoints for AI consumption
   - Add metadata to help AI models understand resource relationships
   - Implement rate limiting and authentication for API access

## Troubleshooting

### Common Issues

1. **FTS5 Not Available**: Ensure your SQLite version supports FTS5 (version 3.9.0 or later)
2. **Search Returns No Results**: Check that the FTS5 index is properly populated
3. **Performance Issues**: Consider optimizing the database and adding appropriate indexes

### Debugging

The search API includes detailed error messages and logging to help diagnose issues. Check the server logs for more information.

## References

- [SQLite FTS5 Documentation](https://www.sqlite.org/fts5.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Python Documentation](https://docs.python.org/3/library/sqlite3.html)

## Contributors

- Augment AI Assistant - Initial implementation and documentation
- [Your Name] - Project oversight and requirements

## License

This implementation is part of the Kern Resources project and is subject to its licensing terms.

---

*Last updated: June 2024*
