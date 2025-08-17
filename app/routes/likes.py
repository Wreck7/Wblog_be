from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.config import db

router = APIRouter()

# =============================
# GET all likes on a post (public)
# =============================


@router.get("/posts/{post_id}/likes")
def get_likes(post_id: str):
    response = db.table("likes").select(
        "id, author_id").eq("post_id", post_id).execute()
    return {
        "count": len(response.data),
        "res": response.data,
        'message': "success"
    }

# =============================
# ADD like (auth required)
# =============================


@router.post("/posts/{post_id}/likes")
def add_like(post_id: str, user=Depends(get_current_user)):
    # Check if already liked
    existing = db.table("likes").select("*").eq("post_id",
                                                post_id).eq("author_id", user.id).execute()
    if existing.data:
        raise HTTPException(
            status_code=400, detail="You already liked this post")

    response = db.table("likes").insert({
        "post_id": post_id,
        "author_id": user.id
    }).execute()
    return {'message': "success", "res": response.data}

# =============================
# REMOVE like (auth required)
# =============================


@router.delete("/posts/{post_id}/likes")
def remove_like(post_id: str, user=Depends(get_current_user)):
    # Check if like exists
    existing = db.table("likes").select("*").eq("post_id",
                                                post_id).eq("author_id", user.id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Like not found")

    db.table("likes").delete().eq("post_id", post_id).eq(
        "author_id", user.id).execute()
    return {"message": "Like removed"}
