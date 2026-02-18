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

def require_role(required_role: str):
    def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires '{required_role}' role"
            )
        return user

    return role_checker