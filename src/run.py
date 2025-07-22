# run.py

import os
import time
import gradio as gr
from dotenv import load_dotenv

from openrouter_llm import ChatOpenRouter

from generating_syllabus import generate_syllabus, generate_assignment, generate_quiz

from teaching_agent import TeachingGPT

from flashcard_generator import generate_flashcards

from multilingual_support import MultilingualSupport
from progress_tracker import ProgressTracker


# ✅ Load .env variables
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY in .env file")

# ✅ Initialize OpenRouter-compatible model


llm = ChatOpenRouter(
    temperature=0.7,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="gpt-3.5-turbo-0613"

)


# ✅ Teaching Agent
teaching_agent = TeachingGPT.from_llm(llm=llm, verbose=False)

# ✅ Helpers
translator = MultilingualSupport()
tracker = ProgressTracker()

with gr.Blocks() as demo:
    gr.Markdown("# 🎓 Your AI Instructor (EduGPT)")

    # =================== Tab 1: Study Material ===================
    with gr.Tab("📘 Generate Study Material"):
        topic_input = gr.Textbox(label="📚 Enter a topic you want to learn:")
        syllabus_output = gr.Textbox(label="📖 Generated Syllabus")
        assignment_output = gr.Textbox(label="📝 Assignment")
        quiz_output = gr.Textbox(label="🧠 Quiz")

        generate_btn = gr.Button("🚀 Generate Syllabus")
        assignment_btn = gr.Button("🛠 Generate Assignment")
        quiz_btn = gr.Button("❓ Generate Quiz")

        def generate_all_material(topic):
            task = f"Generate a course syllabus to teach the topic: {topic}"
            syllabus = generate_syllabus(topic, task)
            assignment = generate_assignment(topic)
            quiz = generate_quiz(topic)
            teaching_agent.seed_agent(syllabus, task)
            return syllabus, assignment, quiz

        generate_btn.click(generate_all_material, inputs=topic_input, outputs=[syllabus_output, assignment_output, quiz_output])
        assignment_btn.click(generate_assignment, inputs=topic_input, outputs=assignment_output)
        quiz_btn.click(generate_quiz, inputs=topic_input, outputs=quiz_output)

    # =================== Tab 2: Multilingual Translator ===================
    with gr.Tab("🌐 Translate Output"):
        text_to_translate = gr.Textbox(label="🔠 Enter Text")
        lang_choice = gr.Dropdown(["ur", "fr", "de", "es", "zh-cn", "hi"], value="ur", label="🌍 Target Language")
        translated_output = gr.Textbox(label="🗣️ Translated Text")

        translate_button = gr.Button("🌍 Translate")
        translate_button.click(fn=translator.translate_text, inputs=[text_to_translate, lang_choice], outputs=translated_output)

    # =================== Tab 3: Flashcards ===================
    with gr.Tab("📋 Flashcards"):
        flashcard_output = gr.Textbox(label="🧠 Generated Flashcards")
        flashcard_button = gr.Button("📚 Generate Flashcards from AI Lecture")

        def generate_flashcards_from_ai():
            content = "\n".join(teaching_agent.conversation_history)
            if not content.strip():
                return "⚠️ No lecture found. Please chat with the AI instructor first!"
            return generate_flashcards(content)

        flashcard_button.click(generate_flashcards_from_ai, outputs=flashcard_output)

    # =================== Tab 4: Track Progress ===================
    with gr.Tab("📈 Track Progress"):
        progress_input = gr.Textbox(label="📌 Topic")
        progress_output = gr.Textbox(label="📊 Updated Progress")

        progress_btn = gr.Button("✅ Mark as Completed")
        progress_btn.click(fn=tracker.update_progress, inputs=progress_input, outputs=progress_output)

    # =================== Tab 5: AI Instructor Chat ===================
    with gr.Tab("👨‍🏫 Chat with AI Instructor"):
        chatbot = gr.Chatbot()
        msg = gr.Textbox(label="💬 Ask your instructor")
        clear = gr.Button("🧹 Clear")

        def user(user_message, history):
            teaching_agent.human_step(user_message)
            return "", history + [[user_message, None]]

        def bot(history):
            bot_message = teaching_agent.instructor_step()
            history[-1][1] = ""
            for char in bot_message:
                history[-1][1] += char
                time.sleep(0.05)
                yield history

        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(bot, chatbot, chatbot)
        clear.click(lambda: [], None, chatbot, queue=False)

# ✅ Start App
demo.queue().launch(debug=True, share=True)
