"""
EVALUATION MANAGEMENT ROUTES

This file contains all API endpoints for supplier risk evaluations:
- Create new evaluation (triggers the 5-agent workflow)
- Get all evaluations
- Get single evaluation by ID
- Get evaluations for a specific supplier
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import traceback
from sqlalchemy import text  # Add this line
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import EvaluationCreate, EvaluationResponse
from ..middleware import get_current_user
from uuid import UUID

# Import the LangGraph workflow with error handling
try:
    from workflows.evaluation_workflow import run_evaluation
    WORKFLOW_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Could not import evaluation workflow: {e}")
    print("   Evaluation creation will return mock data instead of running real agents.")
    run_evaluation = None
    WORKFLOW_AVAILABLE = False

# Create router
router = APIRouter()


# ============================================
# CREATE NEW EVALUATION
# ============================================

@router.post("/", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    evaluation_data: EvaluationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new supplier risk evaluation.
    """
    company_id = current_user["company_id"]
    
    # Verify supplier exists and belongs to this company
    supplier = db.execute(
        text(
        """
        SELECT supplier_id, supplier_name, country, registration_number
        FROM suppliers
        WHERE supplier_id = :supplier_id AND company_id = :company_id
        """
        ),
        {"supplier_id": evaluation_data.supplier_id, "company_id": company_id}
    ).fetchone()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Create evaluation record with status="processing"
    # Create evaluation record with status="pending"
    result = db.execute(
        text(
        """
        INSERT INTO evaluations (
            company_id,
            supplier_id,
            user_id,
            business_context,
            status,
            created_at
        )
        VALUES (
            :company_id,
            :supplier_id,
            :user_id,
            :business_context,
            'pending',
            NOW()
        )
        RETURNING evaluation_id, supplier_id, status,
                business_context, created_at
        """
        ),
        {
            "company_id": company_id,
            "supplier_id": evaluation_data.supplier_id,
            "user_id": current_user["user_id"],
            "business_context": evaluation_data.business_context
        }
    )

    
    evaluation = result.fetchone()
    db.commit()
    evaluation_id = evaluation.evaluation_id
    
    # Add background task to run the evaluation workflow
    if WORKFLOW_AVAILABLE:
        background_tasks.add_task(
            run_evaluation_background,
            evaluation_id=evaluation_id,
            supplier_name=supplier.supplier_name,
            country=supplier.country,
            registration_number=supplier.registration_number,
            business_context=evaluation_data.business_context
        )
    else:
        background_tasks.add_task(
            run_mock_evaluation,
            evaluation_id=evaluation_id
        )
    
    return EvaluationResponse(
        evaluation_id=evaluation.evaluation_id,
        supplier_id=evaluation.supplier_id,
        status=evaluation.status,
        risk_level=None,
        confidence_score=None,
        reasoning=None,
        recommended_actions=None,
        risk_factors=None,
        agent_outputs=None,
        openai_cost_usd=None,
        created_at=evaluation.created_at,
        completed_at=None
    )


# ============================================
# BACKGROUND TASK: RUN REAL EVALUATION
# ============================================

def run_evaluation_background(
    evaluation_id: UUID,
    supplier_name: str,
    country: str,
    registration_number: Optional[str],
    business_context: str
):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/supplier_risk_db"
    )
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print(f"🚀 Starting evaluation {evaluation_id} for supplier: {supplier_name}")
        
        if not WORKFLOW_AVAILABLE or run_evaluation is None:
            raise Exception("Evaluation workflow not available")
        
        supplier_info = {
            "supplier_name": supplier_name,
            "country": country,
            "registration_number": registration_number or "Not provided",
            "business_context": business_context
        }
        
        print(f"   Running 5-agent workflow...")
        final_state = run_evaluation(supplier_info)
        
        decision_output = final_state.get("decision_output", {})
        risk_level = decision_output.get("risk_level")

        if risk_level not in ["Low", "Medium", "High"]:
            risk_level = None
        

        confidence_score = decision_output.get("confidence_score", 0.0)
        reasoning = decision_output.get("reasoning", "No reasoning available")
        recommended_actions = decision_output.get("recommended_actions", [])
        risk_factors = decision_output.get("risk_factors", {})
        
        openai_cost = 0.05
        
        db.execute(
            text(
            """
            UPDATE evaluations
            SET status = 'completed',
                risk_level = :risk_level,
                confidence_score = :confidence_score,
                reasoning = :reasoning,
                recommended_actions = :recommended_actions,
                risk_factors = :risk_factors,
                agent_outputs = :agent_outputs,
                openai_cost_usd = :openai_cost,
                completed_at = NOW(),
                updated_at = NOW()
            WHERE evaluation_id = :evaluation_id
            """
            ),
            {
                "evaluation_id": evaluation_id,
                "risk_level": risk_level,
                "confidence_score": confidence_score,
                "reasoning": reasoning,
                "recommended_actions": json.dumps(recommended_actions),
                "risk_factors": json.dumps(risk_factors),
                "agent_outputs": json.dumps(final_state),
                "openai_cost": openai_cost
            }
        )
        db.commit()
        
        db.execute(
            text(
            """
            UPDATE suppliers
            SET risk_level = :risk_level,
                updated_at = NOW()
            WHERE supplier_id = (
                SELECT supplier_id FROM evaluations WHERE evaluation_id = :evaluation_id
            )
            """
            ),
            {"risk_level": risk_level, "evaluation_id": evaluation_id}
        )
        db.commit()
        
        print(f"✅ Evaluation {evaluation_id} completed successfully!")
        
    except Exception as e:
        print(f"❌ Evaluation {evaluation_id} failed: {e}")
        print(traceback.format_exc())
        
        db.execute(
            text(
            """
            UPDATE evaluations
            SET status = 'failed',
                reasoning = :error_message,
                updated_at = NOW()
            WHERE evaluation_id = :evaluation_id
            """
            ),
            {
                "evaluation_id": evaluation_id,
                "error_message": f"Evaluation failed: {str(e)}"
            }
        )
        db.commit()
        
    finally:
        db.close()


