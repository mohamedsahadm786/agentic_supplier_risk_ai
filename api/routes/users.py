"""
USER MANAGEMENT ROUTES

This file allows admins to:
- Create new users (analyst or viewer)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional

from ..database import get_db
from ..middleware import get_current_user, require_role
from ..auth import hash_password

router = APIRouter()


# ============================================
# REQUEST MODEL
# ============================================

class UserCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str  # Must be "analyst" or "viewer"


# ============================================
# CREATE USER (ADMIN ONLY)
# ============================================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """
    Admin creates new user inside same company.
    """

    company_id = current_user["company_id"]

    # ---------------------------------------------------
    # Validate role
    # ---------------------------------------------------

    if user_data.role not in ["analyst", "viewer"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either 'analyst' or 'viewer'"
        )

    # ---------------------------------------------------
    # Check if email already exists
    # ---------------------------------------------------

    existing_user = db.execute(
        text("SELECT user_id FROM users WHERE email = :email"),
        {"email": user_data.email}
    ).fetchone()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # ---------------------------------------------------
    # Enforce max_users limit
    # ---------------------------------------------------

    company = db.execute(
        text("""
        SELECT max_users FROM companies
        WHERE company_id = :company_id
        """),
        {"company_id": company_id}
    ).fetchone()

    current_user_count = db.execute(
        text("""
        SELECT COUNT(*) FROM users
        WHERE company_id = :company_id
        """),
        {"company_id": company_id}
    ).scalar()

    if current_user_count >= company.max_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User limit reached for your subscription plan"
        )

    # ---------------------------------------------------
    # Hash password
    # ---------------------------------------------------

    hashed_password = hash_password(user_data.password)

    # ---------------------------------------------------
    # Insert user
    # ---------------------------------------------------

    db.execute(
        text("""
        INSERT INTO users (
            company_id,
            full_name,
            email,
            password_hash,
            role,
            is_active,
            created_at,
            updated_at
        )
        VALUES (
            :company_id,
            :full_name,
            :email,
            :password_hash,
            :role,
            TRUE,
            NOW(),
            NOW()
        )
        """),
        {
            "company_id": company_id,
            "full_name": user_data.full_name,
            "email": user_data.email,
            "password_hash": hashed_password,
            "role": user_data.role
        }
    )

    db.commit()

    return {
        "message": f"User created successfully with role '{user_data.role}'"
    }