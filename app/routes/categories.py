from fastapi import APIRouter, Depends, HTTPException
from app.config import db
from app.dependencies import admin_required

router = APIRouter()


# GET all categories (public)

@router.get("/categories")
def get_categories():
    response = db.table("categories").select("*").order("created_at").execute()
    return {"categories": response.data}


# CREATE category (admin only)

@router.post("/categories")
def create_category(name: str, user=Depends(admin_required)):
    # Simple check: only admins can create
    if not user.user_metadata.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")

    response = db.table("categories").insert({"name": name}).execute()
    return {"message": "Category created", "category": response.data}


# UPDATE category (admin only)

@router.put("/categories/{category_id}")
def update_category(category_id: str, name: str, user=Depends(admin_required)):
    if not user.user_metadata.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")

    response = db.table("categories").update(
        {"name": name}).eq("id", category_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category updated", "category": response.data}


# DELETE category (admin only)

@router.delete("/categories/{category_id}")
def delete_category(category_id: str, user=Depends(admin_required)):
    if not user.user_metadata.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")

    response = db.table("categories").delete().eq("id", category_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}


# category feed selection endpoint

@router.get("/feed")
def get_feed(category_id: str | None = None):
    query = db.table("posts").select(
        "*, profiles(username, image_url), categories(name)"
    ).order("created_at", desc=True)

    if category_id:
        query = query.eq("category_id", category_id)

    response = query.execute()
    return {"posts": response.data}
