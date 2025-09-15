from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List, Optional
from pydantic import BaseModel
from app.config import db
from app.dependencies import get_current_user, upload_image
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/posts", tags=["posts"])




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
    # return JSONResponse({'message': "success", "res": response.data}, status_code=status.HTTP_200_OK)


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
async def update_post(
    post_id: str,
    title: str = Form(None),
    content: str = Form(None),
    category_id: str = Form(None),
    file: UploadFile = File(None),
    user=Depends(get_current_user),
):
    # Check if post exists
    existing = db.table("posts").select("author_id").eq(
        "id", post_id).single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Post not found")

    # Only author can update
    if existing.data["author_id"] != user.id:
        raise HTTPException(
            status_code=403, detail="Not allowed to edit this post")

    # Collect update data
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if content is not None:
        update_data["content"] = content
    if category_id is not None:
        update_data["category_id"] = category_id

    # Handle file upload if provided
    if file:
        cover_image_url = await upload_image(file, folder=f"posts", user_id=user.id)
        update_data["cover_image_url"] = cover_image_url

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Update DB
    response = db.table("posts").update(
        update_data).eq("id", post_id).execute()

    if not response.data:
        raise HTTPException(status_code=400, detail="Post update failed")

    return {"message": "success", "res": response.data[0]}


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
