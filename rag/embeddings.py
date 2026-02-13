"""
Embedding generation using HuggingFace sentence-transformers
FREE local inference - no API costs
"""

from sentence_transformers import SentenceTransformer
from typing import List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using HuggingFace models (free, local)"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        """
        Initialize embedding model
        
        Args:
            model_name: HuggingFace model name
                - all-mpnet-base-v2: 768 dimensions, high quality (default)
                - all-MiniLM-L6-v2: 384 dimensions, faster but lower quality
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats (embedding vector)
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batched for efficiency)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        logger.info("Embeddings generated successfully")
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension


# Singleton instance (loaded once, reused)
_embedding_generator = None

def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create singleton embedding generator"""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator