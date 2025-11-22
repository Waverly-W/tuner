import os
import json
import uuid
import shutil
from datetime import datetime
from typing import List, Optional
from app.models.project import Project, ProjectStatus
from app.models.book import Book
from app.services.parser.loader import LoaderFactory
from app.services.cleaner.splitter import ChapterSplitter, SentenceSplitter

from app.services.cleaner.llm_client import LLMClient
from app.services.cleaner.cleaner import TextCleaner
from app.services.cleaner.emotion import EmotionAnalyzer
from app.services.cleaner.speaker import SpeakerAssigner
from app.services.tts.client import TTSClient, TTSBatchProcessor
from app.services.audio.assembler import AudioAssembler

PROJECTS_DIR = "backend/data/projects"
OUTPUT_DIR = "backend/data/outputs"

class ProjectManager:
    def __init__(self):
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def list_projects(self) -> List[Project]:
        projects = []
        if not os.path.exists(PROJECTS_DIR):
            return []
            
        for pid in os.listdir(PROJECTS_DIR):
            p_dir = os.path.join(PROJECTS_DIR, pid)
            if os.path.isdir(p_dir):
                p_file = os.path.join(p_dir, "project.json")
                if os.path.exists(p_file):
                    try:
                        with open(p_file, "r") as f:
                            data = json.load(f)
                            projects.append(Project(**data))
                    except Exception as e:
                        print(f"Error loading project {pid}: {e}")
        
        # Sort by updated_at desc
        projects.sort(key=lambda x: x.updated_at, reverse=True)
        return projects

    def get_project(self, project_id: str) -> Optional[Project]:
        p_file = os.path.join(PROJECTS_DIR, project_id, "project.json")
        if not os.path.exists(p_file):
            return None
        with open(p_file, "r") as f:
            return Project(**json.load(f))

    def create_project(self, file_path: str, filename: str) -> Project:
        project_id = str(uuid.uuid4())
        project_dir = os.path.join(PROJECTS_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)

        # 1. Parse Book
        try:
            loader = LoaderFactory.get_loader(file_path)
            book = loader.load(file_path)
            book.id = project_id
            
            # Initial Split
            splitter = ChapterSplitter()
            book = splitter.split(book)
            sent_splitter = SentenceSplitter()
            book = sent_splitter.split(book)
            
            # Save Book Content
            book_path = os.path.join(project_dir, "book.json")
            self._save_book_file(book, book_path)
            
            # Create Project Metadata
            project = Project(
                id=project_id,
                name=filename,
                status=ProjectStatus.STRUCTURED,
                book_path=book_path,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self._save_project_file(project)
            
            return project
            
        except Exception as e:
            # Cleanup if failed
            shutil.rmtree(project_dir)
            raise e

    def get_book_content(self, project_id: str) -> Optional[Book]:
        project = self.get_project(project_id)
        if not project or not project.book_path or not os.path.exists(project.book_path):
            return None
        
        with open(project.book_path, "r") as f:
            data = json.load(f)
            return Book(**data)

    def update_book_content(self, project_id: str, book: Book) -> Project:
        project = self.get_project(project_id)
        if not project:
            raise ValueError("Project not found")
            
        self._save_book_file(book, project.book_path)
        
        project.updated_at = datetime.now()
        self._save_project_file(project)
        return project

    def update_project_status(self, project_id: str, status: ProjectStatus) -> Project:
        project = self.get_project(project_id)
        if not project:
            raise ValueError("Project not found")
            
        project.status = status
        project.updated_at = datetime.now()
        self._save_project_file(project)
        return project

    async def analyze_project(self, project_id: str) -> Project:
        project = self.get_project(project_id)
        if not project:
            raise ValueError("Project not found")
            
        book = self.get_book_content(project_id)
        if not book:
            raise ValueError("Book content not found")

        # Initialize Services
        llm_client = LLMClient()
        cleaner = TextCleaner(llm_client)
        emotion_analyzer = EmotionAnalyzer(llm_client)
        speaker_assigner = SpeakerAssigner("backend/assets")

        # Run Analysis
        for chapter in book.chapters:
            for sentence in chapter.sentences:
                # Clean
                sentence = await cleaner.clean_sentence(sentence)
                # Analyze Emotion
                if not sentence.is_noise:
                    sentence = await emotion_analyzer.analyze_sentence(sentence)
        
        # Assign Voices
        book = speaker_assigner.assign_voices(book)
        
        # Save
        self._save_book_file(book, project.book_path)
        return self.update_project_status(project_id, ProjectStatus.ANALYZED)

    async def synthesize_project(self, project_id: str) -> Project:
        project = self.get_project(project_id)
        if not project:
            raise ValueError("Project not found")
            
        book = self.get_book_content(project_id)
        if not book:
            raise ValueError("Book content not found")

        # Initialize TTS Client
        tts_client = TTSClient() # Uses default URL from env or default
        batch_processor = TTSBatchProcessor(tts_client)
        audio_assembler = AudioAssembler()
        
        # Output dir for this project
        project_output_dir = os.path.join(OUTPUT_DIR, project_id)
        clips_dir = os.path.join(project_output_dir, "clips")
        os.makedirs(clips_dir, exist_ok=True)

        # Synthesize
        for chapter in book.chapters:
            for sentence in chapter.sentences:
                if sentence.is_noise:
                    continue
                
                speaker_audio = sentence.metadata.get("speaker_audio_path")
                if not speaker_audio or not os.path.exists(speaker_audio):
                    speaker_audio = "backend/assets/ref_audio.wav"
                
                await batch_processor.process_sentence(sentence, speaker_audio, clips_dir)

        # Assemble
        final_dir = audio_assembler.assemble_book(book, project_output_dir)
        
        # Update Project
        project.audio_dir = final_dir
        project.status = ProjectStatus.COMPLETED
        project.updated_at = datetime.now()
        
        # Save updated book (with audio paths) and project
        self._save_book_file(book, project.book_path)
        self._save_project_file(project)
        
        return project

    def _save_project_file(self, project: Project):
        p_dir = os.path.join(PROJECTS_DIR, project.id)
        with open(os.path.join(p_dir, "project.json"), "w") as f:
            f.write(project.model_dump_json(indent=2))

    def _save_book_file(self, book: Book, path: str):
        with open(path, "w") as f:
            f.write(book.model_dump_json(indent=2))
