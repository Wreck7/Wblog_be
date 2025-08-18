from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from app.config import db
from app.dependencies import get_current_user

router = APIRouter()

# MODELS


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    gender: Optional[str] = None
    phone: Optional[str] = None
    image_url: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# SIGNUP (auto login + profile)
@router.post("/signup")
def signup(data: SignupRequest):
    response = db.auth.sign_up({
        "email": data.email,
        "password": data.password
    })

    if not response.user:
        raise HTTPException(status_code=400, detail="Signup failed")

    user = response.user
    session = response.session

    # create profile in "profiles" with extra fields
    db.table("profiles").insert({
        "id": user.id,
        "username": data.username,
        "gender": data.gender,
        "image_url": data.image_url,
        "phone": data.phone
    }).execute()

    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": data.username,
            "image_url": data.image_url,
            "gender": data.gender,
            "phone": data.phone
        }
    }


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


# LOGOUT
@router.post("/logout")
def logout(user=Depends(get_current_user)):
    db.auth.sign_out()
    return {"message": "Logged out successfully"}
