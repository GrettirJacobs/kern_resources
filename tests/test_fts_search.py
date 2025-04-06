"""
Test script for the FTS5 search implementation.

This script tests:
1. Setting up the FTS5 index
2. Searching using the FTS5 index
3. API endpoints for search
"""

import os
import sys
import unittest
import json
import sqlite3
import requests
from contextlib import closing

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules to test
import setup_fts_index
from fts_search_api import app

class TestFTS5Search(unittest.TestCase):
    """Test the FTS5 search implementation."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test database
        self.db_path = 'test_resources.db'
        self.create_test_database()
        
        # Set up the FTS5 index
        setup_fts_index.setup_fts_index(self.db_path)
        
        # Set up the Flask test client
        app.config['TESTING'] = True
        self.client = app.test_client()

    def tearDown(self):
        """Clean up after the tests."""
        # Remove the test database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def create_test_database(self):
        """Create a test database with sample resources."""
        # Remove existing database if it exists
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        # Connect to the database
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Create resources table
            cursor.execute('''
            CREATE TABLE resources (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                url TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                eligibility_criteria TEXT,
                application_process TEXT,
                documents_required TEXT,
                cost TEXT,
                hours_of_operation TEXT,
                languages_supported TEXT,
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                verification_notes TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create categories table
            cursor.execute('''
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create resource_categories table
            cursor.execute('''
            CREATE TABLE resource_categories (
                resource_id INTEGER,
                category_id INTEGER,
                PRIMARY KEY (resource_id, category_id),
                FOREIGN KEY (resource_id) REFERENCES resources (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
            ''')
            
            # Insert sample resources
            resources = [
                (1, "Food Bank of Kern County", "Provides food assistance to those in need", "http://example.com", "555-1234", "info@foodbank.org", "123 Main St", "Low income", "Walk-in", "ID", "Free", "9-5", "English, Spanish", 1, 0, "", "", "2023-01-01", "2023-01-01"),
                (2, "Community Action Partnership of Kern (CAPK) Food Bank", "Distributes food to those in need throughout Kern County", "http://example.com", "555-5678", "info@capk.org", "456 Oak St", "Low income", "Appointment", "ID, Proof of income", "Free", "10-4", "English, Spanish", 1, 1, "Verified by admin", "", "2023-01-02", "2023-01-02"),
                (3, "Bakersfield Rescue Mission", "Provides shelter and meals to homeless individuals", "http://example.com", "555-9012", "info@rescue.org", "789 Pine St", "Homeless", "Walk-in", "None", "Free", "24/7", "English", 1, 0, "", "", "2023-01-03", "2023-01-03"),
                (4, "Kern County Department of Human Services", "Administers CalWORKs (cash aid), General Assistance, and CalFresh (food stamps)", "http://example.com", "555-3456", "info@dhs.org", "321 Elm St", "Low income", "Application", "ID, Proof of income, Residency", "Free", "8-5", "English, Spanish", 1, 1, "Verified by admin", "", "2023-01-04", "2023-01-04"),
                (5, "Medical Clinic", "Provides medical services to low-income individuals", "http://example.com", "555-7890", "info@clinic.org", "654 Maple St", "Low income", "Appointment", "ID, Insurance", "Sliding scale", "9-6", "English, Spanish", 1, 0, "", "", "2023-01-05", "2023-01-05")
            ]
            
            cursor.executemany('''
            INSERT INTO resources (id, name, description, url, phone, email, address, eligibility_criteria, application_process, documents_required, cost, hours_of_operation, languages_supported, is_active, is_verified, verification_notes, image_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', resources)
            
            # Insert sample categories
            categories = [
                (1, "Food", "Food assistance resources"),
                (2, "Housing", "Housing assistance resources"),
                (3, "Medical", "Medical assistance resources"),
                (4, "Financial", "Financial assistance resources")
            ]
            
            cursor.executemany('''
            INSERT INTO categories (id, name, description)
            VALUES (?, ?, ?)
            ''', categories)
            
            # Insert sample resource_categories
            resource_categories = [
                (1, 1),  # Food Bank of Kern County - Food
                (2, 1),  # CAPK Food Bank - Food
                (3, 1),  # Bakersfield Rescue Mission - Food
                (3, 2),  # Bakersfield Rescue Mission - Housing
                (4, 1),  # Kern County Department of Human Services - Food
                (4, 4),  # Kern County Department of Human Services - Financial
                (5, 3)   # Medical Clinic - Medical
            ]
            
            cursor.executemany('''
            INSERT INTO resource_categories (resource_id, category_id)
            VALUES (?, ?)
            ''', resource_categories)
            
            # Commit changes
            conn.commit()

    def test_fts5_index_setup(self):
        """Test that the FTS5 index is set up correctly."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Check if the FTS5 table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='resource_fts'")
            self.assertIsNotNone(cursor.fetchone(), "FTS5 table does not exist")
            
            # Check if the triggers exist
            for trigger_name in ['resources_ai', 'resources_au', 'resources_ad']:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='trigger' AND name='{trigger_name}'")
                self.assertIsNotNone(cursor.fetchone(), f"Trigger {trigger_name} does not exist")

    def test_fts5_search(self):
        """Test searching using the FTS5 index."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Search for resources with 'food' in their name or description
            cursor.execute("""
            SELECT r.id, r.name, r.description
            FROM resources r
            JOIN resource_fts fts ON r.id = fts.rowid
            WHERE resource_fts MATCH ?
            """, ("food",))
            
            results = cursor.fetchall()
            self.assertGreater(len(results), 0, "No resources found matching 'food'")
            
            # Check that the Food Bank is in the results
            food_bank_found = False
            for result in results:
                if result['name'] == "Food Bank of Kern County":
                    food_bank_found = True
                    break
            
            self.assertTrue(food_bank_found, "Food Bank of Kern County not found in search results")

    def test_api_search_endpoint(self):
        """Test the search API endpoint."""
        # Set the database path for the API
        app.config['DATABASE_PATH'] = self.db_path
        
        # Make a request to the search endpoint
        response = self.client.get('/api/search?q=food')
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200, "API request failed")
        
        # Parse the response
        data = json.loads(response.data)
        
        # Check that the response contains resources
        self.assertTrue(data['success'], "API response indicates failure")
        self.assertGreater(len(data['resources']), 0, "No resources found in API response")
        
        # Check that the Food Bank is in the results
        food_bank_found = False
        for resource in data['resources']:
            if resource['name'] == "Food Bank of Kern County":
                food_bank_found = True
                break
        
        self.assertTrue(food_bank_found, "Food Bank of Kern County not found in API response")

    def test_api_resource_endpoint(self):
        """Test the resource API endpoint."""
        # Set the database path for the API
        app.config['DATABASE_PATH'] = self.db_path
        
        # Make a request to the resource endpoint
        response = self.client.get('/api/resource/1')
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200, "API request failed")
        
        # Parse the response
        data = json.loads(response.data)
        
        # Check that the response contains the resource
        self.assertTrue(data['success'], "API response indicates failure")
        self.assertEqual(data['resource']['name'], "Food Bank of Kern County", "Wrong resource returned")

if __name__ == '__main__':
    unittest.main()
