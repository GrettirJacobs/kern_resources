import numpy as np
import pytest
from kern_resources.core.embeddings import EmbeddingsHandler

def test_embeddings_initialization():
    handler = EmbeddingsHandler()
    assert handler.model_name == "all-MiniLM-L6-v2"
    assert handler.dimension == 384

def test_encode_text():
    handler = EmbeddingsHandler(dimension=5)
    embedding = handler.encode_text("test text")
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (5,)

def test_batch_encode():
    handler = EmbeddingsHandler(dimension=3)
    texts = ["first text", "second text", "third text"]
    embeddings = handler.batch_encode(texts)
    assert len(embeddings) == 3
    assert all(isinstance(emb, np.ndarray) for emb in embeddings)
    assert all(emb.shape == (3,) for emb in embeddings)

def test_similarity():
    handler = EmbeddingsHandler()
    emb1 = np.array([1.0, 0.0, 0.0])
    emb2 = np.array([1.0, 0.0, 0.0])
    emb3 = np.array([0.0, 1.0, 0.0])
    
    # Same vectors should have similarity 1.0
    assert handler.similarity(emb1, emb2) == 1.0
    # Orthogonal vectors should have similarity 0.0
    assert handler.similarity(emb1, emb3) == 0.0
