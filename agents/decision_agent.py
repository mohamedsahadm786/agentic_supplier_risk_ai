"""
Agent 5: Decision & Report Agent
Role: Synthesize all data and produce final risk assessment
Does NOT: Use fine-tuning - uses instruction-tuned prompts only
Technology: OpenAI GPT-4 with carefully crafted prompts
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DecisionAgent:
    """
    Decision & Report Agent - Final risk assessment and recommendations
    
    Think of this as a senior risk analyst who:
    - Reviews ALL information from other agents
    - Synthesizes findings into a coherent risk assessment
    - Assigns a final risk level (Low/Medium/High)
    - Provides specific, actionable recommendations
    - Creates detailed reasoning with evidence
    - Generates audit-ready reports
    """
    
    def __init__(self):
        """
        Initialize the Decision Agent
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
        
        print("✅ Decision Agent initialized successfully")
    
    
    def make_decision(
        self,
        supplier_name: str,
        evaluation_plan: Dict,
        document_analysis: Dict,
        rag_answers: Dict,
        external_intelligence: Dict,
        business_context: Optional[str] = None
    ) -> Dict:
        """
        Make final risk decision based on all agent outputs
        
        Args:
            supplier_name: Name of the supplier being evaluated
            evaluation_plan: Output from Planner Agent
            document_analysis: Output from Document Agent
            rag_answers: Output from RAG Agent
            external_intelligence: Output from External Agent
            business_context: Optional additional context
        
        Returns:
            Dictionary containing:
            - risk_level: "Low", "Medium", or "High"
            - confidence_score: 0.0-1.0
            - reasoning: Detailed explanation of decision
            - positive_factors: List of favorable findings
            - negative_factors: List of risk concerns
            - recommended_actions: Specific next steps
            - decision_summary: Executive summary
            - evidence_trail: Links to supporting evidence
        
        Example:
            decision = agent.make_decision(
                supplier_name="TechTextiles Ltd",
                evaluation_plan=planner_output,
                document_analysis=doc_output,
                rag_answers=rag_output,
                external_intelligence=external_output
            )
        """
        
        print(f"\n⚖️ Decision Agent: Making final risk assessment for {supplier_name}...")
        
        try:
            # Generate decision using GPT-4
            decision = self._generate_decision(
                supplier_name=supplier_name,
                evaluation_plan=evaluation_plan,
                document_analysis=document_analysis,
                rag_answers=rag_answers,
                external_intelligence=external_intelligence,
                business_context=business_context
            )
            
            print(f"\n✅ Decision complete!")
            print(f"   Risk Level: {decision.get('risk_level', 'Unknown')}")
            print(f"   Confidence: {decision.get('confidence_score', 0):.0%}")
            print(f"   Positive factors: {len(decision.get('positive_factors', []))}")
            print(f"   Negative factors: {len(decision.get('negative_factors', []))}")
            print(f"   Recommendations: {len(decision.get('recommended_actions', []))}")
            
            return decision
            
        except Exception as e:
            print(f"❌ Error making decision: {str(e)}")
            
            # Return minimal decision on error
            return {
                "risk_level": "High",
                "confidence_score": 0.0,
                "reasoning": f"Unable to complete risk assessment due to error: {str(e)}",
                "positive_factors": [],
                "negative_factors": ["Assessment incomplete due to technical error"],
                "recommended_actions": ["Re-evaluate supplier with complete data"],
                "decision_summary": "Risk assessment failed - manual review required",
                "evidence_trail": {},
                "error": str(e)
            }
    
    
    def _generate_decision(
        self,
        supplier_name: str,
        evaluation_plan: Dict,
        document_analysis: Dict,
        rag_answers: Dict,
        external_intelligence: Dict,
        business_context: Optional[str]
    ) -> Dict:
        """
        Internal method: Use GPT-4 to generate final risk decision
        
        This uses advanced prompt engineering to ensure:
        - Evidence-based decisions
        - Balanced assessment (not biased toward rejection)
        - Specific, actionable recommendations
        - Audit-ready reasoning
        """
        
        # Comprehensive system prompt for high-quality risk decisions
        system_prompt = """You are a senior supplier risk analyst with 15+ years of experience in international trade compliance, fraud detection, and supplier due diligence.

Your role is to make FINAL RISK DECISIONS about supplier onboarding based on comprehensive evidence from multiple sources.

CRITICAL DECISION FRAMEWORK:

1. RISK LEVELS (choose ONE):
   - LOW: Minimal risk, recommend approval with standard monitoring
   - MEDIUM: Some concerns but manageable, recommend approval with enhanced due diligence
   - HIGH: Significant risks, recommend rejection or escalation to senior management

2. EVIDENCE-BASED REASONING:
   - Every decision MUST be supported by specific evidence
   - Cite which agent/source provided each piece of evidence
   - Balance positive and negative findings fairly
   - Do NOT make assumptions beyond provided data
   - If data is missing, state what's missing and how it affects the decision

3. CONFIDENCE SCORING (0.0-1.0):
   - High confidence (0.8-1.0): Complete data, clear patterns, multiple confirming sources
   - Medium confidence (0.5-0.79): Some missing data, mixed signals, single-source confirmations
   - Low confidence (0.0-0.49): Significant data gaps, conflicting information, or error conditions

4. POSITIVE vs NEGATIVE FACTORS:
   - List ALL favorable findings (even if final decision is negative)
   - List ALL risk concerns (even if final decision is positive)
   - Be balanced and objective - not overly cautious or overly permissive

5. RECOMMENDED ACTIONS:
   - Provide SPECIFIC, ACTIONABLE next steps
   - Prioritize recommendations by importance
   - Include both immediate actions and ongoing monitoring requirements
   - If approving with conditions, state conditions clearly

6. CRITICAL RED FLAGS (automatically → HIGH risk):
   - Sanctions list matches (company or owners)
   - Evidence of fraud or criminal activity
   - Company inactive/dissolved
   - Consistent negative news coverage indicating serious legal/ethical issues
   - Significant document forgery indicators
   - Multiple major compliance violations

7. DECISION BIAS AWARENESS:
   - Do NOT default to "High risk" just to be safe
   - Low/Medium risk decisions are valid when evidence supports them
   - Missing documentation ≠ automatic rejection (depends on criticality)
   - Negative news ≠ automatic rejection (depends on severity and recency)

OUTPUT FORMAT - Return ONLY valid JSON:
{
    "risk_level": "Low|Medium|High",
    "confidence_score": 0.85,
    "reasoning": "Comprehensive explanation of decision with specific evidence citations. Example: 'Based on Document Agent findings, the company registration is active (Companies House, verified [date]). External Agent found 3 positive news articles with no negative coverage. However, Document Agent flagged missing VAT certificate, which raises compliance concerns but is not critical for this supplier type.'",
    "positive_factors": [
        "Active company registration verified via UK Companies House",
        "No sanctions matches found (EU, OFAC, UN lists checked)",
        "Positive news coverage (3 articles, mostly positive sentiment)",
        "Financial statements show stable revenue growth"
    ],
    "negative_factors": [
        "Missing VAT registration certificate",
        "Address inconsistency between invoice and registration documents",
        "Limited news coverage (only 3 articles found)"
    ],
    "recommended_actions": [
        "Request VAT registration certificate within 5 business days",
        "Clarify registered address discrepancy with supplier",
        "Approve for trial order (max $10,000) pending document verification",
        "Schedule 90-day review to reassess based on initial transaction performance"
    ],
    "decision_summary": "Medium risk supplier suitable for conditional approval. Active, registered company with positive reputation but minor compliance documentation gaps. Recommend approval with enhanced monitoring and document verification requirements.",
    "evidence_trail": {
        "document_agent": "Extracted company data, flagged missing VAT cert and address inconsistency",
        "rag_agent": "Confirmed VAT requirements for UK exporters",
        "external_agent": "Verified active company status, found positive news, no sanctions matches",
        "planner_agent": "Identified 8 evaluation tasks, all completed"
    }
}

IMPORTANT: Your decision will be used for high-stakes business decisions. Be thorough, balanced, and evidence-based."""

        # Build comprehensive user message with all agent outputs
        user_message = f"""Supplier Risk Assessment Request

SUPPLIER INFORMATION:
Name: {supplier_name}
"""
        
        if business_context:
            user_message += f"Business Context: {business_context}\n"
        
        user_message += f"""
---

EVALUATION PLAN (Planner Agent):
Tasks Identified: {json.dumps(evaluation_plan.get('tasks', []), indent=2)}
Planning Reasoning: {evaluation_plan.get('reasoning', 'N/A')}

---

DOCUMENT ANALYSIS (Document Agent):
Extracted Data: {json.dumps(document_analysis.get('extracted_data', {}), indent=2)}
Missing Data: {json.dumps(document_analysis.get('missing_data', []), indent=2)}
Inconsistencies: {json.dumps(document_analysis.get('inconsistencies', []), indent=2)}
Confidence: {document_analysis.get('confidence_score', 0):.0%}

---

POLICY/COMPLIANCE KNOWLEDGE (RAG Agent):
{json.dumps(rag_answers, indent=2)}

---

EXTERNAL INTELLIGENCE (External Agent):
Company Registry: {json.dumps(external_intelligence.get('company_registry', {}), indent=2)}
News Analysis: {json.dumps(external_intelligence.get('news_analysis', {}), indent=2)}
Sanctions Check: {json.dumps(external_intelligence.get('sanctions_check', {}), indent=2)}
Risk Signals: {json.dumps(external_intelligence.get('risk_signals', []), indent=2)}
Data Sources: {', '.join(external_intelligence.get('data_sources', []))}

---

Based on ALL the evidence above, provide your final risk assessment decision in the specified JSON format.
"""

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # Lower temperature for consistent, logical decisions
            response_format={"type": "json_object"}
        )
        
        # Parse JSON response
        decision = json.loads(response.choices[0].message.content)
        
        # Add metadata
        decision["evaluated_at"] = datetime.now().isoformat()
        decision["supplier_name"] = supplier_name
        
        return decision


