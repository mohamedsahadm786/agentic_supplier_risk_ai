"""
Agent 2: Document Intelligence Agent
Role: Extract structured facts from supplier-submitted documents (PDFs)
Does NOT: Make risk judgments - only extracts and flags data
Technology: PyPDF2/pdfplumber + OpenAI GPT-4
"""

import os
import json
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Import MCP-1 Document Tools
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tools.document_tools import read_pdf, extract_tables

# Load environment variables
load_dotenv()


class DocumentAgent:
    """
    Document Intelligence Agent - Extracts structured data from PDFs
    
    Think of this as a data extraction specialist who:
    - Reads supplier documents (invoices, certificates, registration docs)
    - Extracts key information (company name, addresses, tax IDs, etc.)
    - Identifies missing information
    - Flags inconsistencies across documents
    - Does NOT make decisions - just reports facts
    """
    
    def __init__(self):
        """
        Initialize the Document Intelligence Agent
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
        self.model = "gpt-4o-mini"  # Using GPT-4o-mini for cost efficiency
        
        print("✅ Document Agent initialized successfully")
    
    
    def analyze_documents(
        self, 
        document_paths: List[str],
        supplier_name: str = None
    ) -> Dict:
        """
        Analyze multiple supplier documents and extract structured data
        
        Args:
            document_paths: List of PDF file paths to analyze
            supplier_name: Expected supplier name (for validation)
        
        Returns:
            Dictionary containing:
            - extracted_data: Structured information found
            - missing_data: List of missing critical fields
            - inconsistencies: List of data conflicts across documents
            - document_summaries: Summary of each document
            - confidence_score: Overall confidence in extracted data (0-1)
        
        Example:
            result = agent.analyze_documents(
                document_paths=["invoice.pdf", "certificate.pdf"],
                supplier_name="TechTextiles Ltd"
            )
        """
        
        print(f"\n📄 Document Agent: Analyzing {len(document_paths)} documents...")
        
        # Step 1: Extract text from all documents
        documents_content = []
        for i, doc_path in enumerate(document_paths, 1):
            print(f"   Reading document {i}/{len(document_paths)}: {os.path.basename(doc_path)}")
            
            try:
                # Read PDF using MCP-1 Document Tools
                text = read_pdf(doc_path)
                
                # Also try to extract tables if present
                tables = extract_tables(doc_path)
                
                documents_content.append({
                    "filename": os.path.basename(doc_path),
                    "text": text[:10000],  # Limit to 10K chars per doc (API limits)
                    "has_tables": len(tables) > 0,
                    "table_count": len(tables)
                })
                
            except Exception as e:
                print(f"   ⚠️ Error reading {doc_path}: {str(e)}")
                documents_content.append({
                    "filename": os.path.basename(doc_path),
                    "text": "",
                    "error": str(e)
                })
        
        # Step 2: Use GPT-4 to extract structured data
        print(f"\n🧠 Analyzing content with AI...")
        
        try:
            analysis = self._extract_structured_data(documents_content, supplier_name)
            
            print(f"✅ Analysis complete!")
            print(f"   - Extracted {len(analysis.get('extracted_data', {}))} data fields")
            print(f"   - Found {len(analysis.get('missing_data', []))} missing fields")
            print(f"   - Detected {len(analysis.get('inconsistencies', []))} inconsistencies")
            print(f"   - Confidence: {analysis.get('confidence_score', 0):.0%}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            
            # Return minimal structure on error
            return {
                "extracted_data": {},
                "missing_data": ["Analysis failed - check documents"],
                "inconsistencies": [],
                "document_summaries": [],
                "confidence_score": 0.0,
                "error": str(e)
            }
    
    
    def _extract_structured_data(
        self, 
        documents_content: List[Dict],
        supplier_name: str = None
    ) -> Dict:
        """
        Internal method: Use GPT-4 to extract structured data from document text
        
        This is where the AI magic happens - GPT-4 reads the text and extracts:
        - Company information
        - Registration details
        - Financial data
        - Contact information
        - Dates and validity periods
        """
        
        # Create enhanced system prompt for better extraction
        system_prompt = """You are an expert document analysis AI specializing in supplier verification and data extraction.

