import abc
import os
import chardet
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import List, Optional
from app.models.book import Book, Chapter, Sentence

class BaseLoader(abc.ABC):
    @abc.abstractmethod
    def load(self, file_path: str) -> Book:
        pass

class TextLoader(BaseLoader):
    def load(self, file_path: str) -> Book:
        # Detect encoding
        with open(file_path, 'rb') as f:
            raw = f.read(10000)
            result = chardet.detect(raw)
            encoding = result['encoding'] or 'utf-8'

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fallback to utf-8 with errors ignore/replace if detection failed
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

        # For TXT, we initially create one big chapter or just raw content
        # Splitting will happen in the next step (ChapterSplitter)
        # But to fit the model, we can put everything in a "Raw Content" chapter
        # Or we can try to do basic splitting here if it's simple.
        # The PRD says "Chapter Splitter" is a separate module (2.2.1).
        # So here we just load the text.
        
        filename = os.path.basename(file_path)
        title = os.path.splitext(filename)[0]
        
        # Create a temporary single chapter with all text
        # The splitter will later take this text and restructure the book
        chapter = Chapter(
            id="raw",
            title="Raw Content",
            sentences=[Sentence(id="raw_s", text=content)] 
            # We put all text in one "sentence" for now, or just attach it to chapter metadata
            # Actually, the Book model expects chapters. 
            # Let's store raw text in a dummy chapter's first sentence or similar.
            # Better: The ChapterSplitter will likely take a Book object and refine it.
        )
        
        return Book(
            id=filename, # Use filename as ID for now
            title=title,
            chapters=[chapter]
        )

class EpubLoader(BaseLoader):
    def load(self, file_path: str) -> Book:
        book = epub.read_epub(file_path)
        title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else "Unknown"
        author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "Unknown"
        
        chapters = []
        
        # Iterate items
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Extract text from HTML
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text(separator='\n')
                
                # Try to find a title from h1/h2
                chapter_title = "Untitled"
                header = soup.find(['h1', 'h2'])
                if header:
                    chapter_title = header.get_text().strip()
                
                if text.strip():
                    chapters.append(Chapter(
                        id=item.get_id(),
                        title=chapter_title,
                        sentences=[Sentence(id=f"{item.get_id()}_raw", text=text)]
                    ))
                    
        return Book(
            id=os.path.basename(file_path),
            title=title,
            author=author,
            chapters=chapters
        )

class LoaderFactory:
    @staticmethod
    def get_loader(file_path: str) -> BaseLoader:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.txt', '.md']:
            return TextLoader()
        elif ext == '.epub':
            return EpubLoader()
        else:
            raise ValueError(f"Unsupported format for loading: {ext}")
