# app/main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}
