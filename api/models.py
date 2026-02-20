"""
DATA MODELS FOR API REQUEST/RESPONSE VALIDATION

This file defines Pydantic models, which are like "blueprints" for data.
They automatically validate incoming data and provide clear error messages.

Think of it like a form: If a field says "email", it must be a valid email.
If required fields are missing, Pydantic will reject the data automatically.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# ============================================
# AUTHENTICATION MODELS
# ============================================


class UserSignup(BaseModel):
    """
    Data required when a new user signs up.

    Example JSON:
    {  
        "full_name" : "Sahad M"
        "email": "user@company.com",
        "password": "SecurePassword123!",
        "company_name": "TechCorp Inc"
    }
    """
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)
    company_name: str = Field(..., min_length=2)


class UserLogin(BaseModel):
    """
    Data required when a user logs in.
    
    Example JSON:
    {
        "email": "user@company.com",
        "password": "SecurePassword123!"
    }
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Response sent back after successful login.
    
    Example JSON:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    """
    access_token: str  # JWT token for authentication
    token_type: str = "bearer"  # Always "bearer" for JWT


# ============================================
# SUPPLIER MODELS
# ============================================

class SupplierCreate(BaseModel):
    """
    Data required to create a new supplier.
    
    Example JSON:
    {
        "supplier_name": "TechTextiles Ltd",
        "country": "United Kingdom",
        "registration_number": "12345678",
        "business_context": "Textile manufacturer specializing in sustainable fabrics"
    }
    """
    supplier_name: str = Field(..., min_length=2)
    country: str
    registration_number: Optional[str] = None  # Optional field
    business_context: Optional[str] = None


class SupplierResponse(BaseModel):
    """
    Response when retrieving supplier information.
    Includes all supplier data plus database-generated fields.
    """
    supplier_id: UUID
    supplier_name: str
    country: str
    registration_number: Optional[str]
    risk_level: Optional[str]  # Low, Medium, High (set after evaluation)
    created_at: datetime
    updated_at: datetime

    class Config:
        # Allows Pydantic to work with SQLAlchemy database models
        from_attributes = True


# ============================================
# EVALUATION MODELS
# ============================================

class EvaluationCreate(BaseModel):
    """
    Data required to start a new supplier evaluation.
    
    Example JSON:
    {
        "supplier_id": 123,
        "business_context": "Evaluating for high-volume textile contract",
        "document_ids": [456, 789]  // IDs of uploaded PDFs
    }
    """
    supplier_id: UUID
    business_context: str = Field(..., min_length=10)
    document_ids: List[UUID] = []  # List of uploaded document IDs


class EvaluationResponse(BaseModel):
    """
    Response after evaluation completes.
    Contains the full risk assessment.
    """
    evaluation_id: UUID
    supplier_id: UUID
    status: str  # "pending", "processing", "completed", "failed"
    risk_level: Optional[str]  # Low, Medium, High
    confidence_score: Optional[float]  # 0.0 to 1.0
    reasoning: Optional[str]
    recommended_actions: Optional[List[str]]
    risk_factors: Optional[dict]  # {"positive": [...], "negative": [...]}
    agent_outputs: Optional[dict]  # Full output from all 5 agents
    openai_cost_usd: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================
# DOCUMENT UPLOAD MODELS
# ============================================

class DocumentUploadResponse(BaseModel):
    """
    Response after a document is uploaded to MinIO.
    """
    document_id: UUID
    file_name: str
    file_path: str  # Path in MinIO storage
    file_size_bytes: int
    uploaded_at: datetime

    class Config:
        from_attributes = True