# ============================================
# BACKGROUND TASK: RUN MOCK EVALUATION (FALLBACK)
# ============================================

def run_mock_evaluation(evaluation_id: UUID):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os
    from dotenv import load_dotenv
    import time
    
    load_dotenv()
    
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/supplier_risk_db"
    )
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print(f"🔄 Running MOCK evaluation {evaluation_id} (workflow not available)")
        
        time.sleep(3)
        
        mock_result = {
            "risk_level": "Medium",
            "confidence_score": 0.75,
            "reasoning": "MOCK EVALUATION: This is test data. Real evaluation requires workflow setup.",
            "recommended_actions": [
                "Complete workflow setup",
                "Test with real supplier data",
                "Review agent outputs"
            ],
            "risk_factors": {
                "positive": ["Mock positive factor 1", "Mock positive factor 2"],
                "negative": ["Mock negative factor 1"]
            }
        }
        
        db.execute(
            text(
            """
            UPDATE evaluations
            SET status = 'completed',
                risk_level = :risk_level,
                confidence_score = :confidence_score,
                reasoning = :reasoning,
                recommended_actions = :recommended_actions,
                risk_factors = :risk_factors,
                openai_cost_usd = 0.00,
                completed_at = NOW(),
                updated_at = NOW()
            WHERE evaluation_id = :evaluation_id
            """
            ),
            {
                "evaluation_id": evaluation_id,
                "risk_level": mock_result["risk_level"],
                "confidence_score": mock_result["confidence_score"],
                "reasoning": mock_result["reasoning"],
                "recommended_actions": json.dumps(mock_result["recommended_actions"]),
                "risk_factors": json.dumps(mock_result["risk_factors"])
            }
        )
        db.commit()
        
        print(f"✅ Mock evaluation {evaluation_id} completed")
        
    except Exception as e:
        print(f"❌ Mock evaluation {evaluation_id} failed: {e}")
        
        db.execute(
            text(
            """
            UPDATE evaluations
            SET status = 'failed',
                reasoning = :error_message,
                updated_at = NOW()
            WHERE evaluation_id = :evaluation_id
            """
            ),
            {
                "evaluation_id": evaluation_id,
                "error_message": f"Mock evaluation failed: {str(e)}"
            }
        )
        db.commit()
        
    finally:
        db.close()


# ============================================
# GET ALL EVALUATIONS
# ============================================

@router.get("/", response_model=List[EvaluationResponse])
async def get_evaluations(
    supplier_id: Optional[UUID] = None,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]
    
    query = "SELECT * FROM evaluations WHERE company_id = :company_id"
    params = {"company_id": company_id}
    
    if supplier_id:
        query += " AND supplier_id = :supplier_id"
        params["supplier_id"] = supplier_id
    
    if status:
        query += " AND status = :status"
        params["status"] = status
    
    if risk_level:
        query += " AND risk_level = :risk_level"
        params["risk_level"] = risk_level
    
    query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset
    
    result = db.execute(text(query), params)
    evaluations = result.fetchall()
    
    return [
        EvaluationResponse(
            evaluation_id=e.evaluation_id,
            supplier_id=e.supplier_id,
            status=e.status,
            risk_level=e.risk_level,
            confidence_score=e.confidence_score,
            reasoning=e.reasoning,
            recommended_actions=e.recommended_actions,
            risk_factors=e.risk_factors,
            agent_outputs=e.agent_outputs,
            openai_cost_usd=e.openai_cost_usd,
            created_at=e.created_at,
            completed_at=e.completed_at
        )
        for e in evaluations
    ]


# ============================================
# GET SINGLE EVALUATION BY ID
# ============================================

@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = current_user["company_id"]
    
    result = db.execute(
        text(
        """
        SELECT * FROM evaluations
        WHERE evaluation_id = :evaluation_id AND company_id = :company_id
        """
        ),
        {"evaluation_id": evaluation_id, "company_id": company_id}
    )
    
    evaluation = result.fetchone()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    return EvaluationResponse(
        evaluation_id=evaluation.evaluation_id,
        supplier_id=evaluation.supplier_id,
        status=evaluation.status,
        risk_level=evaluation.risk_level,
        confidence_score=evaluation.confidence_score,
        reasoning=evaluation.reasoning,
        recommended_actions=evaluation.recommended_actions,
        risk_factors=evaluation.risk_factors,
        agent_outputs=evaluation.agent_outputs,
        openai_cost_usd=evaluation.openai_cost_usd,
        created_at=evaluation.created_at,
        completed_at=evaluation.completed_at
    )