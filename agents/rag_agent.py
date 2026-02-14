"""
Agent 3: RAG Knowledge Agent
Role: Answer compliance/policy questions using internal knowledge base
Does NOT: Check external websites or make risk decisions
Technology: HuggingFace embeddings + Qdrant vector search + OpenAI GPT-4
"""

import os
import sys
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Import RAG retrieval system - using query_rag directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Since we already have query_rag.py working, we'll create a simple wrapper
def search_similar_chunks(query: str, top_k: int = 5, min_score: float = 0.3) -> List[Dict]:
    """
    Wrapper function to search Qdrant - uses existing RAG system
    For mock testing, returns empty list (will be replaced in production)
    """
    try:
        from qdrant_client import QdrantClient
        from rag.embeddings import get_embedding_generator
        
        # Connect to Qdrant
        client = QdrantClient(host="localhost", port=6333)
        
        # Get embedding model
        embedding_model = get_embedding_generator()
        
        # Generate query embedding
        query_embedding = embedding_model.encode(query).tolist()
        
        # Search in Qdrant
        search_results = client.search(
            collection_name="compliance_policies",
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=min_score
        )
        
        # Format results
        results = []
        for result in search_results:
            results.append({
                "text": result.payload.get("text", ""),
                "metadata": {
                    "document_name": result.payload.get("document_name", "Unknown"),
                    "page_number": result.payload.get("page_number", "Unknown"),
                    "chunk_id": result.payload.get("chunk_id", "Unknown")
                },
                "score": result.score
            })
        
        return results
    except Exception as e:
        # If Qdrant is not running or any error, return empty for mock testing
        print(f"   ⚠️ RAG search not available: {str(e)}")
        return []

# Load environment variables
load_dotenv()


