"""
FTS5 Search API for resources.

This script provides a simple API for searching resources using the FTS5 index.
It can be used by an AI model to search for resources.
"""

import sqlite3
import os
import json
import sys
from flask import Flask, request, jsonify

app = Flask(__name__)

def setup_fts_index(db_path):
    """Set up FTS5 index for resources."""
    print(f"Setting up FTS5 index for database at {db_path}")

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if the resources table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resources'")
        if not cursor.fetchone():
            print("Error: Resources table does not exist")
            return False

        # Count resources
        cursor.execute("SELECT COUNT(*) FROM resources")
        resource_count = cursor.fetchone()[0]
        print(f"Found {resource_count} resources in the database")

        # Check if FTS5 is available
        try:
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            print(f"SQLite version: {version}")

            # Create a test FTS5 table to check if FTS5 is available
            cursor.execute("CREATE VIRTUAL TABLE temp.test_fts USING fts5(content)")
            cursor.execute("DROP TABLE temp.test_fts")
            print("FTS5 is available")
        except sqlite3.OperationalError as e:
            print(f"Error: FTS5 is not available - {str(e)}")
            print("Please make sure your SQLite version supports FTS5")
            return False

        # Check if the FTS5 table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resource_fts'")
        if cursor.fetchone():
            print("FTS5 table already exists, dropping it to recreate")
            cursor.execute("DROP TABLE resource_fts")

        # Create the FTS5 virtual table
        print("Creating FTS5 virtual table...")
        cursor.execute("""
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
        """)

        # Populate the FTS5 table with existing data
        print("Populating FTS5 table with existing data...")
        cursor.execute("""
        INSERT INTO resource_fts(rowid, name, description, eligibility_criteria,
                                application_process, documents_required, cost,
                                hours_of_operation, languages_supported)
        SELECT id, name, description, eligibility_criteria,
               application_process, documents_required, cost,
               hours_of_operation, languages_supported
        FROM resources
        """)

        # Check for existing triggers and drop them if they exist
        print("Checking for existing triggers...")
        for trigger_name in ['resources_ai', 'resources_au', 'resources_ad']:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name=?", (trigger_name,))
            if cursor.fetchone():
                print(f"Dropping existing trigger {trigger_name}...")
                cursor.execute(f"DROP TRIGGER {trigger_name}")

        # Create triggers to keep the FTS5 table in sync with the resources table
        print("Creating triggers to keep the FTS5 table in sync...")

        # Insert trigger
        cursor.execute("""
        CREATE TRIGGER resources_ai AFTER INSERT ON resources BEGIN
            INSERT INTO resource_fts(rowid, name, description, eligibility_criteria,
                                    application_process, documents_required, cost,
                                    hours_of_operation, languages_supported)
            VALUES (new.id, new.name, new.description, new.eligibility_criteria,
                   new.application_process, new.documents_required, new.cost,
                   new.hours_of_operation, new.languages_supported);
        END;
        """)

        # Update trigger
        cursor.execute("""
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
        """)

        # Delete trigger
        cursor.execute("""
        CREATE TRIGGER resources_ad AFTER DELETE ON resources BEGIN
            DELETE FROM resource_fts WHERE rowid = old.id;
        END;
        """)

        # Commit changes
        conn.commit()

        # Test the FTS5 index
        print("\nTesting FTS5 index...")
        cursor.execute("""
        SELECT r.id, r.name, r.description
        FROM resources r
        JOIN resource_fts fts ON r.id = fts.rowid
        WHERE resource_fts MATCH ?
        LIMIT 5
        """, ("food",))

        results = cursor.fetchall()
        print(f"Found {len(results)} resources matching 'food'")

        if results:
            print("\nSample results:")
            for i, result in enumerate(results):
                print(f"{i+1}. ID: {result[0]}, Name: {result[1]}")
                if result[2]:
                    print(f"   Description: {result[2][:100]}...")
                else:
                    print("   Description: None")
                print()

        print("FTS5 index setup completed successfully")
        return True

    except Exception as e:
        print(f"Error setting up FTS5 index: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_db_connection(db_path=None):
    """Get a database connection."""
    # Try different possible locations for the database
    if db_path is None:
        possible_paths = [
            'resources.db',
            'kern_resources_new/resources.db',
            os.path.join('kern_resources_new', 'resources.db')
        ]

        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                print(f"Using database at: {path}")
                break

    if not db_path or not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/search', methods=['GET'])
def search():
    """Search resources using FTS5."""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)

    if not query:
        return jsonify({
            'success': False,
            'error': 'No query provided',
            'resources': []
        })

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the FTS5 table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resource_fts'")
        if not cursor.fetchone():
            print("FTS5 index not found. Creating it now...")
            conn.close()  # Close the current connection

            # Get the database path
            db_path = conn.path if hasattr(conn, 'path') else 'kern_resources_new/resources.db'

            # Set up the FTS5 index
            if not setup_fts_index(db_path):
                return jsonify({
                    'success': False,
                    'error': 'Failed to create FTS5 index. Please check the logs.',
                    'resources': []
                })

            # Reconnect to the database
            conn = get_db_connection(db_path)
            cursor = conn.cursor()

        # Search using FTS5
        cursor.execute("""
        SELECT r.id, r.name, r.description, r.url, r.phone, r.email, r.address,
               r.eligibility_criteria, r.application_process, r.documents_required,
               r.cost, r.hours_of_operation, r.languages_supported, r.is_active,
               r.is_verified
        FROM resources r
        JOIN resource_fts fts ON r.id = fts.rowid
        WHERE resource_fts MATCH ?
        LIMIT ? OFFSET ?
        """, (query, limit, offset))

        # Convert results to a list of dictionaries
        resources = []
        for row in cursor.fetchall():
            resource = {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'url': row['url'],
                'phone': row['phone'],
                'email': row['email'],
                'address': row['address'],
                'eligibility_criteria': row['eligibility_criteria'],
                'application_process': row['application_process'],
                'documents_required': row['documents_required'],
                'cost': row['cost'],
                'hours_of_operation': row['hours_of_operation'],
                'languages_supported': row['languages_supported'],
                'is_active': bool(row['is_active']),
                'is_verified': bool(row['is_verified'])
            }
            resources.append(resource)

        # Get total count
        cursor.execute("""
        SELECT COUNT(*) as count
        FROM resources r
        JOIN resource_fts fts ON r.id = fts.rowid
        WHERE resource_fts MATCH ?
        """, (query,))

        total = cursor.fetchone()['count']

        # Close the connection
        conn.close()

        return jsonify({
            'success': True,
            'query': query,
            'total': total,
            'limit': limit,
            'offset': offset,
            'resources': resources
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'resources': []
        })

