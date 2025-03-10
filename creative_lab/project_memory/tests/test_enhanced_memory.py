"""
Tests for the enhanced memory system functionality.
"""

import pytest
from pathlib import Path
import json
import shutil
from app.enhanced_memory import EnhancedProjectMemory

@pytest.fixture
def temp_memory(tmp_path):
    """Create a temporary memory system for testing."""
    memory = EnhancedProjectMemory(tmp_path)
    yield memory
    # Cleanup
    shutil.rmtree(tmp_path)

def test_save_entry_basic(temp_memory):
    """Test basic entry saving functionality."""
    content = "This is a test entry about artificial intelligence and machine learning."
    result = temp_memory.save_entry(content)
    
    assert result["entry_file"].endswith(".txt")
    assert result["abstract_file"].endswith(".json")
    assert "abstract" in result
    assert "sentiment" in result
    assert "tags" in result
    
    # Check if files were created
    assert Path(result["entry_file"]).exists()
    assert Path(result["abstract_file"]).exists()

def test_save_entry_with_title(temp_memory):
    """Test entry saving with a custom title."""
    content = "Test content"
    title = "Custom Title"
    result = temp_memory.save_entry(content, title)
    
    assert title in result["entry_file"]
    assert title in result["abstract_file"]

def test_save_entry_empty_content(temp_memory):
    """Test handling of empty content."""
    with pytest.raises(ValueError):
        temp_memory.save_entry("")
    
    with pytest.raises(ValueError):
        temp_memory.save_entry("   ")

def test_find_related_entries(temp_memory):
    """Test finding related entries."""
    # Save multiple entries
    entries = [
        "Artificial intelligence is transforming technology",
        "Machine learning algorithms are becoming more sophisticated",
        "Climate change affects global weather patterns",
        "Neural networks can recognize patterns in data"
    ]
    
    for entry in entries:
        temp_memory.save_entry(entry)
    
    # Search for AI-related content
    results = temp_memory.find_related_entries("AI and machine learning", top_n=2)
    
    assert len(results) <= 2
    assert isinstance(results, list)
    assert all("distance" in result for result in results)
    assert all("metadata" in result for result in results)

def test_sentiment_analysis(temp_memory):
    """Test sentiment analysis functionality."""
    # Test positive sentiment
    positive_content = "I love how this project is coming together beautifully!"
    pos_result = temp_memory.save_entry(positive_content)
    assert pos_result["sentiment"] > 0
    
    # Test negative sentiment
    negative_content = "This is terrible and frustrating."
    neg_result = temp_memory.save_entry(negative_content)
    assert neg_result["sentiment"] < 0
    
    # Test neutral sentiment
    neutral_content = "The project contains multiple components."
    neut_result = temp_memory.save_entry(neutral_content)
    assert abs(neut_result["sentiment"]) < 0.5

def test_tag_generation(temp_memory):
    """Test automatic tag generation."""
    content = "Artificial intelligence and machine learning are revolutionizing technology"
    result = temp_memory.save_entry(content)
    
    assert "tags" in result
    assert len(result["tags"]) > 0
    assert any("intelligence" in tag.lower() or "learning" in tag.lower() 
              for tag in result["tags"])

def test_knowledge_graph_generation(temp_memory):
    """Test knowledge graph visualization."""
    # Add some related entries
    entries = [
        "Python programming basics",
        "Advanced Python concepts",
        "Python web development",
        "JavaScript fundamentals"
    ]
    
    for entry in entries:
        temp_memory.save_entry(entry)
    
    graph_html = temp_memory.generate_knowledge_graph()
    
    assert isinstance(graph_html, str)
    assert "plotly" in graph_html.lower()
    assert any(entry.lower() in graph_html.lower() for entry in entries)

def test_long_content_handling(temp_memory):
    """Test handling of long content."""
    # Generate a long piece of content
    long_content = " ".join(["This is sentence number " + str(i) for i in range(100)])
    result = temp_memory.save_entry(long_content)
    
    assert result["entry_file"].endswith(".txt")
    assert result["abstract_file"].endswith(".json")
    
    # Verify the content was properly saved
    saved_content = Path(result["entry_file"]).read_text()
    assert saved_content == long_content

def test_special_characters(temp_memory):
    """Test handling of special characters in content and titles."""
    content = "Special chars: !@#$%^&*()_+-=[]{}|;:,.<>?"
    title = "Test !@#$%^&*()"
    result = temp_memory.save_entry(content, title)
    
    # Check if files were created with sanitized names
    assert Path(result["entry_file"]).exists()
    assert Path(result["abstract_file"]).exists()
    
    # Verify content was saved correctly
    saved_content = Path(result["entry_file"]).read_text()
    assert saved_content == content

def test_concurrent_entries(temp_memory):
    """Test saving multiple entries rapidly."""
    import concurrent.futures
    
    def save_entry(i):
        return temp_memory.save_entry(f"Test content {i}", f"Title {i}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(save_entry, i) for i in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    assert len(results) == 10
    assert len(set(r["entry_file"] for r in results)) == 10  # All files should be unique
