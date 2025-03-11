import pytest
import os
import sys
import json
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from session_manager import CreativeSession

@pytest.fixture
def session():
    """Fixture to provide a fresh CreativeSession for each test"""
    return CreativeSession()

def test_session_creation(session):
    """Test that a new session is created with valid attributes"""
    assert session.base_path is not None
    assert isinstance(session.base_path, Path)
    assert session.session_id is not None
    assert isinstance(session.session_id, str)

def test_conversation_saving(session):
    """Test that conversations are saved correctly"""
    test_content = "Test conversation content"
    
    # Save the conversation
    file_path = session.save_conversation("test_model", test_content)
    
    # Check if file exists
    assert file_path.exists(), f"Expected file not found at {file_path}"
    
    # Verify content
    with open(file_path, 'r') as f:
        saved_content = f.read()
    assert saved_content == test_content, "Saved content doesn't match input content"

def test_links_file_creation(session):
    """Test that links.json is created on session initialization"""
    assert session.links_file.exists(), "links.json should be created automatically"
    
    # Verify it's valid JSON
    with open(session.links_file, 'r') as f:
        links_data = json.load(f)
    assert isinstance(links_data, dict), "links.json should contain a valid JSON object"

def test_directory_structure(session):
    """Test that required directories are created"""
    assert (session.base_path / "conversations").exists(), "conversations directory should exist"
    assert (session.base_path / "insights").exists(), "insights directory should exist"