from fastapi import Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import uuid4
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

def upload_image(file: UploadFile, folder: str = "profiles"):
    try:
        # Read file bytes
        file_bytes = file.file.read()

        # Unique filename
        ext = os.path.splitext(file.filename)[-1] or ".jpg"
        filename = f"{uuid4()}{ext}"
        file_path = f"{folder}/{filename}"

        # Upload using service role client
        res = db_admin.storage.from_("images").upload(
            file_path,
            file_bytes,
            {"content-type": file.content_type}
        )

        # If upload failed, res.error will have info
        if res.error:
            raise HTTPException(status_code=400, detail=f"Upload failed: {res.error.message}")

        # Return public URL
        url = db_admin.storage.from_("images").get_public_url(file_path)
        return url

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")
