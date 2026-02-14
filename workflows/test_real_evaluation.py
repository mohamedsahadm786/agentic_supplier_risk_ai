"""
Real End-to-End Evaluation Test
Tests the complete workflow with real API calls
Cost: ~$0.10-0.20 per run
"""

from evaluation_workflow import SupplierEvaluationWorkflow
import json

print("=" * 70)
print("REAL END-TO-END SUPPLIER EVALUATION TEST")
print("=" * 70)
print("\n⚠️ WARNING: This will use OpenAI API credits (~$0.10-0.20)")
print("Press ENTER to continue or Ctrl+C to cancel...")
input()

# Initialize workflow
print("\n🔧 Initializing workflow...")
workflow = SupplierEvaluationWorkflow()

print("\n🚀 Starting evaluation...")

result = workflow.evaluate_supplier(
    supplier_name="AMAZON UK SERVICES LTD",  # Real company for testing
    supplier_country="UK",
    business_context="E-commerce and logistics services",
    registration_number="04017546",  # Real Amazon UK registration number
    document_paths=[],  # No documents for this test
    owner_names=[]
)

# Display results
print("\n" + "=" * 70)
print("📊 EVALUATION RESULTS")
print("=" * 70)

print(f"\n🏢 SUPPLIER: {result['supplier_name']}")
print(f"🌍 COUNTRY: {result['supplier_country']}")
print(f"⏱️ STARTED: {result['started_at']}")
print(f"⏱️ COMPLETED: {result['completed_at']}")
print(f"📊 STATUS: {result['workflow_status']}")

print("\n" + "=" * 70)
print("FINAL DECISION")
print("=" * 70)

decision = result.get('final_decision', {})
print(f"\n⚖️ RISK LEVEL: {decision.get('risk_level', 'Unknown')}")
print(f"🎯 CONFIDENCE: {decision.get('confidence_score', 0):.0%}")
print(f"\n📋 SUMMARY:\n{decision.get('decision_summary', 'N/A')}")

print(f"\n✅ POSITIVE FACTORS ({len(decision.get('positive_factors', []))}):")
for factor in decision.get('positive_factors', [])[:5]:
    print(f"   + {factor}")

print(f"\n⚠️ NEGATIVE FACTORS ({len(decision.get('negative_factors', []))}):")
for factor in decision.get('negative_factors', [])[:5]:
    print(f"   - {factor}")

print(f"\n🎯 RECOMMENDED ACTIONS ({len(decision.get('recommended_actions', []))}):")
for i, action in enumerate(decision.get('recommended_actions', [])[:5], 1):
    print(f"   {i}. {action}")

# Show errors if any
if result.get('errors'):
    print(f"\n⚠️ ERRORS ENCOUNTERED ({len(result['errors'])}):")
    for error in result['errors']:
        print(f"   - {error}")

# Save full results to file
output_file = "test_evaluation_results.json"
with open(output_file, 'w') as f:
    json.dump(result, f, indent=2)

print(f"\n💾 Full results saved to: {output_file}")
print("\n" + "=" * 70)
print("✅ TEST COMPLETED")
print("=" * 70)