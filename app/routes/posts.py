from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
from app.config import db
from app.dependencies import get_current_user, upload_image

router = APIRouter(prefix="/posts", tags=["posts"])


# SCHEMAS


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    category_id: Optional[str] = None


# PUBLIC ENDPOINTS

@router.get("/")
def get_all_posts():
    """
    Get all posts (public).
    """
    response = db.table("posts").select(
        "*, categories(name), profiles(username, image_url)"
    ).order("created_at", desc=True).execute()

    return {'message': "success", "res": response.data}


@router.get("/{post_id}")
def get_post(post_id: str):
    """
    Get a single post by ID (public).
    """
    response = db.table("posts").select(
        "*, categories(name), profiles(username, image_url)"
    ).eq("id", post_id).single().execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Post not found")

    return {'message': "success", "res": response.data}


# get posts by user id
@router.get("/all/{author_id}")
def get_posts_by_author(author_id: str):
    try:
        response = (
            db.table("posts")
            .select("id, title, content, cover_image_url, created_at, profiles(username, image_url)")
            .eq("author_id", author_id)
            .order("created_at", desc=True)
            .execute()
        )

        return {
            "count": len(response.data),
            "posts": response.data,
            "message": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# PRIVATE ENDPOINTS


@router.post("/")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    category_id: str = Form(None),
    file: UploadFile = File(None),
    user=Depends(get_current_user),
):
    cover_image_url = None
    if file:
        cover_image_url = await upload_image(file, folder=f"posts", user_id=user.id)

    data = {
        "title": title,
        "content": content,
        "cover_image_url": cover_image_url,
        "category_id": category_id,
        "author_id": user.id,
    }

    response = db.table("posts").insert(data).execute()

    if not response.data:
        raise HTTPException(status_code=400, detail="Post creation failed")

    return {"message": "success", "res": response.data[0]}


@router.put("/{post_id}")
def update_post(post_id: str, post: PostUpdate, user=Depends(get_current_user), file: UploadFile = File(None)):

    existing = db.table("posts").select("author_id").eq(
        "id", post_id).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Post not found")

    if existing.data["author_id"] != user.id:
        raise HTTPException(
            status_code=403, detail="Not allowed to edit this post")

    update_data = {k: v for k, v in post.dict().items() if v is not None}

    if file:
        image_url = upload_image(file, folder=f"posts/{user.id}")
        update_data["cover_image_url"] = image_url

    response = db.table("posts").update(
        update_data).eq("id", post_id).execute()
    return {'message': "success", "res": response.data[0]} if response.data else {"message": "No changes"}


@router.delete("/{post_id}")
def delete_post(post_id: str, user=Depends(get_current_user)):
    """
    Delete a post (only by author).
    """
    existing = db.table("posts").select("author_id").eq(
        "id", post_id).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Post not found")

    if existing.data["author_id"] != user.id:
        raise HTTPException(
            status_code=403, detail="Not allowed to delete this post")

    db.table("posts").delete().eq("id", post_id).execute()
    return {"message": "Post deleted successfully"}
