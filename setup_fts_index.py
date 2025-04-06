"""
Set up Full-Text Search (FTS5) index for resources.

This script:
1. Creates an FTS5 virtual table for resources
2. Populates it with existing resource data
3. Sets up triggers to keep the index in sync with the resources table
"""

import sqlite3
import os
import sys

def setup_fts_index(db_path='resources.db'):
    """Set up FTS5 index for resources."""
    print(f"Setting up FTS5 index for database at {db_path}")

    # Check if the database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False

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

if __name__ == "__main__":
    # Get database path from command line arguments or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'resources.db'

    if setup_fts_index(db_path):
        print("FTS5 index setup completed successfully")
    else:
        print("Failed to set up FTS5 index")
        sys.exit(1)
