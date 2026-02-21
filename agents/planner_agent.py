"""
Agent 1: Planner Agent
Role: Strategic task decomposition - breaks down supplier evaluation into actionable steps
Does NOT: Read documents, call tools, or make decisions
Technology: OpenAI GPT-4
"""

from typing import List, Dict




class PlannerAgent:
    """
    Planner Agent - Creates evaluation plans
    
    Think of this as a project manager who:
    - Takes a high-level request ("Evaluate this supplier")
    - Breaks it into specific tasks
    - Doesn't do the tasks itself, just plans them
    """

    def __init__(self, db, company_id, evaluation_id):
        """
        Initialize Planner Agent with DB + context.
        """

        from api.services.llm_service import LLMService

        self.db = db
        self.company_id = company_id
        self.evaluation_id = evaluation_id
        self.llm = LLMService(db)

        print("✅ Planner Agent initialized (LLM centralized)")

    
    def create_evaluation_plan(
        self, 
        supplier_name: str,
        supplier_country: str,
        business_context: str = None
    ) -> Dict[str, List[str]]:
        """
        Create a detailed evaluation plan for a supplier
        
        Args:
            supplier_name: Name of the supplier (e.g., "TechTextiles Ltd")
            supplier_country: Country code (e.g., "UK", "UAE", "CN")
            business_context: Optional context (e.g., "textile manufacturer", "electronics trader")
        
        Returns:
            Dictionary with:
            - 'tasks': List of evaluation tasks
            - 'reasoning': Why these tasks were chosen
        
        Example:
            plan = planner.create_evaluation_plan(
                supplier_name="TechTextiles Ltd",
                supplier_country="UK",
                business_context="textile manufacturer"
            )
        """
        
        print(f"\n🧠 Planner Agent: Creating evaluation plan for {supplier_name}...")
        
        # Create the prompt for GPT-4
        system_prompt = """You are a strategic risk assessment planner for supplier evaluations.

Your job is to create a detailed evaluation plan that breaks down the supplier assessment into specific, actionable tasks.

Consider these evaluation areas:
1. Company verification (registration, legal status)
2. Document analysis (financial statements, certificates, licenses)
3. Compliance checks (export licenses, industry regulations)
4. External intelligence (news, sanctions, watchlists)
5. Financial health assessment
6. Reputational risk analysis

Create 5-8 specific tasks that are:
- Clear and actionable
- Relevant to the supplier's country and industry
- Prioritized by risk level
- Cover both internal documents and external sources

Return your response as a JSON object with:
{
    "tasks": ["task 1", "task 2", ...],
    "reasoning": "Brief explanation of why these tasks were chosen"
}"""

        # Build user message with supplier details
        user_message = f"""Create an evaluation plan for:

Supplier Name: {supplier_name}
Country: {supplier_country}"""
        
        if business_context:
            user_message += f"\nBusiness Type: {business_context}"
        
        user_message += "\n\nProvide a comprehensive evaluation plan."
        
        try:
            # Call OpenAI API
            response = self.llm.invoke(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                company_id=self.company_id,
                evaluation_id=self.evaluation_id,
                agent_name="planner_agent",
                response_format={"type": "json_object"},
                temperature=0.7
            )



            
            
            # Extract the plan from response
            import json
            plan = json.loads(response["content"])
            
            
            
            # Print the plan for visibility
            print(f"✅ Plan created with {len(plan.get('tasks', []))} tasks")
            print("\n📋 Evaluation Tasks:")
            for i, task in enumerate(plan.get('tasks', []), 1):
                print(f"   {i}. {task}")
            
            return plan
            
        except Exception as e:
            print(f"❌ Error creating plan: {str(e)}")
            
            # Return a fallback generic plan if API fails
            fallback_plan = {
                "tasks": [
                    f"Verify {supplier_name} company registration in {supplier_country}",
                    "Extract and validate key information from submitted documents",
                    "Check compliance with export regulations and licenses",
                    "Search for recent news articles and media coverage",
                    "Check international sanctions and watchlists",
                    "Assess financial health from available documents",
                    "Identify any red flags or inconsistencies"
                ],
                "reasoning": "Generic evaluation plan (API call failed)"
            }
            
            print("⚠️ Using fallback generic plan")
            return fallback_plan


# Test function - runs when you execute this file directly
if __name__ == "__main__":
    """
    Test the Planner Agent
    Run this file directly to test: python agents/planner_agent.py
    """
    
    print("=" * 60)
    print("TESTING PLANNER AGENT")
    print("=" * 60)
    
    # Create agent instance
    agent = PlannerAgent()
    
    # Test Case 1: UK Textile Manufacturer
    print("\n\n🧪 TEST CASE 1: UK Textile Manufacturer")
    print("-" * 60)
    plan1 = agent.create_evaluation_plan(
        supplier_name="TechTextiles Ltd",
        supplier_country="UK",
        business_context="textile manufacturer"
    )
    print(f"\nReasoning: {plan1.get('reasoning')}")
    
    # Test Case 2: UAE Trading Company
    print("\n\n🧪 TEST CASE 2: UAE Trading Company")
    print("-" * 60)
    plan2 = agent.create_evaluation_plan(
        supplier_name="Emirates Global Trading LLC",
        supplier_country="UAE",
        business_context="electronics trading company"
    )
    print(f"\nReasoning: {plan2.get('reasoning')}")
    
    print("\n" + "=" * 60)
    print("✅ PLANNER AGENT TESTS COMPLETED")
    print("=" * 60)