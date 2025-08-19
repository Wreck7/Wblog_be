from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.config import db_admin, db


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {"user": user}


@router.put("/admin/{user_id}")
def make_admin(user_id: str, user=Depends(get_current_user)):
    if not user.user_metadata.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized")

    admin_response = db_admin.auth.admin.update_user_by_id(
        user_id,
        {
            "user_metadata": {
                "is_admin": True
            }
        }
    )
    return {"message": "User promoted to admin", "res": admin_response}
