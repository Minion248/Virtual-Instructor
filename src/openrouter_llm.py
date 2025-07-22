# openrouter_llm.py
from langchain_community.chat_models import ChatOpenAI
import os

class ChatOpenRouter(ChatOpenAI):
    def __init__(self, model: str = "openai/gpt-3.5-turbo-0613", temperature: float = 0.7, **kwargs):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables.")

        super().__init__(
            model=model,
            openai_api_base="https://openrouter.ai/api/v1",  # ✅ must be here, not `base_url`
            openai_api_key=api_key,
            temperature=temperature,
            **kwargs
        )
