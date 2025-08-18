from fastapi import FastAPI
from app.config import db

from app.routes import auth
from app.routes import posts
from app.routes import comments
from app.routes import likes
from app.routes import follows
from app.routes import bookmarks
from app.routes import categories

app = FastAPI(title="Blogging API")

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(follows.router)
app.include_router(bookmarks.router)
app.include_router(categories.router)

@app.get("/")
def root():
    return {"message": "Blog API is running!"}
