import pytest
import os
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from session_manager import CreativeSession

def test_session_creation():
    """Test that a new session is created with valid attributes"""
    session = CreativeSession()
    assert session.base_path is not None
    assert isinstance(session.base_path, Path)
    assert session.session_id is not None
    assert isinstance(session.session_id, str)

def test_conversation_saving():
    """Test that conversations are saved correctly"""
    session = CreativeSession()
    test_content = "Test conversation content"
    
    # Save the conversation
    session.save_conversation("test_model", test_content)
    
    # Check if file exists
    expected_path = session.base_path / "conversations" / session.session_id / "test_model_conversation.txt"
    assert expected_path.exists(), f"Expected file not found at {expected_path}"
    
    # Verify content
    with open(expected_path, 'r') as f:
        saved_content = f.read()
    assert saved_content == test_content, "Saved content doesn't match input content"