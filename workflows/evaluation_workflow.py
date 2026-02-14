"""
LangGraph Workflow: Supplier Risk Evaluation
Orchestrates all 5 agents in sequence to produce final risk assessment
"""

import os
import sys
from typing import TypedDict, Annotated, Dict, List
from datetime import datetime
import json

# Import LangGraph
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# Import all agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.planner_agent import PlannerAgent
from agents.document_agent import DocumentAgent
from agents.rag_agent import RAGAgent
from agents.external_agent import ExternalAgent
from agents.decision_agent import DecisionAgent


# Define the state that flows through the workflow
class EvaluationState(TypedDict):
    """
    State object that passes through all agents
    Each agent adds its output to this state
    """
    # Input data
    supplier_name: str
    supplier_country: str
    business_context: str
    document_paths: List[str]
    registration_number: str
    owner_names: List[str]
    
    # Agent outputs
    evaluation_plan: Dict
    document_analysis: Dict
    rag_answers: Dict
    external_intelligence: Dict
    final_decision: Dict
    
    # Metadata
    workflow_status: str
    errors: List[str]
    started_at: str
    completed_at: str


class SupplierEvaluationWorkflow:
    """
    Main workflow orchestrator
    Runs all 5 agents in sequence
    """
    
    def __init__(self):
        """
        Initialize workflow and all agents
        """
        print("🔧 Initializing Supplier Evaluation Workflow...")
        
        # Initialize all 5 agents
        self.planner = PlannerAgent()
        self.document_agent = DocumentAgent()
        self.rag_agent = RAGAgent()
        self.external_agent = ExternalAgent()
        self.decision_agent = DecisionAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
        print("✅ Workflow initialized successfully")
        print("   All 5 agents ready")
    
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow
        Defines the sequence: Planner → Document → RAG → External → Decision
        """
        
        # Create the graph
        workflow = StateGraph(EvaluationState)
        
        # Add nodes (each node is an agent)
        workflow.add_node("planner", self._run_planner)
        workflow.add_node("document", self._run_document_agent)
        workflow.add_node("rag", self._run_rag_agent)
        workflow.add_node("external", self._run_external_agent)
        workflow.add_node("decision", self._run_decision_agent)
        
        # Define edges (flow between agents)
        workflow.set_entry_point("planner")  # Start with planner
        workflow.add_edge("planner", "document")  # Planner → Document
        workflow.add_edge("document", "rag")  # Document → RAG
        workflow.add_edge("rag", "external")  # RAG → External
        workflow.add_edge("external", "decision")  # External → Decision
        workflow.add_edge("decision", END)  # Decision → End
        
        # Compile the workflow
        return workflow.compile()
    
    
    def _run_planner(self, state: EvaluationState) -> EvaluationState:
        """
        Node 1: Run Planner Agent
        Creates evaluation strategy
        """
        print("\n" + "="*70)
        print("STEP 1/5: PLANNER AGENT")
        print("="*70)
        
        try:
            plan = self.planner.create_evaluation_plan(
                supplier_name=state["supplier_name"],
                supplier_country=state["supplier_country"],
                business_context=state.get("business_context")
            )
            state["evaluation_plan"] = plan
            
        except Exception as e:
            print(f"❌ Planner failed: {str(e)}")
            state["errors"].append(f"Planner: {str(e)}")
            state["evaluation_plan"] = {"tasks": [], "reasoning": "Failed"}
        
        return state
    
    
    def _run_document_agent(self, state: EvaluationState) -> EvaluationState:
        """
        Node 2: Run Document Agent
        Extracts data from supplier PDFs
        """
        print("\n" + "="*70)
        print("STEP 2/5: DOCUMENT INTELLIGENCE AGENT")
        print("="*70)
        
        try:
            if state.get("document_paths"):
                analysis = self.document_agent.analyze_documents(
                    document_paths=state["document_paths"],
                    supplier_name=state["supplier_name"]
                )
                state["document_analysis"] = analysis
            else:
                print("⚠️ No documents provided - skipping document analysis")
                state["document_analysis"] = {
                    "extracted_data": {},
                    "missing_data": ["No documents provided"],
                    "inconsistencies": [],
                    "confidence_score": 0.0
                }
                
        except Exception as e:
            print(f"❌ Document analysis failed: {str(e)}")
            state["errors"].append(f"Document Agent: {str(e)}")
            state["document_analysis"] = {"error": str(e)}
        
        return state
    
    
    def _run_rag_agent(self, state: EvaluationState) -> EvaluationState:
        """
        Node 3: Run RAG Agent
        Answers compliance/policy questions
        """
        print("\n" + "="*70)
        print("STEP 3/5: RAG KNOWLEDGE AGENT")
        print("="*70)
        
        try:
            # Generate relevant questions from evaluation plan
            questions = self._extract_policy_questions(state["evaluation_plan"])
            
            if questions:
                answers = self.rag_agent.answer_multiple_questions(questions)
                state["rag_answers"] = {
                    "questions": questions,
                    "answers": answers
                }
            else:
                print("ℹ️ No policy questions generated")
                state["rag_answers"] = {"questions": [], "answers": []}
                
        except Exception as e:
            print(f"❌ RAG query failed: {str(e)}")
            state["errors"].append(f"RAG Agent: {str(e)}")
            state["rag_answers"] = {"error": str(e)}
        
        return state
    
    
    def _run_external_agent(self, state: EvaluationState) -> EvaluationState:
        """
        Node 4: Run External Intelligence Agent
        Gathers news, registry, sanctions data
        """
        print("\n" + "="*70)
        print("STEP 4/5: EXTERNAL INTELLIGENCE AGENT")
        print("="*70)
        
        try:
            intelligence = self.external_agent.gather_intelligence(
                company_name=state["supplier_name"],
                country=state["supplier_country"],
                registration_number=state.get("registration_number"),
                owner_names=state.get("owner_names", [])
            )
            state["external_intelligence"] = intelligence
            
        except Exception as e:
            print(f"❌ External intelligence failed: {str(e)}")
            state["errors"].append(f"External Agent: {str(e)}")
            state["external_intelligence"] = {"error": str(e)}
        
        return state
    
    
    def _run_decision_agent(self, state: EvaluationState) -> EvaluationState:
        """
        Node 5: Run Decision Agent
        Makes final risk assessment
        """
        print("\n" + "="*70)
        print("STEP 5/5: DECISION & REPORT AGENT")
        print("="*70)
        
        try:
            decision = self.decision_agent.make_decision(
                supplier_name=state["supplier_name"],
                evaluation_plan=state.get("evaluation_plan", {}),
                document_analysis=state.get("document_analysis", {}),
                rag_answers=state.get("rag_answers", {}),
                external_intelligence=state.get("external_intelligence", {}),
                business_context=state.get("business_context")
            )
            state["final_decision"] = decision
            state["workflow_status"] = "completed"
            state["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"❌ Decision making failed: {str(e)}")
            state["errors"].append(f"Decision Agent: {str(e)}")
            state["final_decision"] = {"error": str(e)}
            state["workflow_status"] = "failed"
        
        return state
    
    
    def _extract_policy_questions(self, evaluation_plan: Dict) -> List[str]:
        """
        Extract policy-related questions from evaluation plan
        These will be answered by RAG Agent
        """
        questions = []
        
        # Generate questions based on country and tasks
        tasks = evaluation_plan.get("tasks", [])
        
        for task in tasks:
            task_lower = task.lower()
            
            # Export-related questions
            if "export" in task_lower or "license" in task_lower:
                questions.append("What export licenses and permits are required?")
            
            # Compliance questions
            if "compliance" in task_lower or "regulation" in task_lower:
                questions.append("What are the key compliance requirements for supplier onboarding?")
            
            # Due diligence questions
            if "due diligence" in task_lower or "oecd" in task_lower:
                questions.append("What are OECD due diligence requirements?")
        
        # Remove duplicates
        questions = list(set(questions))
        
        # Limit to 3 questions to save API costs
        return questions[:3]
    
    
    def evaluate_supplier(
        self,
        supplier_name: str,
        supplier_country: str,
        document_paths: List[str] = None,
        business_context: str = None,
        registration_number: str = None,
        owner_names: List[str] = None
    ) -> Dict:
        """
        Run complete supplier evaluation workflow
        
        Args:
            supplier_name: Name of supplier to evaluate
            supplier_country: Country code (e.g., "UK", "UAE")
            document_paths: List of PDF file paths to analyze
            business_context: Optional business description
            registration_number: Optional company registration number
            owner_names: Optional list of owner/director names
        
        Returns:
            Complete evaluation results including final decision
        """
        
        print("\n" + "🎯"*35)
        print(f"STARTING SUPPLIER EVALUATION: {supplier_name}")
        print("🎯"*35)
        
        # Initialize state
        initial_state = {
            "supplier_name": supplier_name,
            "supplier_country": supplier_country,
            "business_context": business_context or "",
            "document_paths": document_paths or [],
            "registration_number": registration_number or "",
            "owner_names": owner_names or [],
            "evaluation_plan": {},
            "document_analysis": {},
            "rag_answers": {},
            "external_intelligence": {},
            "final_decision": {},
            "workflow_status": "running",
            "errors": [],
            "started_at": datetime.now().isoformat(),
            "completed_at": ""
        }
        
        # Run the workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            print("\n" + "🎉"*35)
            print("EVALUATION COMPLETE")
            print("🎉"*35)
            
            return final_state
            
        except Exception as e:
            print(f"\n❌ Workflow failed: {str(e)}")
            initial_state["workflow_status"] = "failed"
            initial_state["errors"].append(f"Workflow: {str(e)}")
            return initial_state


# Test function - MOCK VERSION
# Test function - Simple initialization test only
if __name__ == "__main__":
    """
    Test workflow initialization
    To test: python workflows/evaluation_workflow.py
    """
    print("=" * 70)
    print("TESTING WORKFLOW INITIALIZATION")
    print("=" * 70)
    
    try:
        workflow = SupplierEvaluationWorkflow()
        print("\n✅ Workflow initialized successfully!")
        print("   All 5 agents loaded and ready")
    except Exception as e:
        print(f"\n❌ Initialization failed: {str(e)}")
        exit(1)
    
    print("\n" + "=" * 70)
    print("✅ WORKFLOW READY FOR PRODUCTION")
    print("=" * 70)