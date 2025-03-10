"""
AI model integration tests for the Project Memory System.
Tests the interaction with the BART-large-CNN model and its summarization capabilities.
"""

import pytest
from app import ProjectMemory
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize

@pytest.fixture
def test_memory(tmp_path):
    """Create a test memory instance with temporary directory"""
    memory = ProjectMemory()
    memory.base_path = tmp_path / "test_memory"
    memory.entries_path = memory.base_path / "entries"
    memory.abstracts_path = memory.base_path / "abstracts"
    memory.entries_path.mkdir(parents=True)
    memory.abstracts_path.mkdir(parents=True)
    return memory

def test_model_initialization():
    """Test AI model initialization and basic functionality"""
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Test basic summarization
    test_text = "This is a test sentence. It should be summarized by the model."
    summary = summarizer(test_text, max_length=130, min_length=30, do_sample=False)
    
    assert isinstance(summary, list)
    assert len(summary) > 0
    assert "summary_text" in summary[0]
    assert isinstance(summary[0]["summary_text"], str)

def test_abstract_quality(test_memory):
    """Test the quality of generated abstracts"""
    # Test with different types of content
    test_cases = [
        {
            "content": "The quick brown fox jumps over the lazy dog. "
                      "This simple sentence contains every letter of the English alphabet.",
            "expected_keywords": ["fox", "dog", "alphabet"]
        },
        {
            "content": "Python is a high-level programming language. "
                      "It emphasizes code readability and allows programmers to express concepts in fewer lines of code.",
            "expected_keywords": ["Python", "programming", "code"]
        }
    ]
    
    for case in test_cases:
        abstract = test_memory.generate_abstract(case["content"])
        
        # Check if abstract contains key concepts
        for keyword in case["expected_keywords"]:
            assert keyword.lower() in abstract.lower(), f"Abstract should contain '{keyword}'"
        
        # Check abstract length is reasonable
        assert len(abstract) < len(case["content"])
        assert len(abstract) > len(case["content"]) / 10

def test_model_consistency(test_memory):
    """Test consistency of abstract generation"""
    content = "This is a test of model consistency. The model should generate similar abstracts for similar content."
    
    # Generate multiple abstracts for the same content
    abstracts = [
        test_memory.generate_abstract(content)
        for _ in range(3)
    ]
    
    # Compare abstracts for similarity
    from difflib import SequenceMatcher
    
    def similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()
    
    # Check that abstracts are similar but not identical
    for i in range(len(abstracts)):
        for j in range(i + 1, len(abstracts)):
            sim_ratio = similarity(abstracts[i], abstracts[j])
            assert 0.7 < sim_ratio < 1.0, "Abstracts should be similar but not identical"

def test_chunking_consistency(test_memory):
    """Test that chunking doesn't affect abstract quality"""
    # Create content that will require chunking
    short_content = "This is a short test content."
    long_content = short_content * 50
    
    # Generate abstracts
    short_abstract = test_memory.generate_abstract(short_content)
    long_abstract = test_memory.generate_abstract(long_content)
    
    # Verify that long abstract maintains coherence
    assert len(long_abstract.split()) > len(short_abstract.split())
    assert "." in long_abstract  # Should contain complete sentences
    
    # Check for sentence structure
    sentences = sent_tokenize(long_abstract)
    for sentence in sentences:
        # Each sentence should be properly capitalized and end with punctuation
        assert sentence[0].isupper()
        assert sentence[-1] in ".!?"

def test_model_error_handling(test_memory):
    """Test handling of model errors and edge cases"""
    # Test with invalid input types
    with pytest.raises(Exception):
        test_memory.generate_abstract(None)
    
    with pytest.raises(Exception):
        test_memory.generate_abstract(123)
    
    # Test with extremely short input
    very_short = "Hi"
    short_abstract = test_memory.generate_abstract(very_short)
    assert isinstance(short_abstract, str)
    assert len(short_abstract) > 0
    
    # Test with special characters and formatting
    special_content = "**Bold** _italic_ ```code``` [link](http://example.com)"
    special_abstract = test_memory.generate_abstract(special_content)
    assert isinstance(special_abstract, str)
    assert len(special_abstract) > 0

def test_model_memory_management(test_memory):
    """Test model memory management during processing"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Process multiple large texts
    large_content = " ".join(["Sentence {}".format(i) for i in range(1000)])
    abstracts = []
    
    for _ in range(5):
        abstract = test_memory.generate_abstract(large_content)
        abstracts.append(abstract)
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Check memory usage is reasonable
    assert memory_increase < 500 * 1024 * 1024  # Less than 500MB increase
    
    # Verify all abstracts were generated successfully
    assert len(abstracts) == 5
    for abstract in abstracts:
        assert isinstance(abstract, str)
        assert len(abstract) > 0
