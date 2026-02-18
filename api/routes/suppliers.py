"""
SUPPLIER MANAGEMENT ROUTES

This file contains all API endpoints for managing suppliers:
- Create new supplier
- Get all suppliers (with filtering)
- Get single supplier by ID
- Update supplier
- Delete supplier
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy import text  # Add this line
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SupplierCreate, SupplierResponse
from ..middleware import get_current_user
from uuid import UUID

# Create router (like a mini-app for supplier routes)
router = APIRouter()


# ============================================
# CREATE NEW SUPPLIER
# ============================================

@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new supplier in the system.
    
    Requires authentication (JWT token).
    
    Request body example:
    {
        "supplier_name": "TechTextiles Ltd",
        "country": "United Kingdom",
        "registration_number": "12345678",
        "business_context": "Textile manufacturer"
    }
    
    Returns:
    - 201 Created with supplier details
    - 400 Bad Request if supplier already exists
    """
    # Get company_id from authenticated user
    company_id = current_user["company_id"]
    
    # Check if supplier already exists for this company
    existing = db.execute(
        text("""
        SELECT supplier_id FROM suppliers
        WHERE company_id = :company_id
        AND supplier_name = :supplier_name
        AND country = :country
        """),  # ✅
        {
            "company_id": company_id,
            "supplier_name": supplier_data.supplier_name,
            "country": supplier_data.country
        }
    ).fetchone()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier with this name and country already exists"
        )
    
    # Insert new supplier
    result = db.execute(
        text("""
        INSERT INTO suppliers (
            company_id, supplier_name, country, registration_number,
            risk_level, created_at, updated_at
        )
        VALUES (
            :company_id, :supplier_name, :country, :registration_number,
            NULL, NOW(), NOW()
        )
        RETURNING supplier_id, supplier_name, country, registration_number,
                risk_level, created_at, updated_at
        """),  # ✅
        {
            "company_id": company_id,
            "supplier_name": supplier_data.supplier_name,
            "country": supplier_data.country,
            "registration_number": supplier_data.registration_number
        }
    )
    
    supplier = result.fetchone()
    db.commit()
    
    return SupplierResponse(
        supplier_id=supplier.supplier_id,
        supplier_name=supplier.supplier_name,
        country=supplier.country,
        registration_number=supplier.registration_number,
        risk_level=supplier.risk_level,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at
    )


# ============================================
# GET ALL SUPPLIERS (WITH FILTERS)
# ============================================

@router.get("/", response_model=List[SupplierResponse])
async def get_suppliers(
    country: Optional[str] = Query(None, description="Filter by country"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (Low/Medium/High)"),
    search: Optional[str] = Query(None, description="Search supplier name"),
    limit: int = Query(100, ge=1, le=1000, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all suppliers for the current user's company.
    
    Supports filtering by:
    - country (e.g., "United Kingdom")
    - risk_level (e.g., "High")
    - search (searches supplier name)
    
    Supports pagination with limit and offset.
    
    Example requests:
    - GET /api/suppliers (get all)
    - GET /api/suppliers?country=United%20Kingdom (filter by country)
    - GET /api/suppliers?risk_level=High (filter by risk)
    - GET /api/suppliers?search=Tech (search name)
    - GET /api/suppliers?limit=10&offset=0 (pagination)
    """
    company_id = current_user["company_id"]
    
    # Build query dynamically based on filters
    query = "SELECT * FROM suppliers WHERE company_id = :company_id"
    params = {"company_id": company_id}
    
    if country:
        query += " AND country = :country"
        params["country"] = country
    
    if risk_level:
        query += " AND risk_level = :risk_level"
        params["risk_level"] = risk_level
    
    if search:
        query += " AND supplier_name ILIKE :search"
        params["search"] = f"%{search}%"
    
    query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset
    
    result = db.execute(text(query), params)
    suppliers = result.fetchall()
    
    return [
        SupplierResponse(
            supplier_id=s.supplier_id,
            supplier_name=s.supplier_name,
            country=s.country,
            registration_number=s.registration_number,
            risk_level=s.risk_level,
            created_at=s.created_at,
            updated_at=s.updated_at
        )
        for s in suppliers
    ]


# ============================================
# GET SINGLE SUPPLIER BY ID
# ============================================

@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific supplier.
    
    Example: GET /api/suppliers/123
    """
    company_id = current_user["company_id"]

    result = db.execute(
        text("""
        SELECT * FROM suppliers
        WHERE supplier_id = :supplier_id AND company_id = :company_id
        """),  # ✅
        {"supplier_id": supplier_id, "company_id": company_id}
    )
    
    supplier = result.fetchone()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return SupplierResponse(
        supplier_id=supplier.supplier_id,
        supplier_name=supplier.supplier_name,
        country=supplier.country,
        registration_number=supplier.registration_number,
        risk_level=supplier.risk_level,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at
    )


# ============================================
# UPDATE SUPPLIER
# ============================================

@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: UUID,
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update supplier information.
    
    Example: PUT /api/suppliers/123
    Request body:
    {
        "supplier_name": "Updated Name",
        "country": "United Kingdom",
        "registration_number": "87654321"
    }
    """
    company_id = current_user["company_id"]
    
    # Check if supplier exists and belongs to this company
    existing = db.execute(
        text("""
        SELECT supplier_id FROM suppliers
        WHERE supplier_id = :supplier_id AND company_id = :company_id
        """),  # ✅
        {"supplier_id": supplier_id, "company_id": company_id}
    ).fetchone()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Update supplier
    result = db.execute(
        text("""
        UPDATE suppliers
        SET supplier_name = :supplier_name,
            country = :country,
            registration_number = :registration_number,
            updated_at = NOW()
        WHERE supplier_id = :supplier_id
        RETURNING supplier_id, supplier_name, country, registration_number,
                risk_level, created_at, updated_at
        """),  # ✅
        {
            "supplier_id": supplier_id,
            "supplier_name": supplier_data.supplier_name,
            "country": supplier_data.country,
            "registration_number": supplier_data.registration_number
        }
    )
    
    supplier = result.fetchone()
    db.commit()
    
    return SupplierResponse(
        supplier_id=supplier.supplier_id,
        supplier_name=supplier.supplier_name,
        country=supplier.country,
        registration_number=supplier.registration_number,
        risk_level=supplier.risk_level,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at
    )


# ============================================
# DELETE SUPPLIER
# ============================================

@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a supplier.
    
    WARNING: This will also delete all associated evaluations and documents!
    
    Example: DELETE /api/suppliers/123
    """
    company_id = current_user["company_id"]
    
    # Check if supplier exists
    existing = db.execute(
        text("""
        SELECT supplier_id FROM suppliers
        WHERE supplier_id = :supplier_id AND company_id = :company_id
        """),  # ✅
        {"supplier_id": supplier_id, "company_id": company_id}
    ).fetchone()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Delete supplier (CASCADE will delete related records)
    db.execute(
        text("DELETE FROM suppliers WHERE supplier_id = :supplier_id"),  # ✅
        {"supplier_id": supplier_id}
    )   
    db.commit()
    
    return None  # 204 No Content (successful deletion)