import uuid
from fastapi import Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import db, db_admin
import jwt
import os

security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        # Verify token with db
        user = db.auth.get_user(token)

        if user.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return user.user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def admin_required(user=Depends(get_current_user)):
    if not user.user_metadata.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# converting images to urls

# def upload_image(file: UploadFile, folder: str = "uploads") -> str:
#     try:
#         # Generate unique filename
#         file_ext = file.filename.split(".")[-1]
#         unique_filename = f"{folder}/{uuid.uuid4()}.{file_ext}"

#         # Upload to db bucket
#         res = db.storage.from_("images").upload(
#             unique_filename,
#             file.file,
#             {"content-type": file.content_type}
#         )

#         if res.get("error"):
#             raise HTTPException(status_code=400, detail=res["error"]["message"])

#         # Get public URL
#         url = db.storage.from_("images").get_public_url(unique_filename)
#         return url

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

async def upload_image(file: UploadFile, folder: str, user_id: str) -> str:
    """
    Upload an image to Supabase Storage and return its public URL.
    """
    try:
        # 1. Read file content asynchronously
        file_bytes = await file.read()
        content_type = file.content_type

        # 2. Determine extension
        ext_map = {
            "image/jpeg": ".jpeg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }
        ext = ext_map.get(content_type, ".jpg")

        # 3. Unique filename
        filename = f"{uuid.uuid4()}{ext}"
        file_path = f"{folder}/{user_id}/{filename}"  # folder/user_id/filename

        # 4. Upload synchronously (remove await!)
        upload_response = db_admin.storage.from_("images").upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": content_type}
        )

        if not upload_response:
            raise HTTPException(status_code=500, detail="Failed to upload image to Supabase.")

        # 5. Get public URL
        public_url = db_admin.storage.from_("images").get_public_url(file_path)

        if not public_url:
            raise HTTPException(status_code=500, detail="Failed to retrieve public URL for uploaded image.")
        return public_url

    except Exception as e:
        print(f"Error during image upload: {e}")
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
    
