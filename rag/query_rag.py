"""
Interactive RAG Query Tool
Run this to ask questions to the knowledge base
"""

from retrieval import RAGRetriever
import sys


def main():
    """Interactive query loop"""
    
    print("\n" + "=" * 80)
    print("RAG KNOWLEDGE BASE QUERY TOOL")
    print("=" * 80)
    print("\nInitializing retriever...")
    
    retriever = RAGRetriever(top_k=5)
    
    print("\nReady! Ask questions about compliance policies.")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        # Get user input
        try:
            query = input("\n🔍 Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nExiting...")
            break
        
        if not query:
            continue
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("\nExiting...")
            break
        
        # Search
        print("\nSearching...")
        result = retriever.answer_question(query, top_k=5)
        
        # Display results
        print("\n" + "-" * 80)
        print(f"📊 Confidence: {result['confidence']:.2%}")
        print(f"📚 Sources: {', '.join(result['sources'])}")
        print(f"📄 Chunks used: {result['num_chunks_used']}")
        print("-" * 80)
        
        print("\n📖 RELEVANT INFORMATION:\n")
        for idx, chunk in enumerate(result['chunks'][:3], 1):  # Show top 3
            print(f"{idx}. From {chunk['document_name']} (Score: {chunk['similarity_score']:.2f})")
            print(f"   {chunk['text'][:300]}...")  # First 300 chars
            print()


if __name__ == "__main__":
    main()