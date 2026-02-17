"""
AUTHENTICATION & SECURITY FUNCTIONS

This file handles:
1. Password hashing (converting passwords into unreadable strings)
2. Password verification (checking if entered password matches stored hash)
3. JWT token generation (creating digital "ID cards" for logged-in users)
4. JWT token verification (checking if a token is valid)

SECURITY NOTE: We NEVER store plain-text passwords in the database!
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================

# Secret key for signing JWT tokens (like a signature that can't be forged)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"  # Encryption algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing configuration
# bcrypt is a one-way encryption algorithm (can't be reversed)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================
# PASSWORD HASHING FUNCTIONS
# ============================================

def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a hashed (encrypted) version.
    
    Example:
    Input:  "MyPassword123!"
    Output: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ND0dalKa8u3y"
    
    Why: If a hacker steals our database, they can't read the actual passwords!
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if a plain-text password matches the stored hash.
    
    Example:
    verify_password("MyPassword123!", "$2b$12$LQv3c1yqB...") → True
    verify_password("WrongPassword", "$2b$12$LQv3c1yqB...") → False
    
    This is how we check login credentials without storing the actual password!
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# JWT TOKEN FUNCTIONS
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token (like a digital ID card) for a logged-in user.
    
    The token contains:
    - User ID
    - Email
    - Company ID
    - Expiration time
    
    Example token (encoded):
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    
    The user's browser stores this token and sends it with every request.
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Create and return the encoded token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode a JWT token to extract user information.
    
    This is called on every API request to verify the user is logged in.
    
    Returns:
    - User data (if token is valid)
    - None (if token is expired or invalid)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================
# HELPER FUNCTION FOR EXTRACTING USER FROM TOKEN
# ============================================

def get_current_user_id(token: str) -> Optional[int]:
    """
    Extract the user ID from a JWT token.
    
    Example:
    Token contains: {"user_id": 123, "email": "user@company.com", ...}
    Returns: 123
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("user_id")
    return None