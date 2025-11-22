import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.models.project import Project, ProjectStatus
from app.models.book import Book
from app.services.project.manager import ProjectManager

router = APIRouter(prefix="/api/projects", tags=["projects"])
manager = ProjectManager()

@router.get("", response_model=List[Project])
async def list_projects():
    return manager.list_projects()

@router.post("", response_model=Project)
async def create_project(file: UploadFile = File(...)):
    # Save temp file
    temp_dir = "backend/data/temp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        project = manager.create_project(temp_path, file.filename)
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/{project_id}/content", response_model=Book)
async def get_project_content(project_id: str):
    book = manager.get_book_content(project_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book content not found")
    return book

@router.put("/{project_id}/content", response_model=Project)
async def update_project_content(project_id: str, book: Book):
    try:
        return manager.update_book_content(project_id, book)
    except ValueError:
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/analyze", response_model=Project)
async def analyze_project(project_id: str, background_tasks: BackgroundTasks):
    try:
        # For MVP, we run inline or background? 
        # User wants "Human-in-the-loop", so we should probably await it or use WebSocket.
        # For now, let's await it to return the updated state immediately for the UI to refresh.
        # Warning: This might timeout for large books.
        return await manager.analyze_project(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/synthesize", response_model=Project)
async def synthesize_project(project_id: str, background_tasks: BackgroundTasks):
    try:
        # Synthesis takes long, so background task is better.
        # But for MVP simplicity and "Step-by-step" confirmation, let's use background 
        # and frontend polls status.
        background_tasks.add_task(manager.synthesize_project, project_id)
        return manager.update_project_status(project_id, ProjectStatus.SYNTHESIZED)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
