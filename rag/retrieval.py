"""
RAG Retrieval: Query Qdrant for relevant document chunks
"""

import os
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import logging
from rag.embeddings import get_embedding_generator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "compliance_policies"
DEFAULT_TOP_K = 5  # Number of chunks to retrieve


class RAGRetriever:
    """Retrieve relevant chunks from Qdrant vector database"""
    
    def __init__(self, top_k: int = DEFAULT_TOP_K):
        """
        Initialize retriever
        
        Args:
            top_k: Number of most relevant chunks to retrieve
        """
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.embedding_generator = get_embedding_generator()
        self.collection_name = COLLECTION_NAME
        self.top_k = top_k
        
        # Verify collection exists
        self._verify_collection()
    
    def _verify_collection(self):
        """Check if collection exists"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                raise ValueError(
                    f"Collection '{self.collection_name}' does not exist. "
                    f"Run ingest_pipeline.py first to create and populate the collection."
                )
            
            # Get collection info
            collection_info = self.client.get_collection(self.collection_name)
            logger.info(f"Connected to collection: {self.collection_name}")
            logger.info(f"Total vectors in collection: {collection_info.points_count}")
        
        except Exception as e:
            logger.error(f"Error verifying collection: {e}")
            raise
    
    def search(
        self, 
        query: str, 
        top_k: int = None,
        document_filter: str = None
    ) -> List[Dict]:
        """
        Search for relevant chunks using semantic similarity
        
        Args:
            query: User's question or search query
            top_k: Number of results to return (uses default if None)
            document_filter: Optional filter by document name
            
        Returns:
            List of relevant chunks with metadata and scores
        """
        if top_k is None:
            top_k = self.top_k
        
        logger.info(f"Searching for: '{query}' (top_k={top_k})")
        
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Optional filter by document
        query_filter = None
        if document_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_name",
                        match=MatchValue(value=document_filter)
                    )
                ]
            )
        
        # Search Qdrant
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=query_filter
        )
        
        # Format results
        results = []
        for idx, result in enumerate(search_results):
            results.append({
                "rank": idx + 1,
                "text": result.payload["text"],
                "document_name": result.payload["document_name"],
                "document_category": result.payload["document_category"],
                "chunk_index": result.payload["chunk_index"],
                "similarity_score": result.score,
                "id": result.id
            })
        
        logger.info(f"Found {len(results)} relevant chunks")
        return results
    
    def get_context_for_llm(self, query: str, top_k: int = None) -> str:
        """
        Get formatted context for LLM prompt
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            Formatted context string ready for LLM
        """
        results = self.search(query, top_k)
        
        if not results:
            return "No relevant information found in the knowledge base."
        
        # Format context
        context_parts = []
        context_parts.append("RELEVANT POLICY EXCERPTS:\n")
        
        for result in results:
            context_parts.append(
                f"\n--- Source: {result['document_name']} (Relevance: {result['similarity_score']:.2f}) ---\n"
                f"{result['text']}\n"
            )
        
        return "\n".join(context_parts)
    
    def answer_question(self, question: str, top_k: int = None) -> Dict:
        """
        Answer a compliance question using RAG
        
        Args:
            question: Compliance question
            top_k: Number of chunks to use
            
        Returns:
            Dict with answer, sources, and metadata
        """
        # Retrieve relevant chunks
        results = self.search(question, top_k)
        
        if not results:
            return {
                "question": question,
                "answer": "No relevant policy information found.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Build context
        context = self.get_context_for_llm(question, top_k)
        
        # Calculate average confidence
        avg_confidence = sum(r["similarity_score"] for r in results) / len(results)
        
        # Extract unique sources
        sources = list(set(r["document_name"] for r in results))
        
        return {
            "question": question,
            "context": context,
            "sources": sources,
            "confidence": avg_confidence,
            "num_chunks_used": len(results),
            "chunks": results  # Full chunk details
        }


def test_retrieval():
    """Test the RAG retrieval system"""
    
    print("=" * 80)
    print("TESTING RAG RETRIEVAL SYSTEM")
    print("=" * 80)
    
    # Initialize retriever
    retriever = RAGRetriever(top_k=3)
    
    # Test queries
    test_queries = [
        "What export licenses are required for UK textile exports?",
        "What are the OECD due diligence requirements?",
        "What documents are needed for customs clearance?",
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 80}")
        print(f"QUERY: {query}")
        print('=' * 80)
        
        result = retriever.answer_question(query, top_k=3)
        
        print(f"\nConfidence: {result['confidence']:.2f}")
        print(f"Sources: {', '.join(result['sources'])}")
        print(f"\nCONTEXT:")
        print(result['context'])
        print("\n")


if __name__ == "__main__":
    test_retrieval()