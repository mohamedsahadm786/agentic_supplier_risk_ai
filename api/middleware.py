"""
AUTHENTICATION MIDDLEWARE

This file creates a "middleware" - a function that runs BEFORE every API request.
Think of it like a security guard at a building entrance who checks everyone's ID.

How it works:
1. User makes request to API (e.g., GET /suppliers)
2. Middleware intercepts the request
3. Checks if Authorization header contains valid JWT token
4. If valid → Allow request to continue
5. If invalid → Return 401 Unauthorized error
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from .auth import decode_access_token

# ============================================
# JWT BEARER SECURITY SCHEME
# ============================================

security = HTTPBearer()


# ============================================
# AUTHENTICATION DEPENDENCY
# ============================================

def get_current_user(credentials: HTTPAuthorizationCredentials = security):
    """
    Dependency function that extracts and validates JWT token.
    
    How it's used in FastAPI:
    @app.get("/protected-route")
    def protected_route(user = Depends(get_current_user)):
        return {"message": f"Hello user {user['user_id']}!"}
    
    If the token is invalid, this function raises an HTTPException
    and the user gets a 401 Unauthorized response.
    
    Args:
        credentials: Automatically extracted from Authorization header
    
    Returns:
        User data (dict with user_id, email, company_id)
    
    Raises:
        HTTPException 401 if token is invalid or expired
    """
    token = credentials.credentials
    
    # Decode the token
    payload = decode_access_token(token)
    
    # If decoding failed (expired or invalid token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


# ============================================
# OPTIONAL AUTHENTICATION (FOR PUBLIC ROUTES)
# ============================================

def get_current_user_optional(request: Request) -> Optional[dict]:
    """
    Extract user from token if present, but don't require it.
    
    Use this for routes that can work with OR without authentication.
    Example: A public blog post list that shows "Edit" button only to logged-in users.
    
    Returns:
        User data if token is valid, None if no token or invalid token
    """
    try:
        # Try to extract Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        # Extract token (remove "Bearer " prefix)
        token = auth_header.replace("Bearer ", "")
        
        # Decode token
        payload = decode_access_token(token)
        return payload
        
    except Exception:
        return None


# ============================================
# ROLE-BASED ACCESS CONTROL (FUTURE USE)
# ============================================

def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    
    Future enhancement - restrict routes to specific user roles.
    
    Example usage:
    @app.delete("/admin/users/{user_id}")
    def delete_user(user = Depends(require_role("admin"))):
        # Only users with role="admin" can access this
        pass
    
    Args:
        required_role: The role required (e.g., "admin", "manager", "viewer")
    
    Returns:
        A dependency function that checks user role
    """
    def role_checker(user: dict = Depends(get_current_user)):
        user_role = user.get("role", "user")
        
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires '{required_role}' role"
            )
        
        return user
    
    return role_checker