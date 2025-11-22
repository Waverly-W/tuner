from app.services.cleaner.llm_client import LLMClient
from app.models.book import Sentence
import asyncio

SYSTEM_PROMPT = """
你是一个专业的文本清洗助手，负责从文本书籍中识别并标注非正文内容。

任务：对每句话进行分析，识别内容类型，并提供处理建议。

输出格式（JSON）：
{
  "original_text": "原始文本",
  "is_noise": true/false,
  "content_type": "dialogue/narration/description/quote/footnote/noise",
  "speaker": "角色名/无",
  "noise_type": "页脚/旁注/脚注/其他噪音/null",
  "process_suggestion": "保留/移除/语音描述",
  "cleaned_text": "清洗后的文本",
  "confidence": 0.95
}
"""

class TextCleaner:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def clean_sentence(self, sentence: Sentence, context: str = "") -> Sentence:
        user_prompt = f"""
分析以下文本：
"{sentence.text}"

上下文（前3句）：
{context}

请返回 JSON 格式结果。
"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        result = await self.llm_client.chat_completion(messages, json_mode=True)
        
        if result:
            sentence.is_noise = result.get("is_noise", False)
            sentence.speaker = result.get("speaker") if result.get("speaker") != "无" else None
            sentence.metadata["content_type"] = result.get("content_type")
            sentence.metadata["cleaned_text"] = result.get("cleaned_text")
            
            # If cleaned text is different and valid, update it?
            # PRD says "cleaned_text" in output. 
            # We might want to keep original text but use cleaned for TTS.
            # For now, let's store it in metadata or update text if it's just cleaning.
            if result.get("cleaned_text"):
                 sentence.text = result.get("cleaned_text")
                 
        return sentence