Your task is to extract structured information from supplier documents (invoices, certificates, registration documents, financial statements, etc.).

CRITICAL EXTRACTION RULES:
1. Extract ALL company identifiers: legal name, trading names, registration numbers, tax IDs, VAT numbers
2. Extract ALL addresses: registered address, trading address, billing address (note if they differ)
3. Extract financial data: revenue, profit, assets, liabilities (if present)
4. Extract dates: incorporation date, document issue dates, validity periods
5. Extract contact information: phone numbers, email addresses, websites
6. Extract certifications: ISO certifications, industry-specific licenses, export licenses
7. Extract ownership information: directors, shareholders, beneficial owners (if present)

INCONSISTENCY DETECTION:
- Flag if company name appears differently across documents
- Flag if addresses don't match across documents
- Flag if registration numbers are inconsistent
- Flag if dates seem illogical (e.g., document dated before company incorporation)

MISSING DATA DETECTION:
Identify if these critical fields are missing:
- Company registration number
- Registered address
- Tax identification number
- Valid contact information
- Recent financial statements (within last 2 years)
- Required certifications for the industry

CONFIDENCE SCORING:
- High confidence (0.8-1.0): Clear, consistent data across multiple documents
- Medium confidence (0.5-0.79): Some missing fields or minor inconsistencies
- Low confidence (0.0-0.49): Multiple missing fields or significant inconsistencies

Return your analysis as a JSON object with this EXACT structure:
{
    "extracted_data": {
        "company_name": "string",
        "registration_number": "string",
        "tax_id": "string or null",
        "vat_number": "string or null",
        "registered_address": "string",
        "trading_address": "string or null",
        "incorporation_date": "YYYY-MM-DD or null",
        "contact_email": "string or null",
        "contact_phone": "string or null",
        "website": "string or null",
        "directors": ["list of names"] or [],
        "certifications": ["list of certifications"] or [],
        "financial_data": {
            "currency": "string or null",
            "annual_revenue": "number or null",
            "latest_financial_year": "YYYY or null"
        }
    },
    "missing_data": [
        "List of critical fields that are missing",
        "Example: VAT registration certificate not found",
        "Example: No financial statements provided"
    ],
    "inconsistencies": [
        "List of data conflicts across documents",
        "Example: Company name on invoice (ABC Ltd) differs from registration (ABC Limited)",
        "Example: Registered address on certificate differs from invoice address"
    ],
    "document_summaries": [
        {
            "filename": "document name",
            "document_type": "invoice/certificate/registration/financial_statement/other",
            "key_findings": "brief summary of what this document contains"
        }
    ],
    "confidence_score": 0.85
}

