from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Sentence(BaseModel):
    id: str
    text: str
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Analysis results
    is_noise: bool = False
    speaker: Optional[str] = None
    emotion_vector: Optional[List[float]] = None
    audio_path: Optional[str] = None

class Chapter(BaseModel):
    id: str
    title: str
    sentences: List[Sentence] = Field(default_factory=list)
    audio_path: Optional[str] = None
    duration: float = 0.0

class Book(BaseModel):
    id: str
    title: str
    author: Optional[str] = None
    chapters: List[Chapter] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "UPLOADED" # UPLOADED, PARSING, CLEANING, SYNTHESIZING, COMPLETED, FAILED
