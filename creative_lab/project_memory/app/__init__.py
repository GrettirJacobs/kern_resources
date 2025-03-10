"""
Project Memory System - Core Package
"""

from flask import Flask
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import json
import numpy as np
import logging
from .enhanced_memory import EnhancedProjectMemory
from qdrant_client import QdrantClient

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create base Flask application
app = Flask(__name__)

class ProjectMemory(EnhancedProjectMemory):
    """
    Main project memory interface that extends EnhancedProjectMemory.
    Provides backward compatibility with original ProjectMemory interface.
    """
    def __init__(self, base_path: Path = None):
        super().__init__(base_path)
        self.abstracts_path = self.base_path / "abstracts"
        self.abstracts_path.mkdir(parents=True, exist_ok=True)
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        self.qdrant_client.recreate_collection(
            collection_name="project_memory",
            vectors_config={
                "size": 4,
                "distance": "Cosine"
            }
        )
        logger.debug(f"Initialized ProjectMemory with base_path: {self.base_path}")
        
    def save_entry(self, content: str, title: Optional[str] = None) -> Dict:
        """Save a new memory entry with backward compatibility"""
        if not content or not content.strip():
            raise ValueError("Content cannot be empty or whitespace-only")
            
        # Generate timestamp for filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        entry_id = f"entry_{timestamp}"
        
        # Save raw content to entry file
        entry_file = self.entries_path / f"{entry_id}.txt"
        entry_file.write_text(content, encoding='utf-8')
        logger.debug(f"Saved entry content to {entry_file}")
        
        # Generate and save abstract with metadata
        abstract = self.generate_abstract(content)
        abstract_file = self.abstracts_path / f"{entry_id}.json"
        abstract_data = {
            "title": title or f"Entry {timestamp}",
            "abstract": abstract,
            "original_file": str(entry_file),
            "timestamp": datetime.utcnow().isoformat()
        }
        with open(abstract_file, 'w', encoding='utf-8') as f:
            json.dump(abstract_data, f, ensure_ascii=False, indent=2)
        logger.debug(f"Saved abstract to {abstract_file}")
        
        # Add to vector search index
        self.add_to_index(entry_id, content)
        logger.debug(f"Added entry to vector index: {entry_id}")
        
        # Create result
        result = {
            'id': entry_id,
            'title': title or f"Entry {timestamp}",
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'entry_file': str(entry_file),
            'abstract_file': str(abstract_file),
            'abstract': abstract
        }
        
        return result
        
    def get_all_entries(self) -> List[Dict]:
        """Get all entries sorted by timestamp"""
        entries = []
        logger.debug(f"Searching for entries in {self.entries_path}")
        
        # Look for all txt files in entries directory
        entry_files = list(self.entries_path.glob('*.txt'))
        logger.debug(f"Found {len(entry_files)} entry files: {[f.name for f in entry_files]}")
        
        for entry_file in entry_files:
            entry_id = entry_file.stem
            abstract_file = self.abstracts_path / f"{entry_id}.json"
            
            logger.debug(f"Processing entry {entry_id}")
            logger.debug(f"Abstract file exists: {abstract_file.exists()}")
            
            if abstract_file.exists():
                try:
                    # Load abstract metadata
                    with open(abstract_file, 'r', encoding='utf-8') as f:
                        abstract_data = json.load(f)
                        
                    # Load content
                    content = entry_file.read_text(encoding='utf-8')
                    
                    # Create entry
                    entry = {
                        'id': entry_id,
                        'title': abstract_data['title'],
                        'content': content,
                        'timestamp': abstract_data['timestamp'],
                        'entry_file': str(entry_file),
                        'abstract_file': str(abstract_file),
                        'abstract': abstract_data['abstract']
                    }
                    entries.append(entry)
                    logger.debug(f"Added entry {entry_id} to results")
                except Exception as e:
                    logger.error(f"Error processing entry {entry_id}: {str(e)}")
                
        # Sort by timestamp, newest first
        sorted_entries = sorted(entries, key=lambda x: x['timestamp'], reverse=True)
        logger.debug(f"Returning {len(sorted_entries)} entries")
        return sorted_entries
        
    def generate_abstract(self, content: str) -> str:
        """Generate an abstract for the given content"""
        # For now, return a simple truncated version
        max_length = 200
        if len(content) <= max_length:
            return content
        return content[:max_length].rsplit(' ', 1)[0] + '...'
        
    def add_to_index(self, entry_id: str, content: str):
        """Add entry to vector search index"""
        vector = self.model.encode([content])[0]
        self.qdrant_client.upload_collection(
            collection_name="project_memory",
            vectors=[{"id": entry_id, "payload": {"entry_id": entry_id}, "vector": vector}]
        )
        
    def search_similar(self, query: str, limit: int = 5):
        """Search for similar entries"""
        vector = self.model.encode([query])[0]
        return self.qdrant_client.search(
            collection_name="project_memory",
            query_vector=vector,
            limit=limit
        )
        
    def find_similar_entries(self, query: str, limit: int = 5) -> List[Dict]:
        """Find entries similar to the query text"""
        logger.debug(f"Searching for entries similar to query: {query[:50]}...")
        
        # Get similar entries from vector search
        similar = self.search_similar(query, limit=limit)
        
        # Load full entries
        results = []
        for match in similar:
            entry_id = match.payload['entry_id']
            entry_file = self.entries_path / f"{entry_id}.txt"
            abstract_file = self.abstracts_path / f"{entry_id}.json"
            
            if entry_file.exists() and abstract_file.exists():
                try:
                    content = entry_file.read_text(encoding='utf-8')
                    with open(abstract_file, 'r', encoding='utf-8') as f:
                        abstract_data = json.load(f)
                        
                    entry = {
                        'id': entry_id,
                        'title': abstract_data['title'],
                        'content': content,
                        'timestamp': abstract_data['timestamp'],
                        'entry_file': str(entry_file),
                        'abstract_file': str(abstract_file),
                        'abstract': abstract_data['abstract'],
                        'similarity': match.score
                    }
                    results.append(entry)
                except Exception as e:
                    logger.error(f"Error loading similar entry {entry_id}: {str(e)}")
        
        return results

# Initialize the project memory instance
memory = ProjectMemory()

# Import routes after app and memory are initialized
from . import routes

__all__ = ['ProjectMemory', 'app', 'memory']
