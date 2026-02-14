"""
Test RAG Agent exactly as the workflow uses it
"""

from agents.rag_agent import RAGAgent

print("=" * 70)
print("TESTING RAG AGENT (as used in workflow)")
print("=" * 70)

# Step 1: Initialize agent (what workflow does at startup)
print("\nStep 1: Initializing RAG Agent...")
try:
    agent = RAGAgent()
    print("✅ RAG Agent initialized")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    exit(1)

# Step 2: Answer question (what workflow does during evaluation)
print("\nStep 2: Answering question...")
try:
    result = agent.answer_question(
        question="What export licenses are required?",
        top_k=3
    )
    print("✅ Question answered successfully!")
    print(f"   Retrieved chunks: {result.get('retrieved_chunks', 0)}")
    print(f"   Confidence: {result.get('confidence', 0):.0%}")
    
    if result.get('retrieved_chunks', 0) > 0:
        print("\n✅✅✅ RAG AGENT WORKS! ✅✅✅")
    else:
        print("\n❌ RAG Agent returned 0 chunks (same as workflow error)")
        
except Exception as e:
    print(f"❌ Failed to answer: {e}")
    import traceback
    traceback.print_exc()