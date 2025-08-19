from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import db
import jwt
import os

security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        # Verify token with db
        user = db.auth.get_user(token)

        if user.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return user.user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def admin_required(user=Depends(get_current_user)):
    if not user.user_metadata.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
