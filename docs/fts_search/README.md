# FTS5 Search for Kern Resources

This directory contains documentation for the FTS5 search implementation in the Kern Resources project.

## Overview

The Kern Resources project uses SQLite's FTS5 (Full-Text Search) extension to provide powerful and efficient search capabilities for resource data. This implementation allows for:

- Fast full-text search across multiple fields
- Relevance-based ranking of search results
- Case-insensitive searching
- Automatic indexing of new and updated resources

## Documentation

- [Implementation Details](implementation.md) - Comprehensive documentation of the FTS5 search implementation
- [AI Integration](ai_integration.md) - Guide for integrating the FTS5 search with AI models

## Key Files

- `setup_fts_index.py` - Script to set up the FTS5 index
- `fts_search_api.py` - Flask API for searching resources
- `ai_search_demo.py` - Demo of how an AI model could use the search API
- `tests/test_fts_search.py` - Unit tests for the FTS5 search implementation

## Getting Started

1. Set up the FTS5 index:
   ```
   python setup_fts_index.py [database_path]
   ```

2. Start the search API:
   ```
   python fts_search_api.py
   ```

3. Access the API at http://localhost:8082

## Testing

Run the unit tests:
```
python -m unittest tests.test_fts_search
```

## Integration with Llama 4

The FTS5 search API is designed to be easily integrated with the Llama 4 model. See the [AI Integration](ai_integration.md) guide for details.
