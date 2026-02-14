import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing RAG connection from agent context...")

# Simulate what rag_agent.py does
from rag.retrieval import RAGRetriever

try:
    print("Creating RAGRetriever...")
    retriever = RAGRetriever(top_k=5)
    print("✅ SUCCESS! RAGRetriever created")
    print(f"Connected to: {retriever.collection_name}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()