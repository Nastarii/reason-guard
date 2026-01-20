from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import httpx
import hashlib
from jose import jwt, JWTError
from jose.exceptions import JWKError
import json

from app.database import get_db
from app.config import get_settings
from app.models.user import User
from app.models.api_token import ApiToken
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

# Cache for Clerk JWKS
_jwks_cache = {"keys": None, "fetched_at": None}


def hash_token(token: str) -> str:
    """Hash a token for comparison."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_api_token_sync(token: str, db: Session) -> Optional[User]:
    """Verify a ReasonGuard API token and return the user."""
    token_hash = hash_token(token)

    api_token = (
        db.query(ApiToken)
        .filter(ApiToken.token_hash == token_hash, ApiToken.is_active == True)
        .first()
    )

    if not api_token:
        return None

    # Check if token is expired
    if api_token.expires_at and api_token.expires_at < datetime.utcnow():
        return None

    # Update last used timestamp
    api_token.last_used_at = datetime.utcnow()
    db.commit()

    return api_token.user


async def get_clerk_jwks() -> dict:
    """Fetch and cache Clerk's JWKS (JSON Web Key Set)."""
    import time

    # Cache for 1 hour
    cache_duration = 3600
    current_time = time.time()

    if (
        _jwks_cache["keys"] is not None
        and _jwks_cache["fetched_at"] is not None
        and current_time - _jwks_cache["fetched_at"] < cache_duration
    ):
        return _jwks_cache["keys"]

    # Extract the Clerk frontend API domain from publishable key
    # Format: pk_test_<base64> or pk_live_<base64>
    if not settings.clerk_publishable_key:
        raise HTTPException(status_code=500, detail="Clerk publishable key not configured")

    try:
        # The publishable key contains the frontend API URL encoded
        import base64
        key_parts = settings.clerk_publishable_key.split("_")
        if len(key_parts) >= 3:
            encoded_domain = key_parts[2]
            # Add padding if necessary
            padding = 4 - len(encoded_domain) % 4
            if padding != 4:
                encoded_domain += "=" * padding
            frontend_api = base64.b64decode(encoded_domain).decode("utf-8").rstrip("$")
        else:
            raise ValueError("Invalid publishable key format")
    except Exception:
        # Fallback: try to use the secret key to determine the instance
        frontend_api = None

    # Try to fetch JWKS from the Clerk instance
    jwks_urls = []
    if frontend_api:
        jwks_urls.append(f"https://{frontend_api}/.well-known/jwks.json")

    async with httpx.AsyncClient() as client:
        for jwks_url in jwks_urls:
            try:
                response = await client.get(jwks_url)
                if response.status_code == 200:
                    _jwks_cache["keys"] = response.json()
                    _jwks_cache["fetched_at"] = current_time
                    return _jwks_cache["keys"]
            except Exception:
                continue

    raise HTTPException(status_code=500, detail="Failed to fetch Clerk JWKS")


async def verify_clerk_jwt(token: str) -> dict:
    """Verify a Clerk JWT token and return the claims."""
    try:
        # Get the unverified header to find the key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise HTTPException(status_code=401, detail="Token missing key ID")

        # Fetch JWKS
        jwks = await get_clerk_jwks()

        # Find the matching key
        rsa_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = key
                break

        if not rsa_key:
            # Key not found, try refreshing the cache
            _jwks_cache["keys"] = None
            _jwks_cache["fetched_at"] = None
            jwks = await get_clerk_jwks()

            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    rsa_key = key
                    break

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")

        # Verify the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={
                "verify_aud": False,  # Clerk tokens may not have aud
                "verify_iss": False,  # We'll verify issuer manually if needed
            }
        )

        # Extract user ID from 'sub' claim
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing user ID")

        return {"user_id": user_id, "claims": payload}

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except JWKError as e:
        raise HTTPException(status_code=401, detail=f"Key error: {str(e)}")


async def verify_token(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """Verify authorization token - supports both Clerk JWT and ReasonGuard API tokens."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization[7:]

    # Check if it's a ReasonGuard API token (starts with "rg_")
    if token.startswith("rg_"):
        user = verify_api_token_sync(token, db)
        if user:
            return {"user": user, "auth_type": "api_token"}
        raise HTTPException(status_code=401, detail="Invalid or expired API token")

    # Otherwise, treat as Clerk JWT token
    if not settings.clerk_publishable_key:
        # Development mode - accept any token and extract user_id from JWT if possible
        try:
            unverified = jwt.get_unverified_claims(token)
            user_id = unverified.get("sub", "dev-user")
        except Exception:
            user_id = "dev-user"
        return {"user_id": user_id, "auth_type": "clerk"}

    try:
        # Verify the JWT token properly
        result = await verify_clerk_jwt(token)
        return {"user_id": result["user_id"], "auth_type": "clerk", "claims": result.get("claims")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


# Keep the old function for backward compatibility
async def verify_clerk_token(authorization: Optional[str] = Header(None)) -> dict:
    """Verify Clerk JWT token and return user claims."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization[7:]

    if not settings.clerk_publishable_key:
        # Development mode
        try:
            unverified = jwt.get_unverified_claims(token)
            user_id = unverified.get("sub", "dev-user")
        except Exception:
            user_id = "dev-user"
        return {"user_id": user_id}

    try:
        result = await verify_clerk_jwt(token)
        return {"user_id": result["user_id"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


async def get_current_user(
    db: Session = Depends(get_db),
    auth_data: dict = Depends(verify_token),
) -> User:
    """Get user from token (supports both Clerk and API tokens)."""
    # If user was already resolved (API token auth)
    if auth_data.get("auth_type") == "api_token":
        return auth_data["user"]

    # Clerk token auth - get or create user
    clerk_user_id = auth_data.get("user_id")

    user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()

    if not user:
        # Create user if doesn't exist
        user = User(
            clerk_user_id=clerk_user_id,
            email=f"{clerk_user_id}@placeholder.com",  # Will be updated from Clerk
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


@router.post("/webhook/clerk", include_in_schema=False)
async def clerk_webhook(payload: dict, db: Session = Depends(get_db)):
    """Handle Clerk webhook events for user sync."""
    event_type = payload.get("type")
    data = payload.get("data", {})

    if event_type == "user.created":
        clerk_user_id = data.get("id")
        email = data.get("email_addresses", [{}])[0].get("email_address", "")
        full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()

        existing_user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
        if not existing_user:
            user = User(
                clerk_user_id=clerk_user_id,
                email=email,
                full_name=full_name or None,
            )
            db.add(user)
            db.commit()

    elif event_type == "user.updated":
        clerk_user_id = data.get("id")
        user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
        if user:
            email = data.get("email_addresses", [{}])[0].get("email_address", "")
            full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
            user.email = email
            user.full_name = full_name or None
            db.commit()

    elif event_type == "user.deleted":
        clerk_user_id = data.get("id")
        user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
        if user:
            user.is_active = False
            db.commit()

    return {"status": "ok"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user
