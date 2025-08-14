from fastapi import FastAPI
from app.config import db

app = FastAPI(title="Blogging API")

@app.get("/")
def root():
    return {"message": "Blog API is running!"}
