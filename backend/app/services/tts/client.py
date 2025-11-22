import httpx
import asyncio
import os
from typing import Optional, List
from app.models.book import Sentence

class TTSClient:
    def __init__(self, api_url: str = "http://localhost:8000/api/tts"):
        self.api_url = api_url
        self.client = httpx.AsyncClient(timeout=60.0)

    async def synthesize(self, 
                         text: str, 
                         speaker_audio_path: str, 
                         output_filename: str,
                         emotion_mode: int = 0,
                         emotion_vector: Optional[List[float]] = None) -> Optional[bytes]:
        
        if not os.path.exists(speaker_audio_path):
            raise FileNotFoundError(f"Speaker audio not found: {speaker_audio_path}")

        files = {
            "speaker_audio": open(speaker_audio_path, "rb")
        }
        
        data = {
            "text": text,
            "output_filename": output_filename,
            "emotion_mode": emotion_mode
        }
        
        if emotion_vector and emotion_mode == 2:
            # Convert list to string "0.1,0.2,..."
            data["emotion_vector"] = ",".join(map(str, emotion_vector))

        try:
            response = await self.client.post(self.api_url, data=data, files=files)
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            print(f"TTS API Error: {e}")
            return None
        finally:
            files["speaker_audio"].close()

class TTSBatchProcessor:
    def __init__(self, tts_client: TTSClient, max_concurrent: int = 3):
        self.client = tts_client
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.retry_config = {
            "max_retries": 3,
            "base_delay": 2,
            "backoff_factor": 2
        }

    async def process_sentence(self, sentence: Sentence, speaker_audio: str, output_dir: str) -> Sentence:
        async with self.semaphore:
            for attempt in range(self.retry_config["max_retries"]):
                try:
                    output_filename = f"{sentence.id}"
                    # Note: API might return WAV content directly or save it.
                    # PRD 2.4.1 says "output_filename" is a param, but response is WAV.
                    # So we should save the content.
                    
                    audio_content = await self.client.synthesize(
                        text=sentence.text,
                        speaker_audio_path=speaker_audio,
                        output_filename=output_filename,
                        emotion_mode=2 if sentence.emotion_vector else 0,
                        emotion_vector=sentence.emotion_vector
                    )
                    
                    if audio_content:
                        file_path = os.path.join(output_dir, f"{output_filename}.wav")
                        with open(file_path, "wb") as f:
                            f.write(audio_content)
                        
                        sentence.audio_path = file_path
                        return sentence
                    else:
                        raise Exception("Empty response from TTS API")

                except Exception as e:
                    if attempt == self.retry_config["max_retries"] - 1:
                        print(f"Failed to synthesize sentence {sentence.id}: {e}")
                        # We might want to mark it as failed or return None
                        return sentence # Return without audio_path
                    
                    delay = self.retry_config["base_delay"] * (self.retry_config["backoff_factor"] ** attempt)
                    await asyncio.sleep(delay)
        return sentence