Be thorough, precise, and flag ALL potential issues. Your analysis will be used for high-stakes supplier risk assessment."""

        # Build user message with all document content
        user_message = "Analyze the following supplier documents and extract structured information:\n\n"
        
        if supplier_name:
            user_message += f"Expected Supplier Name: {supplier_name}\n\n"
        
        for i, doc in enumerate(documents_content, 1):
            user_message += f"--- DOCUMENT {i}: {doc['filename']} ---\n"
            
            if doc.get('error'):
                user_message += f"Error reading document: {doc['error']}\n\n"
            else:
                user_message += f"Has tables: {doc.get('has_tables', False)}\n"
                user_message += f"Text content:\n{doc['text']}\n\n"
        
        user_message += "\nProvide complete structured analysis following the JSON format specified."
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # Lower temperature for factual extraction
            response_format={"type": "json_object"}
        )
        
        # Parse JSON response
        analysis = json.loads(response.choices[0].message.content)
        
        return analysis


# Test function
# Test function - MOCK VERSION (No API calls to save costs)
if __name__ == "__main__":
    """
    Test the Document Intelligence Agent - MOCK VERSION
    
    This test does NOT call OpenAI API to save your credits.
    It only tests that the agent initializes correctly.
    
    For full testing with real documents and API calls,
    use the workflow tests after all agents are complete.
    
    To test: python agents/document_agent.py
    """
    
    print("=" * 70)
    print("TESTING DOCUMENT INTELLIGENCE AGENT (MOCK MODE)")
    print("=" * 70)
    
    # Test 1: Agent Initialization
    print("\n🧪 TEST 1: Agent Initialization")
    print("-" * 70)
    try:
        agent = DocumentAgent()
        print("✅ Agent initialized successfully with OpenAI connection")
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")
        print("   Check your .env file has OPENAI_API_KEY=sk-...")
        exit(1)
    
    # Test 2: Mock Document Analysis (No API call)
    print("\n🧪 TEST 2: Mock Document Analysis Structure")
    print("-" * 70)
    print("   Simulating document analysis without API calls...")
    
    # Create mock analysis result (what the agent WOULD return)
    mock_result = {
        "extracted_data": {
            "company_name": "TechTextiles Ltd",
            "registration_number": "12345678",
            "tax_id": "GB123456789",
            "vat_number": "GB987654321",
            "registered_address": "123 High Street, London, UK",
            "trading_address": "123 High Street, London, UK",
            "incorporation_date": "2010-03-15",
            "contact_email": "info@techtextiles.co.uk",
            "contact_phone": "+44 20 1234 5678",
            "website": "www.techtextiles.co.uk",
            "directors": ["John Smith", "Jane Doe"],
            "certifications": ["ISO 9001:2015", "OEKO-TEX Standard 100"],
            "financial_data": {
                "currency": "GBP",
                "annual_revenue": 5000000,
                "latest_financial_year": "2024"
            }
        },
        "missing_data": [
            "Export license documentation not found",
            "Audited financial statements not provided"
        ],
        "inconsistencies": [
            "Company name on invoice (TechTextiles Limited) differs slightly from registration (TechTextiles Ltd)"
        ],
        "document_summaries": [
            {
                "filename": "company_registration.pdf",
                "document_type": "registration",
                "key_findings": "Active UK company registered in 2010"
            },
            {
                "filename": "invoice_2024.pdf",
                "document_type": "invoice",
                "key_findings": "Recent invoice showing business activity"
            }
        ],
        "confidence_score": 0.75
    }
    
    # Display mock results
    print("\n" + "=" * 70)
    print("📊 MOCK ANALYSIS RESULTS (Example Output)")
    print("=" * 70)
    
    print("\n✅ EXTRACTED DATA:")
    for key, value in mock_result['extracted_data'].items():
        if value and value != [] and value != {}:
            print(f"   {key}: {value}")
    
    print("\n⚠️ MISSING DATA:")
    for item in mock_result['missing_data']:
        print(f"   - {item}")
    
    print("\n🚩 INCONSISTENCIES:")
    for item in mock_result['inconsistencies']:
        print(f"   - {item}")
    
    print("\n📄 DOCUMENT SUMMARIES:")
    for doc in mock_result['document_summaries']:
        print(f"   {doc['filename']}: {doc['document_type']}")
        print(f"      → {doc['key_findings']}")
    
    print(f"\n🎯 CONFIDENCE SCORE: {mock_result['confidence_score']:.0%}")
    
    print("\n" + "=" * 70)
    print("💡 NOTE: This was a MOCK test (no API calls)")
    print("   Real document analysis will happen in the full workflow")
    print("   after all 5 agents are integrated.")
    print("=" * 70)
    
    print("\n✅ DOCUMENT AGENT TESTS COMPLETED")
    print("=" * 70)