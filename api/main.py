"""
MAIN FASTAPI APPLICATION

This is the entry point for the entire backend API.
It creates the FastAPI app, configures CORS, and registers all routes.

To run this server:
1. Open terminal in project folder
2. Run: uvicorn api.main:app --reload
3. API will be available at: http://localhost:8000
4. Documentation at: http://localhost:8000/docs
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime
from sqlalchemy import text  # Add this line
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
# Import our modules
from .database import get_db, check_db_connection
from .models import (
    UserSignup, UserLogin, TokenResponse,
    SupplierCreate, SupplierResponse,
    EvaluationCreate, EvaluationResponse
)
from .auth import hash_password, verify_password, create_access_token
from .middleware import get_current_user


# Import routes
try:
    from .routes import suppliers, evaluations, documents, notifications, users
except ImportError as e:
    print(f"⚠️ Warning: Could not import routes: {e}")
    suppliers = None
    evaluations = None
    documents = None
    notifications = None
    users = None


# ============================================
# CREATE FASTAPI APP
# ============================================


app = FastAPI(
    title="Supplier Risk Intelligence API",
    description="Multi-agent AI system for automated supplier risk assessment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)




# ============================================
# CORS MIDDLEWARE (ALLOW FRONTEND TO CONNECT)
# ============================================

# CORS = Cross-Origin Resource Sharing
# This allows your React frontend (http://localhost:3000) to make requests
# to your FastAPI backend (http://localhost:8000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:5173",  # Vite development server
        "https://your-frontend-domain.com"  # Production frontend (update this later)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# ============================================
# STARTUP EVENT (RUN WHEN SERVER STARTS)
# ============================================

@app.on_event("startup")
async def startup_event():
    """
    This function runs once when the server starts.
    We use it to check if database connection is working.
    """
    print("🚀 Starting Supplier Risk Intelligence API...")
    
    # Check database connection
    if check_db_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed! Check your PostgreSQL container.")
    
    print("📚 API Documentation available at: http://localhost:8000/docs")


# ============================================
# HEALTH CHECK ENDPOINT
# ============================================

@app.get("/", tags=["Health"])
async def root():
    """
    Simple health check endpoint.
    Returns basic API information.
    """
    return {
        "message": "Supplier Risk Intelligence API",
        "status": "running",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database query
        db.execute(text("SELECT 1"))  # ✅
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/auth/signup", response_model=TokenResponse, tags=["Authentication"])
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Process:
    1. Check if email already exists
    2. Hash the password
    3. Create company record
    4. Create user record
    5. Generate JWT token
    6. Return token
    
    Request body example:
    {
        "email": "user@company.com",
        "password": "SecurePass123!",
        "company_name": "TechCorp Inc"
    }
    
    Response:
    {
        "access_token": "eyJhbGc...",
        "token_type": "bearer"
    }
    """
    # Check if user already exists
    existing_user = db.execute(
        text("SELECT user_id FROM users WHERE email = :email"),  # ✅
        {"email": user_data.email}
    ).fetchone()

    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password (NEVER store plain text passwords!)
    hashed_password = hash_password(user_data.password)
    
    # Create company first
    # ---------------------------------------------------
    # Step 1: Check if company already exists
    # ---------------------------------------------------


    # ---------------------------------------------------
    # Determine company and role assignment
    # ---------------------------------------------------

    company = db.execute(
        text("SELECT company_id FROM companies WHERE company_name = :company_name"),
        {"company_name": user_data.company_name}
    ).fetchone()

    if company:
        company_id = company[0]
        assigned_role = "analyst"   # Existing company → analyst
    else:
        # Create new company
        company_result = db.execute(
            text("""
            INSERT INTO companies (company_name, subscription_tier, max_users, created_at, updated_at)
            VALUES (:company_name, 'free', 5, NOW(), NOW())
            RETURNING company_id
            """),
            {"company_name": user_data.company_name}
        )
        company_id = company_result.fetchone()[0]
        db.commit()

        assigned_role = "admin"  # First user becomes admin

    # ---------------------------------------------------
    # Create user
    # ---------------------------------------------------

    user_result = db.execute(
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
        RETURNING user_id
        """),
        {
            "company_id": company_id,
            "full_name": user_data.full_name,
            "email": user_data.email,
            "password_hash": hashed_password,
            "role": assigned_role
        }
    )

    user_id = user_result.fetchone()[0]
    db.commit()

    
    
    # Generate JWT token
    token = create_access_token(
        data={
            "user_id": str(user_id),        # ✅ Convert UUID to string
            "email": user_data.email,
            "company_id": str(company_id),  # ✅ Convert UUID to string
            "role": assigned_role
        }
    )

    
    return TokenResponse(access_token=token)


@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login existing user.
    
    Process:
    1. Find user by email
    2. Verify password against stored hash
    3. Generate JWT token
    4. Return token
    
    Request body example:
    {
        "email": "user@company.com",
        "password": "SecurePass123!"
    }
    """
    # Find user
    # Find user
    user = db.execute(
        text("""
        SELECT user_id, company_id, email, password_hash, role, is_active
        FROM users
        WHERE email = :email
        """),  # ✅
        {"email": credentials.email}
    ).fetchone()

    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate token
    token = create_access_token(
        data={
            "user_id": str(user.user_id),
            "email": user.email,
            "company_id": str(user.company_id),
            "role": user.role
        }
    )

    
    return TokenResponse(access_token=token)
    

@app.get("/auth/me", tags=["Authentication"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):


    """
    Get current logged-in user information.
    
    This endpoint requires authentication (valid JWT token).
    It's useful for the frontend to get user details after login.
    """
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "company_id": current_user["company_id"],
        "role": current_user["role"]
    }


# ============================================
# REGISTER ROUTE MODULES
# ============================================



# Include supplier routes
if suppliers is not None:
    app.include_router(
        suppliers.router,
        prefix="/api/suppliers",
        tags=["Suppliers"]
    )

# Include evaluation routes
if evaluations is not None:
    app.include_router(
        evaluations.router,
        prefix="/api/evaluations",
        tags=["Evaluations"]
    )

if documents is not None:
    app.include_router(
        documents.router,
        prefix="/api/documents",
        tags=["Documents"]
    )

if notifications is not None:
    app.include_router(
        notifications.router,
        prefix="/api/notifications",
        tags=["Notifications"]
    )


if users is not None:
    app.include_router(
        users.router,
        prefix="/api/users",
        tags=["Users"]
    )

# ============================================
# ERROR HANDLERS
# ============================================




@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"❌ Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred.",
            "error_type": type(exc).__name__
        }
    )