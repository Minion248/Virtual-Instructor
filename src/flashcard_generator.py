# flashcard_generator.py

import os

import langchain_community
from dotenv import load_dotenv
langchain_community.chat_models.ChatOpenAI,
from langchain_core.messages import HumanMessage, SystemMessage
from openrouter_llm import ChatOpenRouter  # ✅ Custom wrapper for OpenRouter

# ✅ Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise EnvironmentError("OPENROUTER_API_KEY not found in .env file.")

# ✅ Set fallback OPENAI_API_KEY for LangChain compatibility
os.environ["OPENAI_API_KEY"] = api_key

# ✅ Setup the OpenRouter-compatible LLM
llm = ChatOpenRouter(
    temperature=0.7,
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    model="gpt-3.5-turbo-0613"

)


# ✅ Flashcard Generation Function
def generate_flashcards(content: str) -> str:
    """
    Generate 5–10 flashcards from provided lecture/conversation content.
    Returns a formatted string.
    """
    prompt = f"""
    You are an expert teacher. Based on the following lecture, generate 5–10 flashcards.
    Format each card like:
    Q: <question>
    A: <answer>

    Lecture:
    {content}
    """

    messages = [
        SystemMessage(content="You are a flashcard generation expert."),
        HumanMessage(content=prompt)
    ]

    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"⚠️ Flashcard generation failed: {str(e)}"
