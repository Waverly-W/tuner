import os
import json
import shutil
import subprocess
from typing import List
from app.models.book import Book, Chapter

class AudioAssembler:
    def __init__(self):
        self.silence_duration_ms = 300
        self.chapter_silence_ms = 1000

    def assemble_book(self, book: Book, output_dir: str) -> str:
        """
        Assembles the book audio and returns the path to the output directory.
        """
        book_dir = os.path.join(output_dir, self._sanitize_filename(book.title))
        chapters_dir = os.path.join(book_dir, "chapters")
        os.makedirs(chapters_dir, exist_ok=True)

        total_duration = 0
        
        # Create silence files
        silence_sentence_path = os.path.join(output_dir, "silence_sentence.wav")
        silence_chapter_path = os.path.join(output_dir, "silence_chapter.wav")
        self._create_silence(silence_sentence_path, self.silence_duration_ms)
        self._create_silence(silence_chapter_path, self.chapter_silence_ms)
        
        for chapter in book.chapters:
            file_list_path = os.path.join(chapters_dir, f"{chapter.id}_files.txt")
            with open(file_list_path, "w") as f:
                for sentence in chapter.sentences:
                    if sentence.audio_path and os.path.exists(sentence.audio_path):
                        f.write(f"file '{os.path.abspath(sentence.audio_path)}'\n")
                        f.write(f"file '{os.path.abspath(silence_sentence_path)}'\n")
                
                # Add chapter silence at end
                f.write(f"file '{os.path.abspath(silence_chapter_path)}'\n")
            
            # Concatenate
            chapter_filename = f"{chapter.id}_{self._sanitize_filename(chapter.title)}.wav"
            chapter_path = os.path.join(chapters_dir, chapter_filename)
            
            self._concat_files(file_list_path, chapter_path)
            
            # Get duration
            duration = self._get_duration(chapter_path)
            chapter.audio_path = chapter_path
            chapter.duration = duration
            total_duration += duration
            
            # Cleanup list
            os.remove(file_list_path)

        # Generate metadata
        self._generate_metadata(book, book_dir, total_duration)
        
        # Cleanup silence
        if os.path.exists(silence_sentence_path): os.remove(silence_sentence_path)
        if os.path.exists(silence_chapter_path): os.remove(silence_chapter_path)
        
        return book_dir

    def _create_silence(self, path: str, duration_ms: int):
        duration_sec = duration_ms / 1000.0
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono", 
            "-t", str(duration_sec), path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _concat_files(self, list_path: str, output_path: str):
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, 
            "-c", "copy", output_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _get_duration(self, path: str) -> float:
        try:
            result = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries", "format=duration", 
                "-of", "default=noprint_wrappers=1:nokey=1", path
            ], capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except:
            return 0.0

    def _generate_metadata(self, book: Book, book_dir: str, total_duration: float):
        metadata = {
            "title": book.title,
            "author": book.author,
            "duration": total_duration,
            "total_chapters": len(book.chapters),
            "chapters": [
                {
                    "id": c.id,
                    "title": c.title,
                    "file": f"chapters/{os.path.basename(c.audio_path)}" if c.audio_path else None,
                    "duration": c.duration
                }
                for c in book.chapters
            ]
        }
        
        with open(os.path.join(book_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _sanitize_filename(self, name: str) -> str:
        return "".join([c for c in name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()

    def export_to_zip(self, book_dir: str) -> str:
        """
        Zips the book directory.
        Returns path to the zip file.
        """
        zip_path = shutil.make_archive(book_dir, 'zip', book_dir)
        return zip_path


