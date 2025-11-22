from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.projects import router as project_router

from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Novel-to-Audio Tool")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
os.makedirs("backend/data", exist_ok=True)
app.mount("/static", StaticFiles(directory="backend/data"), name="static")

# Include Routers
app.include_router(project_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
