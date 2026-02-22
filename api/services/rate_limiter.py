"""
REDIS RATE LIMITER SERVICE

Purpose:
    Prevents API abuse by limiting how many evaluation requests
    a single user can make within a 60-second window.

How it works:
    1. User makes a request
    2. We check Redis: "How many times has this user called this in last 60 seconds?"
    3. If count < limit → allow + increment counter
    4. If count >= limit → block with HTTP 429 (Too Many Requests)

Redis Key Format:
    rate_limit:{user_id}:{endpoint_name}
    Example: rate_limit:abc-123:evaluations

TTL (Time To Live):
    60 seconds — Redis auto-deletes the key after 60 seconds
    This means the counter resets every minute automatically
"""

import redis
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONNECT TO REDIS
# ============================================

def get_redis_client():
    """
    Creates and returns a Redis connection.
    Uses your existing .env configuration.
    """
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        password=os.getenv("REDIS_PASSWORD", None),
        db=int(os.getenv("REDIS_DB", 0)),
        decode_responses=True  # Returns strings instead of bytes
    )


# ============================================
# CORE RATE LIMIT CHECK FUNCTION
# ============================================

def check_rate_limit(user_id: str, endpoint: str, max_requests: int = 10, window_seconds: int = 60) -> dict:
    """
    Checks if a user has exceeded their rate limit.

    Parameters:
        user_id       : The ID of the user making the request
        endpoint      : Name of the endpoint (e.g., "evaluations")
        max_requests  : Maximum allowed requests in the time window (default: 10)
        window_seconds: Time window in seconds (default: 60 seconds = 1 minute)

    Returns a dict:
        {
            "allowed": True or False,
            "current_count": 7,
            "max_requests": 10,
            "remaining": 3,
            "retry_after": 0   (seconds to wait if blocked)
        }
    """

    try:
        r = get_redis_client()

        # Build the unique Redis key for this user + endpoint
        # Example key: "rate_limit:abc-123:evaluations"
        redis_key = f"rate_limit:{user_id}:{endpoint}"

        # Get current count from Redis
        # If key doesn't exist yet, Redis returns None
        current_count_str = r.get(redis_key)
        current_count = int(current_count_str) if current_count_str else 0

        if current_count >= max_requests:
            # User has exceeded the limit
            # Check how many seconds are left before the key expires
            ttl = r.ttl(redis_key)
            retry_after = ttl if ttl > 0 else window_seconds

            return {
                "allowed": False,
                "current_count": current_count,
                "max_requests": max_requests,
                "remaining": 0,
                "retry_after": retry_after
            }

        # User is within limit — increment the counter
        # INCR command: if key doesn't exist, Redis creates it starting at 1
        new_count = r.incr(redis_key)

        # If this is the FIRST request (count just became 1),
        # set the expiry timer so Redis auto-deletes after 60 seconds
        if new_count == 1:
            r.expire(redis_key, window_seconds)

        return {
            "allowed": True,
            "current_count": new_count,
            "max_requests": max_requests,
            "remaining": max_requests - new_count,
            "retry_after": 0
        }

    except redis.ConnectionError:
        # If Redis is down, we ALLOW the request
        # (don't block users just because Redis is temporarily down)
        print("⚠️ WARNING: Redis connection failed. Rate limiting disabled temporarily.")
        return {
            "allowed": True,
            "current_count": 0,
            "max_requests": max_requests,
            "remaining": max_requests,
            "retry_after": 0
        }

    except Exception as e:
        # Any other error — allow request (fail open, not fail closed)
        print(f"⚠️ WARNING: Rate limiter error: {e}. Allowing request.")
        return {
            "allowed": True,
            "current_count": 0,
            "max_requests": max_requests,
            "remaining": max_requests,
            "retry_after": 0
        }

# ============================================
# TOKEN BLACKLIST FUNCTIONS (FOR LOGOUT)
# ============================================

def blacklist_token(token: str, expires_in_seconds: int = 86400):
    """
    Adds a JWT token to the Redis blacklist.
    
    When user logs out, their token is stored here.
    Any future request with this token will be rejected.
    
    Parameters:
        token            : The JWT token string to blacklist
        expires_in_seconds: How long to keep in blacklist (default: 24 hours = 86400 seconds)
                           Should match your JWT expiry time
    """
    try:
        r = get_redis_client()
        # Store token with prefix "blacklist:"
        # Value is "1" (we only care that the key exists, not the value)
        # Redis auto-deletes after expires_in_seconds
        redis_key = f"blacklist:{token}"
        r.setex(redis_key, expires_in_seconds, "1")
        return True
    except Exception as e:
        print(f"⚠️ WARNING: Could not blacklist token: {e}")
        return False


def is_token_blacklisted(token: str) -> bool:
    """
    Checks if a JWT token has been blacklisted (i.e., user logged out).
    
    Returns:
        True  → Token is blacklisted (reject the request)
        False → Token is valid (allow the request)
    """
    try:
        r = get_redis_client()
        redis_key = f"blacklist:{token}"
        # EXISTS returns 1 if key exists, 0 if not
        return r.exists(redis_key) == 1
    except Exception as e:
        print(f"⚠️ WARNING: Could not check token blacklist: {e}")
        # If Redis is down, allow the request (fail open)
        return False