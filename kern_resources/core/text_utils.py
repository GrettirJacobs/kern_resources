from typing import List, Optional
import re

class TextProcessor:
    def __init__(self, min_length: int = 3):
        self.min_length = min_length
    
    def clean_text(self, text: str) -> str:
        """Basic text cleaning."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences and filter by minimum word count."""
        # First clean the text
        text = self.clean_text(text)
        print(f"DEBUG - Cleaned text: '{text}'")  # Debug print
        
        # Split into sentences
        raw_sentences = [s.strip() for s in text.split('.') if s.strip()]
        print(f"DEBUG - Raw sentences: {raw_sentences}")  # Debug print
        
        # Filter sentences by word count and total length
        sentences = []
        for sentence in raw_sentences:
            words = sentence.split()
            word_count = len(words)
            total_chars = len(sentence)
            print(f"DEBUG - Sentence: '{sentence}', Word count: {word_count}, Chars: {total_chars}")  # Debug print
            
            # Keep sentences with 2+ words AND more than 11 characters
            if word_count >= 2 and total_chars > 11:
                sentences.append(sentence)
        
        print(f"DEBUG - Final sentences: {sentences}")  # Debug print
        return sentences
    
    def extract_keywords(self, text: str, max_keywords: Optional[int] = None) -> List[str]:
        """Extract potential keywords from text."""
        # Simple word frequency-based extraction
        words = text.lower().split()
        words = [w for w in words if len(w) >= self.min_length]
        if max_keywords:
            return words[:max_keywords]
        return words
