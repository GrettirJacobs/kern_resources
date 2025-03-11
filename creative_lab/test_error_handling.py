import pytest
from session_manager import CreativeSession

@pytest.fixture
def session():
    """Fixture to provide a fresh CreativeSession for each test"""
    return CreativeSession()

def test_none_values(session):
    """Test handling of None values"""
    with pytest.raises(TypeError, match="must not be None"):
        session.save_conversation(None, "content")
    with pytest.raises(TypeError, match="must not be None"):
        session.save_conversation("model", None)

def test_empty_strings(session):
    """Test handling of empty strings"""
    with pytest.raises(ValueError, match="cannot be empty"):
        session.save_conversation("", "content")
    with pytest.raises(ValueError, match="cannot be empty"):
        session.save_conversation("   ", "content")

def test_wrong_types(session):
    """Test handling of incorrect types"""
    with pytest.raises(TypeError, match="must be strings"):
        session.save_conversation(123, "content")
    with pytest.raises(TypeError, match="must be strings"):
        session.save_conversation("model", 123)

def test_insight_validation(session):
    """Test insight data validation"""
    with pytest.raises(TypeError, match="must be a dictionary"):
        session.save_insight("model", "not a dict")
    with pytest.raises(TypeError, match="must not be None"):
        session.save_insight("model", None)
    with pytest.raises(TypeError, match="must be a string"):
        session.save_insight(123, {})