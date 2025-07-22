# teaching_agent.py

import os
from typing import Any, Dict, List

import langchain_community
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field
from openrouter_llm import ChatOpenRouter
langchain_community.chat_models.ChatOpenAI,
# Load environment variables
load_dotenv()

# Instructor Conversation Chain
class InstructorConversationChain(LLMChain):
    @classmethod
    def from_llm(cls, llm: BaseLanguageModel, verbose: bool = True) -> LLMChain:
        """Build the LLM chain with an instructional teaching prompt."""
        instructor_prompt = """
        As a Machine Learning instructor agent, your task is to teach the user based on a provided syllabus.
        The syllabus serves as a roadmap for the learning journey, outlining the specific topics, concepts, and learning objectives to be covered.
        Review the provided syllabus and familiarize yourself with its structure and content.
        Take note of the different topics, their order, and any dependencies between them. Ensure you have a thorough understanding of the concepts to be taught.
        Your goal is to follow topic-by-topic as the given syllabus and provide step to step comprehensive instruction to convey the knowledge in the syllabus to the user.
        DO NOT DISORDER THE SYLLABUS.

        ===
        {syllabus}
        ===

        Maintain a supportive and approachable tone.
        Go deep into each topic: definitions, formulas (if any), and examples.
        Follow the topic order. Do not skip or jump ahead.
        End your response with <END_OF_TURN> so the user can respond.

        ===
        {conversation_history}
        ===
        """
        prompt = PromptTemplate(
            template=instructor_prompt,
            input_variables=["syllabus", "topic", "conversation_history"],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)


# Teaching Agent controller
class TeachingGPT(Chain, BaseModel):
    syllabus: str = ""
    conversation_topic: str = ""
    conversation_history: List[str] = []
    teaching_conversation_utterance_chain: InstructorConversationChain = Field(...)

    class Config:
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return []

    def seed_agent(self, syllabus: str, task: str):
        self.syllabus = syllabus
        self.conversation_topic = task
        self.conversation_history = []

    def human_step(self, human_input: str):
        self.conversation_history.append(human_input.strip() + " <END_OF_TURN>")

    def instructor_step(self) -> str:
        result = self._call({})
        return result['text'] if isinstance(result, dict) else str(result)

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        response = self.teaching_conversation_utterance_chain.invoke({
            "syllabus": self.syllabus,
            "topic": self.conversation_topic,
            "conversation_history": "\n".join(self.conversation_history),
        })

        ai_message = response['text'] if isinstance(response, dict) else str(response)
        self.conversation_history.append(ai_message)
        print("Instructor:", ai_message.rstrip("<END_OF_TURN>"))
        return {"text": ai_message}

    @classmethod
    def from_llm(cls, llm: BaseLanguageModel, verbose: bool = False, **kwargs) -> "TeachingGPT":
        conversation_chain = InstructorConversationChain.from_llm(llm, verbose=verbose)
        return cls(teaching_conversation_utterance_chain=conversation_chain, **kwargs)


# ✅ Initialize OpenRouter LLM for the instructor
llm = ChatOpenRouter(

    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="gpt-3.5-turbo-0613",
    temperature=0.7
)

# ✅ Teaching agent instance
config = dict(conversation_history=[], syllabus="", conversation_topic="")
teaching_agent = TeachingGPT.from_llm(llm=llm, verbose=False, **config)
