from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.config import db

router = APIRouter()


# FOLLOW a user (auth required)


@router.post("/users/{user_id}/follow")
def follow_user(user_id: str, user=Depends(get_current_user)):
    if user.id == user_id:
        raise HTTPException(
            status_code=400, detail="You cannot follow yourself")

    # Check if already following
    existing = db.table("follows").select(
        "*").eq("follower_id", user.id).eq("following_id", user_id).execute()
    if existing.data:
        raise HTTPException(
            status_code=400, detail="Already following this user")
    response = db.table("follows").insert({
        "follower_id": user.id,
        "following_id": user_id
    }).execute()
    return {"message": "Followed successfully", "res": response.data}


# UNFOLLOW a user (auth required)


@router.delete("/users/{user_id}/follow")
def unfollow_user(user_id: str, user=Depends(get_current_user)):
    existing = db.table("follows").select(
        "*").eq("follower_id", user.id).eq("following_id", user_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Not following this user")

    db.table("follows").delete().eq("follower_id", user.id).eq(
        "following_id", user_id).execute()
    return {"message": "Unfollowed successfully"}


# GET followers of a user (public)


@router.get("/users/{user_id}/followers")
def get_followers(user_id: str):
    response = db.table("follows").select(
        "follower_id, profiles!follows_follower_id_fkey(username, avatar_url)"
    ).eq("following_id", user_id).execute()
    return {
        "count": len(response.data),
        "followers": response.data,
        "message": "success"
    }


# GET following list of a user (public)


@router.get("/users/{user_id}/following")
def get_following(user_id: str):
    response = db.table("follows").select(
        "following_id, profiles!follows_following_id_fkey(username, avatar_url)"
    ).eq("follower_id", user_id).execute()
    return {
        "count": len(response.data),
        "following": response.data,
        "message": "success"
    }


# CHECK if current user follows someone (auth)


@router.get("/users/{user_id}/is-following")
def is_following(user_id: str, user=Depends(get_current_user)):
    if user.id == user_id:
        return {"is_following": False}

    response = db.table("follows").select(
        "*").eq("follower_id", user.id).eq("following_id", user_id).execute()
    return {"is_following": bool(response.data)}
