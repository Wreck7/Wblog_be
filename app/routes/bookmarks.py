from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.config import db

router = APIRouter()


# GET all bookmarks of current user (auth required)


@router.get("/bookmarks")
def get_bookmarks(user=Depends(get_current_user)):
    response = db.table("bookmarks").select(
        "id, post_id, posts(id, title, content, created_at, author_id, profiles(username, image_url))"
    ).eq("user_id", user.id).execute()

    return {
        "count": len(response.data),
        "bookmarks": response.data,
        "message": "success"
    }


# ADD a bookmark (auth required)


@router.post("/posts/{post_id}/bookmark")
def add_bookmark(post_id: str, user=Depends(get_current_user)):
    # Check if already bookmarked
    existing = db.table("bookmarks").select(
        "*").eq("post_id", post_id).eq("user_id", user.id).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Post already bookmarked")

    response = db.table("bookmarks").insert({
        "post_id": post_id,
        "user_id": user.id
    }).execute()

    return {"message": "Post bookmarked", "res": response.data}


# REMOVE a bookmark (auth required)


@router.delete("/posts/{post_id}/bookmark")
def remove_bookmark(post_id: str, user=Depends(get_current_user)):
    existing = db.table("bookmarks").select(
        "*").eq("post_id", post_id).eq("user_id", user.id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    db.table("bookmarks").delete().eq(
        "post_id", post_id).eq("user_id", user.id).execute()
    return {"message": "Bookmark removed"}


# CHECK if a post is bookmarked (auth required)

@router.get("/posts/{post_id}/is-bookmarked")
def is_bookmarked(post_id: str, user=Depends(get_current_user)):
    response = db.table("bookmarks").select("id").eq(
        "post_id", post_id).eq("user_id", user.id).execute()
    return {
        "bookmarked": bool(response.data),
        "message": "success"
    }
