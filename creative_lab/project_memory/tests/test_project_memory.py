"""
Unit tests for the Project Memory System.
Tests each component of the system to ensure proper functionality.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
import shutil
import logging
from app import ProjectMemory, app

# Set up logging
logger = logging.getLogger(__name__)

@pytest.fixture
def test_memory():
    """
    Fixture to create a test instance of ProjectMemory with a temporary directory.
    Cleans up the test directory before and after each test.
    """
    # Clean up any existing test directory
    test_base_path = Path("test_memory_store")
    if test_base_path.exists():
        logger.debug("Cleaning up existing test directory")
        shutil.rmtree(test_base_path)
    
    # Create a fresh test instance with a temporary directory
    logger.debug("Creating new test instance")
    memory = ProjectMemory(test_base_path)
    
    # Ensure all required directories exist
    memory.entries_path.mkdir(parents=True, exist_ok=True)
    memory.abstracts_path.mkdir(parents=True, exist_ok=True)
    memory.vectors_path.mkdir(parents=True, exist_ok=True)
    
    yield memory
    
    # Cleanup after test
    logger.debug("Cleaning up test directory after test")
    if test_base_path.exists():
        shutil.rmtree(test_base_path)

@pytest.fixture
def client():
    """Fixture to create a test client for Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_project_memory_initialization(test_memory):
    """Test that ProjectMemory initializes with correct directory structure"""
    assert test_memory.base_path.exists()
    assert test_memory.entries_path.exists()
    assert test_memory.abstracts_path.exists()
    assert test_memory.vectors_path.exists()

def test_save_entry_with_title(test_memory):
    """Test saving an entry with a custom title"""
    content = "This is a test entry content."
    title = "Test Entry"
    
    result = test_memory.save_entry(content, title)
    
    # Check that files were created
    assert Path(result["entry_file"]).exists()
    assert Path(result["abstract_file"]).exists()
    
    # Check entry content
    with open(result["entry_file"]) as f:
        assert f.read() == content
    
    # Check abstract metadata
    with open(result["abstract_file"]) as f:
        abstract_data = json.load(f)
        assert abstract_data["title"] == title
        assert abstract_data["original_file"] == result["entry_file"]
        assert "timestamp" in abstract_data

def test_save_entry_without_title(test_memory):
    """Test saving an entry without a title (should generate timestamp-based title)"""
    content = "This is a test entry without title."
    
    result = test_memory.save_entry(content)
    
    # Check that files were created
    assert Path(result["entry_file"]).exists()
    assert Path(result["abstract_file"]).exists()
    
    # Verify timestamp-based title format
    file_name = Path(result["entry_file"]).name
    assert file_name.startswith("entry_")
    assert "_" in file_name

def test_generate_abstract(test_memory):
    """Test abstract generation for different content lengths"""
    # Test short content
    short_content = "This is a short test content."
    short_abstract = test_memory.generate_abstract(short_content)
    assert isinstance(short_abstract, str)
    assert len(short_abstract) > 0
    
    # Test long content that requires chunking
    long_content = " ".join(["This is sentence {}".format(i) for i in range(100)])
    long_abstract = test_memory.generate_abstract(long_content)
    assert isinstance(long_abstract, str)
    assert len(long_abstract) > 0

def test_get_all_entries(test_memory):
    """Test retrieval of all entries in correct order"""
    # Create multiple entries
    entries = [
        ("First Entry", "Content 1"),
        ("Second Entry", "Content 2"),
        ("Third Entry", "Content 3")
    ]
    
    logger.debug("Creating test entries")
    import time
    for title, content in entries:
        result = test_memory.save_entry(content, title)
        logger.debug(f"Created entry: {result['id']} with title: {title}")
        logger.debug(f"Entry file exists: {Path(result['entry_file']).exists()}")
        logger.debug(f"Abstract file exists: {Path(result['abstract_file']).exists()}")
        time.sleep(1)  # Ensure unique timestamps
    
    # List directory contents
    logger.debug("Entries directory contents:")
    for f in test_memory.entries_path.glob('*'):
        logger.debug(f"  {f.name}")
    logger.debug("Abstracts directory contents:")
    for f in test_memory.abstracts_path.glob('*'):
        logger.debug(f"  {f.name}")
    
    # Get all entries
    logger.debug("Getting all entries")
    all_entries = test_memory.get_all_entries()
    logger.debug(f"Retrieved {len(all_entries)} entries")
    for entry in all_entries:
        logger.debug(f"Retrieved entry: {entry['id']} with title: {entry['title']}")
    
    # Check that we got all entries
    assert len(all_entries) == len(entries)
    
    # Check order (newest first)
    assert all_entries[0]["title"] == "Third Entry"
    assert all_entries[1]["title"] == "Second Entry"
    assert all_entries[2]["title"] == "First Entry"

def test_flask_routes(client):
    """Test Flask routes"""
    # Test index route
    response = client.get('/')
    assert response.status_code == 200
    
    # Test save_entry route
    test_entry = {
        "content": "Test content",
        "title": "Test Title"
    }
    response = client.post('/save_entry',
                         json=test_entry,
                         content_type='application/json')
    assert response.status_code == 200
    json_data = response.get_json()
    assert "entry_file" in json_data
    assert "abstract_file" in json_data
    assert json_data["title"] == test_entry["title"]
    assert json_data["content"] == test_entry["content"]

def test_invalid_save_entry(client):
    """Test save_entry route with invalid data"""
    # Test missing content
    test_entry = {
        "title": "Test Title"
    }
    response = client.post('/save_entry',
                         json=test_entry,
                         content_type='application/json')
    assert response.status_code == 400
    
    # Test empty content
    test_entry = {
        "content": "",
        "title": "Test Title"
    }
    response = client.post('/save_entry',
                         json=test_entry,
                         content_type='application/json')
    assert response.status_code == 400

def test_find_similar_entries(test_memory):
    """Test finding similar entries using vector search"""
    # Create multiple entries with varying similarity
    entries = [
        ("Machine Learning", "Deep learning models have transformed natural language processing."),
        ("Data Science", "Statistical analysis and data visualization techniques."),
        ("Computer Vision", "Image recognition using convolutional neural networks."),
        ("Gardening", "Tips for growing organic vegetables in your backyard.")
    ]
    
    logger.debug("Creating test entries for similarity search")
    for title, content in entries:
        result = test_memory.save_entry(content, title)
        logger.debug(f"Created entry: {result['id']} with title: {title}")
        import time
        time.sleep(1)  # Ensure unique timestamps
    
    # Search for ML-related entries
    query = "neural networks and deep learning"
    similar_entries = test_memory.find_similar_entries(query, limit=2)
    
    # Should find ML and CV entries as most similar
    assert len(similar_entries) == 2
    titles = [entry["title"] for entry in similar_entries]
    assert "Machine Learning" in titles
    assert "Computer Vision" in titles
    
    # Verify similarity scores
    assert all(0 <= entry["similarity"] <= 1 for entry in similar_entries)
    
    # Search for gardening-related entries
    query = "organic farming and vegetables"
    similar_entries = test_memory.find_similar_entries(query, limit=1)
    
    # Should find gardening entry as most similar
    assert len(similar_entries) == 1
    assert similar_entries[0]["title"] == "Gardening"
