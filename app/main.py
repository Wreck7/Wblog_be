from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from app.config import db
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth
from app.routes import posts
from app.routes import comments
from app.routes import likes
from app.routes import follows
from app.routes import bookmarks
from app.routes import categories
from app.routes import profiles
from app.routes import signs

app = FastAPI(title="Blogging API", default_response_class=ORJSONResponse)

origins = [
    "http://localhost:5173",  # Vite
    "http://localhost:3000",  # CRA
    "http://127.0.0.1:5173",
    "https://your-frontend-domain.com",  # production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],    # or specify ["GET", "POST"]
    allow_headers=["*"],    # or specify ["Authorization", "Content-Type"]
)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(follows.router)
app.include_router(bookmarks.router)
app.include_router(categories.router)
app.include_router(profiles.router)
app.include_router(signs.router)

@app.get("/")
def root():
    return {"message": "Blog API is running!"}
