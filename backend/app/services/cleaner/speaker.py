import os
from typing import Dict, Optional
from app.models.book import Sentence, Book

# Voice Configuration
VOICE_LIBRARY = {
    "V01": {"name": "旁白男声", "file": "voice_01.wav", "gender": "male", "type": "narration"},
    "V02": {"name": "旁白女声", "file": "voice_02.wav", "gender": "female", "type": "narration"},
    "V03": {"name": "青年男声", "file": "voice_03.wav", "gender": "male", "type": "dialogue"},
    "V04": {"name": "成熟男声", "file": "voice_04.wav", "gender": "male", "type": "dialogue"},
    "V05": {"name": "少女音", "file": "voice_05.wav", "gender": "female", "type": "dialogue"},
    "V06": {"name": "知性女声", "file": "voice_06.wav", "gender": "female", "type": "dialogue"},
}

class SpeakerAssigner:
    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        self.character_map: Dict[str, str] = {} # character_name -> voice_id

    def assign_voices(self, book: Book) -> Book:
        """
        Assigns a voice_id and audio_path to each sentence.
        """
        for chapter in book.chapters:
            for sentence in chapter.sentences:
                voice_id = self._get_voice_id(sentence)
                sentence.metadata["voice_id"] = voice_id
                
                # Resolve absolute path
                voice_file = VOICE_LIBRARY[voice_id]["file"]
                sentence.metadata["speaker_audio_path"] = os.path.join(self.assets_dir, "voices", voice_file)
                
        return book

    def _get_voice_id(self, sentence: Sentence) -> str:
        # 1. Narration
        if sentence.metadata.get("content_type") != "dialogue":
            return "V01" # Default narration

        # 2. Dialogue - Check speaker
        speaker = sentence.speaker
        if not speaker:
            return "V03" # Default male dialogue if unknown
            
        # 3. Check existing assignment
        if speaker in self.character_map:
            return self.character_map[speaker]
            
        # 4. Assign new voice (Simple Round-Robin or Logic)
        # For MVP, just alternate or random.
        # Here we just pick based on hash to be deterministic
        available_voices = ["V03", "V04", "V05", "V06"]
        idx = hash(speaker) % len(available_voices)
        voice_id = available_voices[idx]
        
        self.character_map[speaker] = voice_id
        return voice_id
