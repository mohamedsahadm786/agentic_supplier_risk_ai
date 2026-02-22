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

    # -------------------------------------------------------
    # Check if token has been blacklisted (user logged out)
    # -------------------------------------------------------
    from .services.rate_limiter import is_token_blacklisted
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

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

# ============================================
# RATE LIMITING DEPENDENCY
# ============================================

from fastapi import Request
from fastapi.responses import JSONResponse
from .services.rate_limiter import check_rate_limit

def rate_limit_evaluation(current_user: dict = Depends(get_current_user)):
    """
    Rate limiting dependency for evaluation endpoint.

    Allows maximum 10 evaluation requests per user per 60 seconds.

    If exceeded:
        Returns HTTP 429 Too Many Requests
        Tells user how many seconds to wait

    Usage in route:
        Depends(rate_limit_evaluation)
    """
    user_id = current_user.get("user_id")

    result = check_rate_limit(
        user_id=str(user_id),
        endpoint="evaluations",
        max_requests=10,
        window_seconds=60
    )

    if not result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": f"You have made too many evaluation requests. Maximum is 10 per minute.",
                "retry_after_seconds": result["retry_after"],
                "current_count": result["current_count"],
                "max_requests": result["max_requests"]
            }
        )

    return current_user
