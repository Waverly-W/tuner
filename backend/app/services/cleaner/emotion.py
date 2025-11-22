from typing import List
from app.services.cleaner.llm_client import LLMClient
from app.models.book import Sentence

EMOTION_PROMPT = """
分析文本的情感色彩，输出 8 维情感向量（0.0-1.0 浮点数）。

任务：基于文本内容和上下文，判断情感倾向。

输出 JSON：
{
  "emotion_vector": [0.1, 0.2, 0.1, 0.1, 0.1, 0.2, 0.3, 0.9],
  "primary_emotion": "平静",
  "emotion_intensity": 0.7,
  "reasoning": "情感分析理由"
}

规则：
- 向量和 = 1.0（归一化）
- 8维顺序：[高兴, 愤怒, 悲伤, 害怕, 厌恶, 忧郁, 惊讶, 平静]
- 主要情感为最高值
- 强度表示情感强烈程度
"""

class EmotionAnalyzer:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def analyze_sentence(self, sentence: Sentence, context: str = "") -> Sentence:
        # Skip if noise
        if sentence.is_noise:
            return sentence

        user_prompt = f"""
分析以下文本的情感：
"{sentence.text}"

上下文：
{context}
"""
        messages = [
            {"role": "system", "content": EMOTION_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        result = await self.llm_client.chat_completion(messages, json_mode=True)
        
        if result:
            sentence.emotion_vector = result.get("emotion_vector")
            sentence.metadata["primary_emotion"] = result.get("primary_emotion")
            sentence.metadata["emotion_intensity"] = result.get("emotion_intensity")
            
        return sentence