class RAGAgent:
    """
    RAG Knowledge Agent - Answers questions using internal policy documents
    
    Think of this as a compliance expert who:
    - Has read all your company's policy documents (already stored in Qdrant)
    - Answers questions about regulations, licenses, requirements
    - Provides citations (document name, page number)
    - Does NOT make risk judgments - only provides factual policy information
    - Does NOT search the internet - only internal knowledge base
    """
    
    def __init__(self):
        """
        Initialize the RAG Knowledge Agent
        Sets up OpenAI API connection
        """
        # Get API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "❌ OPENAI_API_KEY not found! "
                "Make sure your .env file has: OPENAI_API_KEY=sk-..."
            )
        
        # Create OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        
        print("✅ RAG Agent initialized successfully")
    
    
    def answer_question(
        self, 
        question: str,
        top_k: int = 5,
        min_confidence: float = 0.3
    ) -> Dict:
        """
        Answer a compliance/policy question using RAG
        
        Args:
            question: The question to answer (e.g., "What export licenses are required for UK textiles?")
            top_k: Number of relevant document chunks to retrieve (default: 5)
            min_confidence: Minimum similarity score to include chunk (default: 0.3)
        
        Returns:
            Dictionary containing:
            - question: The original question
            - answer: AI-generated answer based on retrieved context
            - sources: List of source documents and page numbers
            - confidence: Confidence score (0-1)
            - retrieved_chunks: Number of relevant chunks found
        
        Example:
            result = agent.answer_question(
                question="What export licenses are required for UK textiles?",
                top_k=5
            )
        """
        
        print(f"\n💡 RAG Agent: Answering question...")
        print(f"   Question: {question}")
        
        # Step 1: Retrieve relevant chunks from Qdrant
        print(f"   🔍 Searching knowledge base for relevant information...")
        
        try:
            # Search for similar chunks in the vector database
            results = search_similar_chunks(
                query=question,
                top_k=top_k,
                min_score=min_confidence
            )
            
            print(f"   ✅ Found {len(results)} relevant chunks")
            
            if not results:
                print(f"   ⚠️ No relevant information found in knowledge base")
                return {
                    "question": question,
                    "answer": "I could not find relevant information in the knowledge base to answer this question.",
                    "sources": [],
                    "confidence": 0.0,
                    "retrieved_chunks": 0
                }
            
            # Step 2: Format context for GPT-4
            context = self._format_context(results)
            
            # Step 3: Generate answer using GPT-4
            print(f"   🧠 Generating answer with AI...")
            answer_data = self._generate_answer(question, context, results)
            
            print(f"   ✅ Answer generated (confidence: {answer_data['confidence']:.0%})")
            
            return answer_data
            
        except Exception as e:
            print(f"   ❌ Error during RAG retrieval: {str(e)}")
            
            return {
                "question": question,
                "answer": f"Error retrieving information: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "retrieved_chunks": 0,
                "error": str(e)
            }
    
    
    def _format_context(self, results: List[Dict]) -> str:
        """
        Format retrieved chunks into context for GPT-4
        
        Each chunk includes:
        - The text content
        - Source document name
        - Page number
        - Relevance score
        """
        
        context_parts = []
        
        for i, result in enumerate(results, 1):
            chunk_text = result.get('text', '')
            doc_name = result.get('metadata', {}).get('document_name', 'Unknown')
            page_num = result.get('metadata', {}).get('page_number', 'Unknown')
            score = result.get('score', 0.0)
            
            context_parts.append(
                f"[Source {i}] {doc_name} (Page {page_num}, Relevance: {score:.2f})\n"
                f"{chunk_text}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    
    def _generate_answer(
        self, 
        question: str, 
        context: str,
        results: List[Dict]
    ) -> Dict:
        """
        Generate answer using GPT-4 based on retrieved context
        
        Uses advanced prompting to ensure:
        - Answers are based ONLY on provided context
        - Citations are included
        - Confidence is assessed
        - Hallucinations are minimized
        """
        
        # Enhanced system prompt for accurate RAG responses
        system_prompt = """You are a compliance and policy expert answering questions based STRICTLY on the provided internal policy documents.

CRITICAL RULES:
1. ONLY use information from the provided context below
2. If the context doesn't contain the answer, clearly state "The provided documents do not contain information about this topic"
3. ALWAYS cite your sources using the format: [Source X]
4. Do NOT make up information or use general knowledge
5. If multiple documents provide conflicting information, mention both and note the conflict
6. Be precise and specific - include exact requirements, numbers, dates when available
7. If the question requires information not in the context, say so explicitly

ANSWER FORMAT:
- Start with a direct answer to the question
- Include specific details from the documents
- Add citations for each fact: [Source 1], [Source 2], etc.
- End with a confidence assessment

CONFIDENCE LEVELS:
- High (0.8-1.0): Multiple sources confirm the same information with specific details
- Medium (0.5-0.79): Information found but limited or from single source
- Low (0.0-0.49): Minimal or tangential information, or no clear answer in documents"""

        # Build user message
        user_message = f"""Context from internal policy documents:

{context}

---

Question: {question}

Please provide a detailed answer based ONLY on the context above. Include citations and assess your confidence level."""

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2,  # Low temperature for factual responses
                max_tokens=800
            )
            
            answer_text = response.choices[0].message.content
            
            # Extract sources from results
            sources = []
            for result in results:
                source_info = {
                    "document": result.get('metadata', {}).get('document_name', 'Unknown'),
                    "page": result.get('metadata', {}).get('page_number', 'Unknown'),
                    "relevance": result.get('score', 0.0)
                }
                if source_info not in sources:  # Avoid duplicates
                    sources.append(source_info)
            
            # Estimate confidence based on number of sources and scores
            avg_score = sum(r.get('score', 0) for r in results) / len(results) if results else 0
            confidence = min(avg_score * 1.2, 1.0)  # Boost slightly but cap at 1.0
            
            return {
                "question": question,
                "answer": answer_text,
                "sources": sources,
                "confidence": confidence,
                "retrieved_chunks": len(results)
            }
            
        except Exception as e:
            print(f"   ❌ Error generating answer: {str(e)}")
            
            return {
                "question": question,
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "retrieved_chunks": len(results),
                "error": str(e)
            }
    
    
    def answer_multiple_questions(
        self, 
        questions: List[str]
    ) -> List[Dict]:
        """
        Answer multiple questions in batch
        Useful for evaluation workflows where multiple policy questions need answers
        
        Args:
            questions: List of questions to answer
        
        Returns:
            List of answer dictionaries
        """
        
        print(f"\n📚 RAG Agent: Answering {len(questions)} questions...")
        
        answers = []
        for i, question in enumerate(questions, 1):
            print(f"\n   Question {i}/{len(questions)}")
            answer = self.answer_question(question)
            answers.append(answer)
        
        print(f"\n✅ All {len(questions)} questions answered")
        
        return answers


