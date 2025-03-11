import pytest
from kern_resources.core.text_utils import TextProcessor

def test_text_processor_initialization():
    processor = TextProcessor()
    assert processor.min_length == 3
    
    custom_processor = TextProcessor(min_length=4)
    assert custom_processor.min_length == 4

def test_clean_text():
    processor = TextProcessor()
    text = "  This   has    extra   spaces  "
    cleaned = processor.clean_text(text)
    assert cleaned == "This has extra spaces"

def test_split_sentences():
    processor = TextProcessor()
    text = "First sentence. Second sentence. Very short. Last sentence."
    print(f"\nDEBUG - Input text: '{text}'")  # Debug print
    
    sentences = processor.split_sentences(text)
    print(f"DEBUG - Output sentences: {sentences}")  # Debug print
    
    # More detailed assertions
    assert len(sentences) == 3, f"Expected 3 sentences, got {len(sentences)}: {sentences}"
    
    # Individual sentence checks
    expected_sentences = ["First sentence", "Second sentence", "Last sentence"]
    for expected in expected_sentences:
        assert expected in sentences, f"Missing expected sentence: '{expected}'"
    
    # Check filtered sentence
    assert "Very short" not in sentences, "'Very short' should have been filtered out"

def test_extract_keywords():
    processor = TextProcessor(min_length=4)
    text = "The quick brown fox jumps over the lazy dog"
    keywords = processor.extract_keywords(text)
    assert "the" not in keywords  # too short
    assert "quick" in keywords
    assert "brown" in keywords
    
    # Test with max_keywords
    limited_keywords = processor.extract_keywords(text, max_keywords=2)
    assert len(limited_keywords) == 2
