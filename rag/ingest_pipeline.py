"""
RAG Ingestion Pipeline: PDF -> Chunks -> Embeddings -> Qdrant
"""

import os
import PyPDF2
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging
from pathlib import Path
from embeddings import get_embedding_generator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CHUNK_SIZE = 700  # tokens (roughly 500-600 words)
CHUNK_OVERLAP = 100  # tokens overlap between chunks
RAW_DOCUMENTS_PATH = "data/raw_documents"
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "compliance_policies"


class PDFChunker:
    """Split PDF documents into overlapping chunks"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        logger.info(f"Extracting text from: {pdf_path}")
        text = ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                logger.info(f"PDF has {num_pages} pages")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise
        
        logger.info(f"Extracted {len(text)} characters")
        return text
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Full text to chunk
            metadata: Document metadata (name, category, etc.)
            
        Returns:
            List of chunks with metadata
        """
        # Simple word-based chunking (approximation of tokens)
        words = text.split()
        chunks = []
        
        # Approximate: 1 token ≈ 0.75 words
        words_per_chunk = int(self.chunk_size * 0.75)
        words_overlap = int(self.chunk_overlap * 0.75)
        
        for i in range(0, len(words), words_per_chunk - words_overlap):
            chunk_words = words[i:i + words_per_chunk]
            chunk_text = " ".join(chunk_words)
            
            if len(chunk_text.strip()) > 50:  # Skip very small chunks
                chunks.append({
                    "text": chunk_text,
                    "chunk_index": len(chunks),
                    "document_name": metadata["document_name"],
                    "document_category": metadata.get("document_category", "general"),
                })
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks


class QdrantIngestion:
    """Ingest chunks into Qdrant vector database"""
    
    def __init__(self):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.embedding_generator = get_embedding_generator()
        self.collection_name = COLLECTION_NAME
    
    def create_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists. Deleting...")
                self.client.delete_collection(self.collection_name)
            
            # Create new collection
            logger.info(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_generator.get_dimension(),
                    distance=Distance.COSINE
                )
            )
            logger.info("Collection created successfully")
        
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def ingest_chunks(self, chunks: List[Dict]):
        """
        Generate embeddings and store chunks in Qdrant
        
        Args:
            chunks: List of text chunks with metadata
        """
        logger.info(f"Ingesting {len(chunks)} chunks into Qdrant...")
        
        # Extract texts for embedding
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings (batched)
        embeddings = self.embedding_generator.generate_embeddings(texts)
        
        # Create points for Qdrant
        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=idx,
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "document_name": chunk["document_name"],
                    "document_category": chunk["document_category"],
                    "chunk_index": chunk["chunk_index"]
                }
            )
            points.append(point)
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logger.info(f"Successfully ingested {len(points)} chunks")


def ingest_all_documents():
    """Main ingestion pipeline: Read all PDFs and ingest into Qdrant"""
    
    logger.info("=" * 80)
    logger.info("STARTING RAG INGESTION PIPELINE")
    logger.info("=" * 80)
    
    # Initialize components
    chunker = PDFChunker()
    qdrant_ingest = QdrantIngestion()
    
    # Create Qdrant collection
    qdrant_ingest.create_collection()
    
    # Find all PDFs
    pdf_dir = Path(RAW_DOCUMENTS_PATH)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.error(f"No PDF files found in {RAW_DOCUMENTS_PATH}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    all_chunks = []
    
    # Process each PDF
    for pdf_file in pdf_files:
        logger.info(f"\nProcessing: {pdf_file.name}")
        
        # Extract text
        text = chunker.extract_text_from_pdf(str(pdf_file))
        
        # Create metadata
        metadata = {
            "document_name": pdf_file.name,
            "document_category": "compliance"  # Can be customized per document
        }
        
        # Chunk text
        chunks = chunker.chunk_text(text, metadata)
        all_chunks.extend(chunks)
    
    # Ingest all chunks into Qdrant
    logger.info(f"\nTotal chunks across all documents: {len(all_chunks)}")
    qdrant_ingest.ingest_chunks(all_chunks)
    
    logger.info("=" * 80)
    logger.info("RAG INGESTION PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)


if __name__ == "__main__":
    ingest_all_documents()