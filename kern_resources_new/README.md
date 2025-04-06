# Kern Resources

An AI-powered resource management system designed to help social services agencies find and recommend appropriate resources for clients.

## 🌟 Features

- **Resource Management**: Store, categorize, and retrieve community resources
- **Advanced Search**: Powerful full-text search using SQLite FTS5 for finding relevant resources
- **AI-Powered Recommendations**: Get intelligent resource suggestions based on client needs
- **Creative Lab**: AI-powered laboratory for managing project conversations and insights
- **Project Memory**: Intelligent storage and retrieval of project knowledge
- **CrewAI Integration**: Coordinated AI assistance across different aspects of the project

## 🏗️ Project Structure

```
kern_resources/
├── app/                  # Main Flask application
│   ├── models/           # Database models
│   ├── routes/           # Web routes and API endpoints
│   ├── services/         # Business logic
│   ├── static/           # Static assets
│   ├── templates/        # HTML templates
│   └── utils/            # Utility functions
├── frontend/             # Static website frontend
│   ├── css/              # CSS stylesheets
│   ├── public/           # Static assets (images, fonts, etc.)
│   ├── src/              # JavaScript source files
│   └── index.html        # Main HTML file
├── creative_lab/         # Creative Lab module
│   ├── conversations/    # Stored conversation data
│   ├── insights/         # Generated AI insights
│   └── session/          # Session management
├── project_memory/       # Project Memory module
│   ├── api/              # API for memory access
│   ├── core/             # Core memory functionality
│   └── storage/          # Storage implementations
├── crew_ai/              # CrewAI integration
│   ├── agents/           # AI agent definitions
│   ├── tasks/            # Task definitions
│   └── examples/         # Example implementations
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── docs/                 # Documentation
│   ├── api/              # API documentation
│   ├── guides/           # User guides
│   ├── deployment/       # Deployment documentation
│   └── examples/         # Example usage
├── run.py                # Application entry point
├── requirements.txt      # Project dependencies
└── setup.py              # Package configuration
```

## 🚀 Getting Started

1. **Prerequisites**
   - Python 3.10+
   - Dependencies listed in requirements.txt

2. **Installation**
   ```bash
   git clone https://github.com/yourusername/kern_resources.git
   cd kern_resources
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # Initialize the database with migrations and seed data
   python cli.py init-db

   # Or run individual steps
   python cli.py upgrade-db  # Run migrations
   python cli.py create-migration -m "your message"  # Create a new migration
   ```

4. **Running the Application**
   ```bash
   python cli.py run
   # Or use Flask directly
   flask run

5. **Running Tests**
   ```bash
   pytest
   ```

## 🔍 Search Functionality

Kern Resources includes a powerful search system based on SQLite FTS5 (Full-Text Search):

- **High-Performance Search**: Find resources quickly, even in large databases
- **Advanced Query Syntax**: Support for phrase searches, boolean operators, and wildcards
- **Partial Matching**: Find resources with terms that start with your search query
- **Graceful Fallback**: Automatically falls back to regular search if FTS5 is not available

For more information, see:
- [User Search Guide](docs/user_guides/search_features.md)
- [Technical Documentation](docs/technical/fts5_search_implementation.md)
- [Developer Quick Reference](docs/technical/fts5_quick_reference.md)

## 📚 Documentation

We follow a systematic documentation approach to ensure our development process is well-documented and our code is maintainable. Our documentation is organized into the following categories:

- **Design Documents**: Architecture decisions and component interactions
  - [Project Architecture](docs/design/2025-04-04_design_project_architecture.md)

- **Implementation Notes**: How specific features were implemented
  - [Resource Management Implementation](docs/implementation/2025-04-04_implementation_resource_management.md)
  - [FTS5 Search Integration](docs/implementation/2025-04-07_implementation_fts5_integration.md)

- **API Documentation**: Endpoint specifications and usage
  - [Resources API v1](docs/api/api_resources_v1.md)
  - [Search API](docs/technical/fts5_search_implementation.md#api-endpoints)

- **Development Logs**: Progress summaries and decisions
  - [Initial Project Restructuring](docs/logs/2025-04-04_devlog_initial_restructuring.md)

- **Project Overview**: High-level documentation
  - [Project Restructuring Documentation](RESTRUCTURING_DOCUMENTATION.md)

- **Deployment Documentation**: Deployment plans and infrastructure
  - [Deployment Plan](docs/deployment/2025-04-07_deployment_plan.md)

For more information about our documentation approach, see the [Documentation README](docs/README.md).

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
