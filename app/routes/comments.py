from fastapi import APIRouter, Depends, HTTPException, Body
from app.config import db

from app.dependencies import get_current_user

router = APIRouter()

# GET comments on a post (public)


@router.get("/posts/{post_id}/comments")
def get_comments(post_id: str):
    response = db.table("comments").select(
        "*, profiles(username, image_url)"
    ).eq("post_id", post_id).order("created_at", desc=True).execute()
    return {'message': "success", "res": response.data}

# ADD comment (auth)


@router.post("/posts/{post_id}/comments")
def add_comment(post_id: str, body: dict = Body(...), user=Depends(get_current_user)):
    response = db.table("comments").insert({
        "post_id": post_id,
        "author_id": user.id,
        "content": body["content"]
    }).execute()
    return {'message': "success", "res": response.data}

# DELETE comment (auth + ownership)


@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: str, user=Depends(get_current_user)):
    comment = db.table("comments").select(
        "*").eq("id", comment_id).single().execute()
    if not comment.data:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.data["author_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not your comment")

    db.table("comments").delete().eq("id", comment_id).execute()
    return {"message": "Comment deleted"}

# update comment (auth + ownership)


@router.put("/comments/{comment_id}")
def update_comment(comment_id: str, body: dict = Body(...), user=Depends(get_current_user)):
    # Check if comment exists
    comment = db.table("comments").select(
        "*").eq("id", comment_id).single().execute()
    if not comment.data:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Ensure ownership
    if comment.data["author_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not your comment")

    # Update comment
    response = db.table("comments").update({
        "content": body["content"]
    }).eq("id", comment_id).execute()

    return {'message': "success", "res": response.data}
