import os
import json
import httpx
from typing import Dict, Any, Optional

class LLMClient:
    def __init__(self, api_key: str = None, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)

    async def chat_completion(self, 
                            messages: list, 
                            model: str = "gpt-4",
                            temperature: float = 0.7,
                            json_mode: bool = False) -> Optional[Dict[str, Any]]:
        
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not set. Returning mock response.")
            # Mock response based on system prompt content to guess type
            system_content = messages[0]["content"]
            if "清洗助手" in system_content:
                mock_data = {
                    "original_text": "Mock text",
                    "is_noise": False,
                    "content_type": "narration",
                    "speaker": "无",
                    "noise_type": None,
                    "process_suggestion": "保留",
                    "cleaned_text": None,
                    "confidence": 0.99
                }
            elif "情感色彩" in system_content:
                mock_data = {
                    "emotion_vector": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.3],
                    "primary_emotion": "平静",
                    "emotion_intensity": 0.5,
                    "reasoning": "Mock reasoning"
                }
            else:
                mock_data = {}

            if json_mode:
                return mock_data
            return json.dumps(mock_data)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions", 
                json=payload, 
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            if json_mode:
                return json.loads(content)
            return content
            
        except Exception as e:
            print(f"LLM API Error: {e}")
            return None
