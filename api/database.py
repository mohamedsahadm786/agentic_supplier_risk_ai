"""
DATABASE CONNECTION & SESSION MANAGEMENT

This file creates a "connection pool" to PostgreSQL.
Think of it like a phone line to the database - we open it once
and reuse it for all requests (instead of reconnecting every time).

Key Concepts:
- Engine: The main database connection
- SessionLocal: A factory that creates database sessions
- Session: A temporary connection for one request
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# DATABASE CONFIGURATION
# ============================================

# Get database URL from environment variables
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://supplier_risk_user:change_this_password_in_production@127.0.0.1:5432/supplier_risk_db"
)

# Fix: Replace 'localhost' with '127.0.0.1' to force IPv4
# This avoids IPv6 (::1) connection issues on Windows
DATABASE_URL = DATABASE_URL.replace("@localhost:", "@127.0.0.1:")



# Create database engine
# echo=False means don't print every SQL query (set to True for debugging)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL queries in console
    pool_pre_ping=True,  # Check connection health before using
    pool_size=10,  # Number of persistent connections
    max_overflow=20  # Extra connections if pool is full
)

# Session factory - creates new database sessions
SessionLocal = sessionmaker(
    autocommit=False,  # We manually commit transactions
    autoflush=False,   # We manually flush changes
    bind=engine
)

# Base class for all database models (tables)
Base = declarative_base()


# ============================================
# DEPENDENCY FUNCTION FOR FASTAPI
# ============================================

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session to API endpoints.
    
    How it works:
    1. Creates a new database session
    2. Yields it to the API endpoint (like lending a book)
    3. Automatically closes the session when done (returns the book)
    
    Usage in FastAPI:
    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        users = db.query(User).all()
        return users
    
    The "Depends(get_db)" part tells FastAPI to call this function
    and pass the session to the endpoint.
    """
    db = SessionLocal()
    try:
        yield db  # Provide the session to the endpoint
    finally:
        db.close()  # Always close the session (even if error occurs)


# ============================================
# DATABASE INITIALIZATION FUNCTION
# ============================================

def init_db():
    """
    Initialize database tables.
    
    This creates all tables defined in our SQLAlchemy models.
    We won't use this in production (we already have tables from schema.sql),
    but it's useful for testing.
    """
    Base.metadata.create_all(bind=engine)


# ============================================
# HEALTH CHECK FUNCTION
# ============================================

def check_db_connection() -> bool:
    """
    Test if database connection is working.
    
    Returns:
    - True if connection successful
    - False if connection failed
    """
    try:
        from sqlalchemy import text  # Import text function
        
        # Try to connect and execute a simple query
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # ✅ Wrapped in text()
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

