from fastapi import APIRouter, Depends, HTTPException, Body
from app.config import db
from app.dependencies import get_current_user

router = APIRouter()


# GET a user profile (public)

@router.get("/profiles/{user_id}")
def get_profile(user_id: str):
    response = db.table("profiles").select(
        "*").eq("id", user_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "success", "res": response.data}


# GET my own profile (auth)

@router.get("/profile/me")
def get_my_profile(user=Depends(get_current_user)):
    response = db.table("profiles").select(
        "*").eq("id", user.id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "success", "res": response.data}


# UPDATE my profile (auth)

@router.put("/profile/me")
def update_profile(
    body: dict = Body(...),
    user=Depends(get_current_user)
):
    update_data = {}
    if "username" in body:
        update_data["username"] = body["username"]
    if "bio" in body:
        update_data["bio"] = body["bio"]
    if "image_url" in body:
        update_data["image_url"] = body["image_url"]

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    response = db.table("profiles").update(
        update_data).eq("id", user.id).execute()
    return {"message": "Profile updated", "res": response.data}
