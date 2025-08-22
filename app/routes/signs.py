
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

from supabase import AuthApiError
from app.config import db, db_admin
from app.dependencies import get_current_user, upload_image

router = APIRouter(prefix="/auth", tags=["auth"])

# MODELS


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    gender: Optional[str] = None
    # image_url: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# @router.post("/signup")
# def signup(data: SignupRequest, file: UploadFile = File(None)):
#     existing_username = db.table("profiles").select(
#         "id").eq("username", data.username).execute()
#     if existing_username.data:
#         raise HTTPException(
#             status_code=400,
#             detail="Username already taken. Please choose another."
#         )
#     try:
#         response = db.auth.sign_up({
#             "email": data.email,
#             "password": data.password
#         })
#     except Exception as e:
#         # db already checks duplicate emails
#         if "User already registered" in str(e):
#             raise HTTPException(
#                 status_code=400, detail="Email already registered. Please login."
#             )
#         raise HTTPException(status_code=400, detail="Signup failed")

#     if not response.user:
#         raise HTTPException(status_code=400, detail="Signup failed")

#     user = response.user
#     session = response.session
#     if not session:
#         raise HTTPException(status_code=400, detail="Signup succeeded, but session not created")
#     image_url = None
#     if file:
#         image_url = upload_image(file, folder=f"profiles/{user.id}")

#     # create profile in "profiles" if not already exists
#     db.table("profiles").upsert({
#         "id": user.id,
#         "username": data.username,
#         "image_url": image_url,
#         "gender": data.gender,
#     }).execute()

#     return {
#         "access_token": session.access_token,
#         "refresh_token": session.refresh_token,
#         "user": {
#             "id": user.id,
#             "email": user.email,
#             "username": data.username,
#             "image_url": image_url,
#             "gender": data.gender
#         }
#     }


# class SignupRequest(BaseModel):
#     email: EmailStr
#     password: str
#     username: str
#     gender: Optional[str] = None


@router.post("/signup")
async def signup(
    email: EmailStr = Form(...),
    password: str = Form(...),
    username: str = Form(...),
    gender: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    # 1. Check if username already exists
    existing_username_res = db.table("profiles").select(
        "id").eq("username", username).execute()
    if existing_username_res.data:
        raise HTTPException(
            status_code=409,  # 409 Conflict is more appropriate
            detail="Username already taken. Please choose another."
        )

    # 2. Register user in Supabase Auth
    new_user = None
    try:
        response = db.auth.sign_up({
            "email": email,
            "password": password
        })
        new_user = response.user
        session = response.session

        if not new_user or not session:
            raise HTTPException(
                status_code=500, detail="Signup failed to create user or session.")

    except AuthApiError as e:
        if "User already registered" in e.message:
            raise HTTPException(
                status_code=409, detail="Email already registered. Please login.")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e.message}")

    # 3. Handle Profile Creation and Image Upload
    image_url = None
    try:
        # Upload image if provided
        if file:
            # Check for valid image content type
            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, detail="Invalid file type. Please upload an image.")

            # The folder is now just "profiles" and the filename is unique
            image_url = await upload_image(
                file, folder="profiles", user_id=new_user.id)

        # Insert profile into the "profiles" table
        db.table("profiles").insert({
            "id": new_user.id,
            "username": username,
            "image_url": image_url,
            "gender": gender,
        }).execute()

        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "username": username,
                "image_url": image_url,
                "gender": gender
            }
        }

    except Exception as e:
        # CLEANUP: If profile creation or image upload fails, delete the created user
        if new_user:
            db_admin.auth.admin.delete_user(new_user.id)

        # Re-raise the exception or raise a new one
        detail = f"Failed to create profile: {str(e)}"
        if isinstance(e, HTTPException):
            detail = e.detail  # Preserve original error message if it's an HTTPException

        raise HTTPException(
            status_code=500,
            detail=detail
        )

# LOGIN


@router.post("/login")
def login(data: LoginRequest):
    response = db.auth.sign_in_with_password({
        "email": data.email,
        "password": data.password
    })

    if not response.session:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    session = response.session
    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "user": {
            "id": session.user.id,
            "email": session.user.email
        }
    }


# REFRESH TOKEN
@router.post("/refresh")
def refresh_token(data: RefreshRequest):
    response = db.auth.refresh_session(data.refresh_token)

    if not response.session:
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    session = response.session
    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "user": {
            "id": session.user.id,
            "email": session.user.email
        }
    }
