# generating_syllabus.py

import os

import langchain_community

from flashcard_generator import generate_flashcards
from multilingual_support import MultilingualSupport
from progress_tracker import ProgressTracker
from openrouter_llm import ChatOpenRouter
langchain_community.chat_models.ChatOpenAI,
from typing import List
from dotenv import load_dotenv

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# ✅ Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")  # Corrected key usage

# ✅ Initialize multilingual & progress tracking
multilingual = MultilingualSupport()
progress_tracker = ProgressTracker()




# ✅ Reusable LLM Getter
def get_llm(temp=0.7):
    return ChatOpenRouter(
        temperature=temp,
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
        model="gpt-3.5-turbo-0613"

    )








# ✅ DiscussAgent Class
class DiscussAgent:
    def __init__(self, system_message: SystemMessage, model):
        self.system_message = system_message
        self.model = model
        self.init_messages()

    def reset(self):
        self.init_messages()

    def init_messages(self):
        self.stored_messages = [self.system_message]

    def update_messages(self, message: BaseMessage) -> List[BaseMessage]:
        self.stored_messages.append(message)
        return self.stored_messages

    def step(self, input_message: HumanMessage) -> AIMessage:
        messages = self.update_messages(input_message)
        output_message = self.model.invoke(messages)
        self.update_messages(output_message)
        return output_message

# ✅ Roles & Prompts
assistant_role_name = "Instructor"
user_role_name = "Teaching Assistant"
word_limit = 50

assistant_inception_prompt = """Never forget you are a {assistant_role_name} and I am a {user_role_name}. Never flip roles! Never instruct me!
We share a common interest in collaborating to successfully complete a task.
You must help me to complete the task.
Here is the task: {task}. Never forget our task!
Your solution must be declarative sentences and simple present tense.
Unless I say the task is completed, you should always start with:
Solution: <YOUR_SOLUTION>
<YOUR_SOLUTION> should be specific and provide preferable implementations and examples for task-solving.
Always end <YOUR_SOLUTION> with: Next request."""

user_inception_prompt = """Never forget you are a {user_role_name} and I am a {assistant_role_name}. Never flip roles! You will always instruct me.
When the task is completed, you must only reply with a single word <TASK_DONE>.
Never say <TASK_DONE> unless my responses have solved your task."""

def get_sys_msgs(assistant_role_name: str, user_role_name: str, task: str):
    assistant_sys_msg = SystemMessagePromptTemplate.from_template(
        assistant_inception_prompt
    ).format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
    )[0]

    user_sys_msg = SystemMessagePromptTemplate.from_template(
        user_inception_prompt
    ).format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
    )[0]

    return assistant_sys_msg, user_sys_msg

# ✅ Task Specifier Setup
task_specifier_sys_msg = SystemMessage(content="You can make a task more specific.")
task_specifier_prompt = """Here is a task that {assistant_role_name} will help {user_role_name} to complete: {task}.
Please make it more specific. Be creative and imaginative.
Please reply with the specified task in {word_limit} words or less. Do not add anything else."""
task_specifier_template = HumanMessagePromptTemplate.from_template(template=task_specifier_prompt)

task_specify_agent = DiscussAgent(
    task_specifier_sys_msg,
    get_llm(temp=1.0)
)

# ✅ Syllabus Generator
def generate_syllabus(topic, task):
    task_specifier_msg = task_specifier_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
        word_limit=word_limit,
    )[0]
    specified_task_msg = task_specify_agent.step(task_specifier_msg)
    specified_task = specified_task_msg.content

    assistant_sys_msg, user_sys_msg = get_sys_msgs(
        assistant_role_name, user_role_name, specified_task
    )

    assistant_agent = DiscussAgent(assistant_sys_msg, get_llm(0.2))
    user_agent = DiscussAgent(user_sys_msg, get_llm(0.2))

    assistant_agent.reset()
    user_agent.reset()

    assistant_msg = HumanMessage(content=f"{user_sys_msg.content}. Now start to give me introductions one by one.")
    user_msg = HumanMessage(content=f"{assistant_sys_msg.content}")
    user_msg = assistant_agent.step(user_msg)

    conversation_history = []

    for _ in range(5):
        user_ai_msg = user_agent.step(assistant_msg)
        user_msg = HumanMessage(content=user_ai_msg.content)
        conversation_history.append("AI User: " + user_msg.content)

        if "<TASK_DONE>" in user_msg.content:
            break

        assistant_ai_msg = assistant_agent.step(user_msg)
        assistant_msg = HumanMessage(content=assistant_ai_msg.content)
        conversation_history.append("AI Assistant: " + assistant_msg.content)

    summarizer_sys_msg = SystemMessage(
        content=f"Summarize this conversation into a {topic} course syllabus form"
    )
    summarizer_prompt = """Here is a conversation history that {assistant_role_name} has discussed with {user_role_name}: {conversation_history}.
Please summarize this into a course syllabus with the topic from user input."""
    summarizer_template = HumanMessagePromptTemplate.from_template(template=summarizer_prompt)

    summarizer_agent = DiscussAgent(summarizer_sys_msg, get_llm(1.0))
    summarizer_msg = summarizer_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        conversation_history=conversation_history,
    )[0]
    summarized_msg = summarizer_agent.step(summarizer_msg)
    return summarized_msg.content

