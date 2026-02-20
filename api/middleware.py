from fastapi import Request, HTTPException, status, Depends
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

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# ============================================
# OPTIONAL AUTHENTICATION
# ============================================

def get_current_user_optional(request: Request) -> Optional[dict]:
    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.replace("Bearer ", "")

        payload = decode_access_token(token)
        return payload

    except Exception:
        return None


# ============================================
# ROLE-BASED ACCESS CONTROL
# ============================================


# ============================================
# ROLE-BASED ACCESS CONTROL
# ============================================

def require_role(allowed_roles: list):
    """
    Allows access only if user's role is in allowed_roles list.
    
    Example:
        Depends(require_role(["admin", "analyst"]))
    """

    def role_checker(user: dict = Depends(get_current_user)):
        user_role = user.get("role")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Allowed roles: {allowed_roles}"
            )

        return user

    return role_checker