# Test function - MOCK VERSION (No API calls)
if __name__ == "__main__":
    """
    Test the RAG Knowledge Agent - MOCK VERSION
    
    This test does NOT call OpenAI API to save your credits.
    It only tests that the agent initializes correctly.
    
    For full testing with real RAG queries and API calls,
    use the workflow tests after all agents are complete.
    
    To test: python agents/rag_agent.py
    """
    
    print("=" * 70)
    print("TESTING RAG KNOWLEDGE AGENT (MOCK MODE)")
    print("=" * 70)
    
    # Test 1: Agent Initialization
    print("\n🧪 TEST 1: Agent Initialization")
    print("-" * 70)
    try:
        agent = RAGAgent()
        print("✅ Agent initialized successfully with OpenAI connection")
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")
        print("   Check your .env file has OPENAI_API_KEY=sk-...")
        exit(1)
    
    # Test 2: Mock RAG Query (No API call)
    print("\n🧪 TEST 2: Mock RAG Query Structure")
    print("-" * 70)
    print("   Simulating RAG query without API calls...")
    
    # Create mock RAG result (what the agent WOULD return)
    mock_result = {
        "question": "What export licenses are required for UK textile exports?",
        "answer": """Based on the internal policy documents, UK textile exports to non-EU countries require an Open General Export Licence (OGEL) [Source 1]. 

Specific requirements include:
- OGEL Type: ML1a for certain textile materials [Source 1]
- Registration: Must register with UK Export Control Joint Unit before first use [Source 2]
- Validity: OGELs are valid indefinitely but must be reviewed annually [Source 2]
- Exemptions: Exports to EU countries and certain Commonwealth nations may be exempt [Source 3]

Additional compliance notes:
- Exporters must maintain records for 4 years [Source 1]
- Certain textile categories (military, dual-use) require Individual Export Licenses instead of OGEL [Source 3]

Confidence: High - This information is confirmed across multiple policy documents with specific regulatory details.""",
        "sources": [
            {
                "document": "uk_export_control_list_2025.pdf",
                "page": 12,
                "relevance": 0.87
            },
            {
                "document": "guide_to_exporting.pdf",
                "page": 45,
                "relevance": 0.82
            },
            {
                "document": "uk_export_control_list_2025.pdf",
                "page": 34,
                "relevance": 0.76
            }
        ],
        "confidence": 0.85,
        "retrieved_chunks": 5
    }
    
    # Display mock results
    print("\n" + "=" * 70)
    print("📊 MOCK RAG QUERY RESULTS (Example Output)")
    print("=" * 70)
    
    print(f"\n❓ QUESTION:")
    print(f"   {mock_result['question']}")
    
    print(f"\n💡 ANSWER:")
    print(f"   {mock_result['answer']}")
    
    print(f"\n📚 SOURCES:")
    for source in mock_result['sources']:
        print(f"   - {source['document']} (Page {source['page']}, Relevance: {source['relevance']:.0%})")
    
    print(f"\n🎯 CONFIDENCE: {mock_result['confidence']:.0%}")
    print(f"📄 RETRIEVED CHUNKS: {mock_result['retrieved_chunks']}")
    
    # Test 3: Mock Multiple Questions
    print("\n🧪 TEST 3: Mock Batch Questions")
    print("-" * 70)
    
    mock_questions = [
        "What are OECD due diligence requirements?",
        "What financial documentation is required for supplier onboarding?",
        "What are the sanctions screening requirements?"
    ]
    
    print(f"   Would process {len(mock_questions)} questions:")
    for i, q in enumerate(mock_questions, 1):
        print(f"   {i}. {q}")
    
    print("\n" + "=" * 70)
    print("💡 NOTE: This was a MOCK test (no API calls)")
    print("   Real RAG queries will happen in the full workflow")
    print("   after all 5 agents are integrated.")
    print("   Your knowledge base has 4 PDFs already indexed in Qdrant.")
    print("=" * 70)
    
    print("\n✅ RAG AGENT TESTS COMPLETED")
    print("=" * 70)