@app.route('/api/resource/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    """Get a resource by ID."""
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the resource
        cursor.execute("""
        SELECT r.id, r.name, r.description, r.url, r.phone, r.email, r.address,
               r.eligibility_criteria, r.application_process, r.documents_required,
               r.cost, r.hours_of_operation, r.languages_supported, r.is_active,
               r.is_verified
        FROM resources r
        WHERE r.id = ?
        """, (resource_id,))

        row = cursor.fetchone()

        if not row:
            return jsonify({
                'success': False,
                'error': f'Resource with ID {resource_id} not found',
                'resource': None
            })

        # Convert row to a dictionary
        resource = {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'url': row['url'],
            'phone': row['phone'],
            'email': row['email'],
            'address': row['address'],
            'eligibility_criteria': row['eligibility_criteria'],
            'application_process': row['application_process'],
            'documents_required': row['documents_required'],
            'cost': row['cost'],
            'hours_of_operation': row['hours_of_operation'],
            'languages_supported': row['languages_supported'],
            'is_active': bool(row['is_active']),
            'is_verified': bool(row['is_verified'])
        }

        # Get categories for the resource
        cursor.execute("""
        SELECT c.id, c.name, c.description
        FROM categories c
        JOIN resource_categories rc ON c.id = rc.category_id
        WHERE rc.resource_id = ?
        """, (resource_id,))

        categories = []
        for row in cursor.fetchall():
            category = {
                'id': row['id'],
                'name': row['name'],
                'description': row['description']
            }
            categories.append(category)

        resource['categories'] = categories

        # Close the connection
        conn.close()

        return jsonify({
            'success': True,
            'resource': resource
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'resource': None
        })

@app.route('/')
def index():
    """Simple web interface for testing the API."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resource Search API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .card { border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; }
            .form-group { margin-bottom: 15px; }
            input[type="text"] { width: 100%; padding: 8px; }
            button { padding: 8px 15px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .resource { margin-bottom: 20px; }
            .resource h3 { margin-top: 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Resource Search API</h1>

            <div class="card">
                <h2>Search Resources</h2>
                <div class="form-group">
                    <label for="query">Search Query:</label>
                    <input type="text" id="query" placeholder="Enter search query...">
                </div>
                <button onclick="searchResources()">Search</button>
            </div>

            <div class="card">
                <h2>API Documentation</h2>
                <h3>Search Endpoint</h3>
                <pre>/api/search?q={query}&limit={limit}&offset={offset}</pre>
                <p>Parameters:</p>
                <ul>
                    <li><strong>q</strong>: Search query (required)</li>
                    <li><strong>limit</strong>: Maximum number of results to return (default: 10)</li>
                    <li><strong>offset</strong>: Number of results to skip (default: 0)</li>
                </ul>

                <h3>Resource Endpoint</h3>
                <pre>/api/resource/{resource_id}</pre>
                <p>Parameters:</p>
                <ul>
                    <li><strong>resource_id</strong>: ID of the resource to retrieve</li>
                </ul>
            </div>

            <div class="card">
                <h2>Results</h2>
                <div id="results"></div>
            </div>
        </div>

        <script>
            function searchResources() {
                const query = document.getElementById('query').value;
                if (!query) {
                    alert('Please enter a search query');
                    return;
                }

                fetch(`/api/search?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        const resultsDiv = document.getElementById('results');

                        if (!data.success) {
                            resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                            return;
                        }

                        if (data.resources.length === 0) {
                            resultsDiv.innerHTML = `<div>No resources found matching "${query}"</div>`;
                            return;
                        }

                        let html = `<div>Found ${data.total} resources matching "${query}"</div><br>`;

                        data.resources.forEach(resource => {
                            html += `
                                <div class="resource">
                                    <h3>${resource.name}</h3>
                                    <p>${resource.description || 'No description available'}</p>
                                    <p><strong>Phone:</strong> ${resource.phone || 'N/A'}</p>
                                    <p><strong>Email:</strong> ${resource.email || 'N/A'}</p>
                                    <p><strong>Address:</strong> ${resource.address || 'N/A'}</p>
                                    <p><strong>Status:</strong> ${resource.is_active ? 'Active' : 'Inactive'} ${resource.is_verified ? '(Verified)' : ''}</p>
                                </div>
                            `;
                        });

                        resultsDiv.innerHTML = html;
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        document.getElementById('results').innerHTML = `<div class="error">Error: ${error.message}</div>`;
                    });
            }
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)
