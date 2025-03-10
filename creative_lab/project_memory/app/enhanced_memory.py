"""
Enhanced memory system with vector search capabilities.
"""
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging

logger = logging.getLogger(__name__)

class EnhancedProjectMemory:
    """Enhanced memory system with vector search and semantic understanding."""
    
    def __init__(self, base_path: Path = None):
        """Initialize the enhanced memory system."""
        if base_path is None:
            base_path = Path.cwd() / "memory_store"
        self.base_path = Path(base_path)
        self.entries_path = self.base_path / "entries"
        self.vectors_path = self.base_path / "vectors"
        
        # Create directories
        self.entries_path.mkdir(parents=True, exist_ok=True)
        self.vectors_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Initialize Qdrant client
        self.qdrant = QdrantClient(":memory:")  # In-memory storage for testing
        self.collection_name = "entries"
        
        # Create vector collection
        self.qdrant.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=384,  # all-MiniLM-L6-v2 embedding size
                distance=models.Distance.COSINE
            )
        )
        
    def encode_text(self, text: str) -> np.ndarray:
        """Generate embeddings for the given text."""
        return self.model.encode([text])[0]
        
    def search_similar(self, query: str, limit: int = 5) -> list:
        """Search for similar entries using vector similarity."""
        query_vector = self.encode_text(query)
        
        # Search in Qdrant
        search_result = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        return search_result
        
    def add_to_index(self, entry_id: str, text: str):
        """Add an entry to the vector index."""
        vector = self.encode_text(text)
        
        # Add to Qdrant
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=hash(entry_id),  # Use hash of entry_id as point id
                    vector=vector.tolist(),
                    payload={"entry_id": entry_id}
                )
            ]
        )
