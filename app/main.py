from fastapi import FastAPI
from app.config import db
from app.routes import auth

app = FastAPI(title="Blogging API")

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Blog API is running!"}