# ✅ Assignment Generator
def generate_assignment(topic):
    assignment_prompt = f"""
    You are an expert instructor. Create a detailed assignment for the topic: '{topic}'.
    The assignment should include:
    - A brief introduction or scenario
    - 3 to 5 questions (mix of theory and practical)
    - Clear instructions
    - Expected length for answers (if applicable)
    Format the output neatly.
    """
    assignment_agent = DiscussAgent(
        SystemMessage(content="Generate assignments based on topics."),
        get_llm(0.7)
    )
    input_msg = HumanMessage(content=assignment_prompt)
    output_msg = assignment_agent.step(input_msg)
    return output_msg.content

# ✅ Quiz Generator
def generate_quiz(topic):
    quiz_prompt = f"""
    You are a quiz generator. Create a quiz for the topic: '{topic}'.

    🟢 Include 3 multiple-choice questions (MCQs):
    - Each MCQ should have 4 options.
    - Mark the correct answer with (Correct).

    🔵 Include 2 short answer questions:
    - Each should test conceptual understanding.
    - Limit answer to 2–3 sentences.

    🟠 Include 1 long answer question:
    - Should be open-ended and require deeper understanding.
    - Expected answer length: 100–150 words.

    Format clearly with headings like:
    - "Multiple Choice Questions"
    - "Short Answer Questions"
    - "Long Answer Question"
    """

    from langchain_core.messages import HumanMessage, SystemMessage
    from generating_syllabus import DiscussAgent, get_llm  # ensure get_llm exists in generating_syllabus

    quiz_agent = DiscussAgent(
         SystemMessage(content="Generate quizzes with answers."),
         get_llm(0.7)  # This should call ChatOpenRouter with correct model
    )

    input_msg = HumanMessage(content=quiz_prompt)
    output_msg = quiz_agent.step(input_msg)
    return output_msg.content


#def generate_quiz(topic):
 #   quiz_prompt = f"""
  #  You are a quiz generator. Create a 5-question multiple-choice quiz for the topic: '{topic}'.
   # - Each question should have 4 options
    #- Highlight the correct answer using (Correct)
    #- Ensure varying difficulty levels
    #- Focus on key concepts from the topic
    #"""
    #quiz_agent = DiscussAgent(
     #   SystemMessage(content="Generate quizzes with answers."),
      #  get_llm(0.7)
   # )
    #input_msg = HumanMessage(content=quiz_prompt)
    #output_msg = quiz_agent.step(input_msg)
    #return output_msg.content

# ✅ Flashcard Generator
def generate_flashcards_from_content(content):
    flashcard_prompt = f"""
    Based on the following content, generate 5–10 flashcards in the format:
    Q: <question>
    A: <answer>

    Content:
    {content}
    """
    flashcard_agent = DiscussAgent(
        SystemMessage(content="Generate educational flashcards."),
        get_llm(0.7)
    )
    input_msg = HumanMessage(content=flashcard_prompt)
    output_msg = flashcard_agent.step(input_msg)
    return output_msg.content

# ✅ Multilingual Translation
def translate_output(content: str, languages=["ur", "fr", "de", "es"]) -> dict:
    translations = {}
    for lang in languages:
        translations[lang] = multilingual.translate_text(content, lang)
    return translations
