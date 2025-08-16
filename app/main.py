from fastapi import FastAPI
from app.config import db

from app.routes import auth
from app.routes import posts
from app.routes import comments

app = FastAPI(title="Blogging API")

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)

@app.get("/")
def root():
    return {"message": "Blog API is running!"}
