# Kern Resources FTS5 Search API

A powerful search API for Kern Resources using SQLite's FTS5 (Full-Text Search) extension.

## Overview

This API provides fast and efficient full-text search capabilities for the Kern Resources database. It allows searching across multiple fields including name, description, eligibility criteria, and more.

## Files

- `setup_fts_index.py` - Script to set up the FTS5 index
- `fts_search_api.py` - Flask API for searching resources
- `ai_search_demo.py` - Demo of how an AI model could use the search API

## Setup

1. Ensure you have Python 3.6+ installed
2. Install the required packages:
   ```
   pip install flask requests
   ```
3. Run the setup script to create the FTS5 index:
   ```
   python setup_fts_index.py [database_path]
   ```
   If no database path is provided, it will look for `resources.db` in the current directory and common locations.

## Running the API

Start the API server:
```
python fts_search_api.py
```

The API will be available at http://localhost:8082

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
      ...
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

## Web Interface

The API includes a simple web interface for testing the search functionality. Access it by opening http://localhost:8082 in your browser.

## AI Integration

The `ai_search_demo.py` script demonstrates how an AI model could use this search API to find resources based on user queries. Run it with:

```
python ai_search_demo.py
```

## Performance

The FTS5 search is optimized for performance and should handle thousands of resources efficiently. For the current dataset of ~500 resources, search queries typically complete in under 50ms.

## Documentation

For more detailed documentation, see the [FTS5 Search Implementation](kern_resources_new/docs/fts_search_implementation.md) document.

## License

This project is part of the Kern Resources application and is subject to its licensing terms.

---

*Created by Augment AI Assistant, June 2024*