# Test function - MOCK VERSION (No API calls)
if __name__ == "__main__":
    """
    Test the Decision Agent - MOCK VERSION
    
    This test does NOT call OpenAI API to save your credits.
    It only tests that the agent initializes correctly.
    
    For full testing with real decision-making,
    use the workflow tests after all agents are complete.
    
    To test: python agents/decision_agent.py
    """
    
    print("=" * 70)
    print("TESTING DECISION & REPORT AGENT (MOCK MODE)")
    print("=" * 70)
    
    # Test 1: Agent Initialization
    print("\n🧪 TEST 1: Agent Initialization")
    print("-" * 70)
    try:
        agent = DecisionAgent()
        print("✅ Agent initialized successfully with OpenAI connection")
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")
        print("   Check your .env file has OPENAI_API_KEY=sk-...")
        exit(1)
    
    # Test 2: Mock Decision Making
    print("\n🧪 TEST 2: Mock Risk Decision Structure")
    print("-" * 70)
    print("   Simulating final risk assessment...")
    
    # Create mock decision result
    mock_decision = {
        "risk_level": "Medium",
        "confidence_score": 0.78,
        "reasoning": """Based on comprehensive analysis across all agents:

POSITIVE INDICATORS:
- Document Agent verified active company registration (UK Companies House #12345678, incorporated 2010)
- External Agent found no sanctions matches (checked EU, OFAC, UN lists - 276 entities, 6,403 individuals)
- External Agent identified 3 positive news articles with no negative coverage
- RAG Agent confirmed compliance requirements are standard for UK textile exporters
- Company shows 14+ years of operational history

CONCERNS:
- Document Agent flagged missing VAT registration certificate
- Minor address inconsistency between invoice (123 High St) and registration (123 High Street) - likely formatting difference but requires clarification
- Limited news coverage suggests smaller operation with lower public profile
- No audited financial statements provided (only management accounts)

ASSESSMENT:
This is a legitimate, established business with no critical red flags. The missing VAT certificate is a compliance gap but not uncommon for smaller exporters and can be resolved. The address inconsistency appears minor but should be verified. Overall risk is MEDIUM - suitable for approval with conditions and enhanced monitoring.""",
        "positive_factors": [
            "Active company registration verified (14+ years operational history)",
            "No sanctions matches found across all major lists",
            "Positive news sentiment (3 articles, all favorable)",
            "No legal disputes or litigation found",
            "Directors have no adverse history",
            "Industry certifications present (ISO 9001:2015, OEKO-TEX)"
        ],
        "negative_factors": [
            "Missing VAT registration certificate",
            "Address formatting inconsistency requires clarification",
            "No audited financial statements (only management accounts)",
            "Limited public information/news coverage",
            "Single bank reference provided (policy requires 2)"
        ],
        "recommended_actions": [
            "REQUEST IMMEDIATELY: VAT registration certificate (within 5 business days)",
            "VERIFY: Registered address discrepancy with supplier contact",
            "REQUEST: Second bank reference or trade reference",
            "APPROVE: Conditional approval for trial order up to $10,000 USD",
            "MONITOR: Schedule 90-day review after first transaction",
            "REQUIRE: Monthly financial statements for first 6 months",
            "ESCALATE: Any order above $10,000 requires senior management approval until track record established"
        ],
        "decision_summary": "Medium-risk supplier suitable for CONDITIONAL APPROVAL. Established UK company (14+ years) with clean sanctions record and positive reputation. Minor compliance gaps (missing VAT cert, address inconsistency) are resolvable and not critical. Recommend approval with $10,000 trial limit, enhanced monitoring, and document verification requirements. Escalate larger orders until track record proven.",
        "evidence_trail": {
            "planner_agent": "Created 8-point evaluation plan covering registration, documents, compliance, news, and sanctions",
            "document_agent": "Extracted structured data from 2 documents, identified 2 missing items and 1 inconsistency, confidence 75%",
            "rag_agent": "Confirmed UK export requirements (OGEL licenses, VAT registration), provided policy citations",
            "external_agent": "Verified active status via Companies House, checked 6 data sources (news, sanctions, watchlists), found 0 critical risks"
        },
        "evaluated_at": "2025-02-14T10:30:00",
        "supplier_name": "TechTextiles Ltd"
    }
    
    # Display mock results
    print("\n" + "=" * 70)
    print("📊 MOCK FINAL RISK DECISION")
    print("=" * 70)
    
    print(f"\n🏢 SUPPLIER: {mock_decision['supplier_name']}")
    print(f"📅 EVALUATED: {mock_decision['evaluated_at']}")
    
    print(f"\n⚖️ RISK LEVEL: {mock_decision['risk_level'].upper()}")
    print(f"🎯 CONFIDENCE: {mock_decision['confidence_score']:.0%}")
    
    print(f"\n📋 DECISION SUMMARY:")
    print(f"   {mock_decision['decision_summary']}")
    
    print(f"\n✅ POSITIVE FACTORS ({len(mock_decision['positive_factors'])}):")
    for factor in mock_decision['positive_factors']:
        print(f"   + {factor}")
    
    print(f"\n⚠️ NEGATIVE FACTORS ({len(mock_decision['negative_factors'])}):")
    for factor in mock_decision['negative_factors']:
        print(f"   - {factor}")
    
    print(f"\n🎯 RECOMMENDED ACTIONS ({len(mock_decision['recommended_actions'])}):")
    for i, action in enumerate(mock_decision['recommended_actions'], 1):
        print(f"   {i}. {action}")
    
    print(f"\n📚 EVIDENCE TRAIL:")
    for agent, evidence in mock_decision['evidence_trail'].items():
        print(f"   {agent}: {evidence}")
    
    print(f"\n💡 DETAILED REASONING:")
    print(f"   {mock_decision['reasoning']}")
    
    print("\n" + "=" * 70)
    print("💡 NOTE: This was a MOCK test (no API calls)")
    print("   Real risk decisions will be made in the full workflow")
    print("   combining outputs from all 5 agents:")
    print("   1. Planner Agent → Evaluation strategy")
    print("   2. Document Agent → PDF data extraction")
    print("   3. RAG Agent → Policy/compliance answers")
    print("   4. External Agent → News, registry, sanctions")
    print("   5. Decision Agent → Final risk assessment")
    print("=" * 70)
    
    print("\n✅ DECISION AGENT TESTS COMPLETED")
    print("=" * 70)
    print("\n🎉 ALL 5 AGENTS CREATED SUCCESSFULLY!")
    print("   Next step: Create LangGraph workflow to orchestrate all agents")
    print("=" * 70)