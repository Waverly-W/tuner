import re
from typing import List
from app.models.book import Book, Chapter, Sentence

class ChapterSplitter:
    # Regex patterns from PRD
    CHAPTER_PATTERNS = [
        r'^第[一二三四五六七八九十百千万\d]+章\s+',  # 第X章
        r'^第[一二三四五六七八九十百千万\d]+回\s+',  # 第X回
        r'Chapter\s+\d+\s*[:.]?\s*',          # Chapter X
        r'^\d+\.\s+',                         # 1. 标题
        r'^\*{3,}.*?\*{3,}',                 # *** 标题 ***
        r'^\[第\d+章\]',                      # [第X章]
    ]
    
    SPECIAL_CHAPTERS = {
        'prologue': r'^(序章|楔子|前言|引子|序幕)\s*',
        'epilogue': r'^(尾声|后记|附录|跋)\s*',
        'extra': r'^(番外|外传|特别篇)\s*'
    }

    def split(self, book: Book) -> Book:
        # If book already has structured chapters (e.g. from EPUB), we might skip or refine
        # For TXT, we have one raw chapter.
        
        new_chapters = []
        
        for chapter in book.chapters:
            # If chapter seems raw (one huge sentence), split it
            if len(chapter.sentences) == 1 and len(chapter.sentences[0].text) > 1000:
                raw_text = chapter.sentences[0].text
                split_chapters = self._split_text(raw_text)
                new_chapters.extend(split_chapters)
            else:
                new_chapters.append(chapter)
                
        book.chapters = new_chapters
        return book

    def _split_text(self, text: str) -> List[Chapter]:
        lines = text.split('\n')
        chapters = []
        current_chapter_lines = []
        current_title = "Start"
        
        # Compile regexes
        patterns = [re.compile(p) for p in self.CHAPTER_PATTERNS]
        special_patterns = [re.compile(p) for p in self.SPECIAL_CHAPTERS.values()]
        
        for line in lines:
            line_stripped = line.strip()
            is_header = False
            
            # Check if line matches chapter header
            for p in patterns + special_patterns:
                if p.match(line_stripped):
                    is_header = True
                    break
            
            if is_header:
                # Save previous chapter
                if current_chapter_lines:
                    chapters.append(Chapter(
                        id=f"ch_{len(chapters)}",
                        title=current_title,
                        sentences=[Sentence(id=f"s_{len(chapters)}", text='\n'.join(current_chapter_lines))]
                    ))
                current_title = line_stripped
                current_chapter_lines = []
            else:
                current_chapter_lines.append(line)
                
        # Add last chapter
        if current_chapter_lines:
            chapters.append(Chapter(
                id=f"ch_{len(chapters)}",
                title=current_title,
                sentences=[Sentence(id=f"s_{len(chapters)}", text='\n'.join(current_chapter_lines))]
            ))
            
        return chapters

class SentenceSplitter:
    def split(self, book: Book) -> Book:
        for chapter in book.chapters:
            new_sentences = []
            for sent in chapter.sentences:
                # If sentence is too long (raw text), split it
                if len(sent.text) > 200: # Threshold for "raw" text
                    split_sents = self._split_text_to_sentences(sent.text)
                    new_sentences.extend(split_sents)
                else:
                    new_sentences.append(sent)
            chapter.sentences = new_sentences
        return book

    def _split_text_to_sentences(self, text: str) -> List[Sentence]:
        # Simple splitting for MVP
        # PRD 2.2.2: Chinese and English splitters
        
        # Regex for splitting
        # (?<=[。！？…]) matches position after these chars
        # Avoid splitting inside quotes is harder with simple regex, 
        # but for MVP we can start with basic split.
        
        # Better regex that keeps delimiters
        pattern = r'([。！？…]+|\. )'
        
        parts = re.split(pattern, text)
        sentences = []
        current_sent = ""
        
        for part in parts:
            current_sent += part
            # If part ends with delimiter, finalize sentence
            if re.search(r'[。！？…]+|\. $', part):
                if current_sent.strip():
                    sentences.append(Sentence(
                        id=f"sub_{len(sentences)}",
                        text=current_sent.strip()
                    ))
                current_sent = ""
        
        if current_sent.strip():
             sentences.append(Sentence(
                id=f"sub_{len(sentences)}",
                text=current_sent.strip()
            ))
            
        return sentences
