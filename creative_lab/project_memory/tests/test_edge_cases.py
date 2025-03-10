"""
Edge case tests for the Project Memory System.
Tests various boundary conditions and error scenarios.
"""

import pytest
from app import ProjectMemory
import json
from pathlib import Path

@pytest.fixture
def test_memory(tmp_path):
    """Create a test memory instance with temporary directory"""
    memory = ProjectMemory(tmp_path / "test_memory")
    return memory

def test_extremely_long_content(test_memory):
    """Test handling of extremely long content"""
    # Create a long content string (10KB)
    long_content = " ".join(["This is sentence {}".format(i) for i in range(1000)])
    
    result = test_memory.save_entry(long_content, "Long Entry")
    
    assert result["id"] is not None
    assert result["content"] == long_content
    assert result["title"] == "Long Entry"
    assert "sentiment" in result

def test_special_characters(test_memory):
    """Test handling of special characters in content and titles"""
    special_content = """
    Special characters test:
    !@#$%^&*()_+-=[]{}|;:'",.<>?/~`
    Unicode characters: ñ á é í ó ú
    Emoji: 😀 🌟 🎉
    """
    special_title = "Special!@#$%^&*()_+ Title"
    
    result = test_memory.save_entry(special_content, special_title)
    
    # Verify content is preserved
    assert result["content"] == special_content
    assert result["title"] == special_title

def test_empty_content(test_memory):
    """Test handling of empty or whitespace-only content"""
    with pytest.raises(ValueError):
        test_memory.save_entry("")
    
    with pytest.raises(ValueError):
        test_memory.save_entry("   ")

def test_duplicate_titles(test_memory):
    """Test handling of duplicate titles"""
    title = "Same Title"
    
    # Save two entries with the same title
    result1 = test_memory.save_entry("Content 1", title)
    result2 = test_memory.save_entry("Content 2", title)
    
    # Verify entries are saved with same title but different IDs
    assert result1["title"] == result2["title"]
    assert result1["id"] != result2["id"]

def test_file_system_limits(test_memory):
    """Test handling of file system limitations"""
    # Save multiple entries
    for i in range(10):
        content = f"Content for entry {i}"
        result = test_memory.save_entry(content)
        assert result["id"] is not None
        
    # Verify we can retrieve all entries
    entries = test_memory.get_all_entries()
    assert len(entries) == 10

@pytest.mark.asyncio
async def test_concurrent_access(test_memory):
    """Test handling of concurrent access"""
    import asyncio
    
    async def save_entry(content):
        return test_memory.save_entry(content)
    
    # Create multiple concurrent save operations
    contents = [f"Concurrent content {i}" for i in range(5)]
    tasks = [save_entry(content) for content in contents]
    
    # Run concurrently
    results = await asyncio.gather(*tasks)
    
    # Verify all entries were saved
    assert len(results) == 5
    assert all(r["id"] is not None for r in results)

def test_memory_cleanup(test_memory):
    """Test system cleanup and resource management"""
    # Save some entries
    entries = []
    for i in range(3):
        result = test_memory.save_entry(f"Content {i}")
        entries.append(result)
    
    # Verify files exist
    for entry in entries:
        entry_file = test_memory.entries_path / f"{entry['id']}.json"
        vector_file = test_memory.vectors_path / f"{entry['id']}.npy"
        assert entry_file.exists()
        assert vector_file.exists()
