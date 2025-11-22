from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    STRUCTURED = "structured"
    ANALYZED = "analyzed"
    SYNTHESIZED = "synthesized"
    COMPLETED = "completed"
    FAILED = "failed"

class Project(BaseModel):
    id: str
    name: str
    status: ProjectStatus = ProjectStatus.DRAFT
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    # Paths to data files
    book_path: Optional[str] = None # Path to book.json
    audio_dir: Optional[str] = None # Path to output audio
