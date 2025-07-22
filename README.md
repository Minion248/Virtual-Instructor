Virtual Instructor


Virtual Instructor is an AI-powered educational assistant designed to help students and teachers generate personalized study material. It serves as a virtual teaching companion, allowing users to generate syllabi, assignments, quizzes, flashcards, track progress, translate content, and interact with an AI tutor — all in one place. Built using LangChain, OpenRouter (GPT-3.5-turbo / Mistral), and Gradio for seamless interaction.
📌 Features
•	✅ Syllabus Generator
•	✅ Assignment & Quiz Creator (MCQs + Theory)
•	✅ Flashcard Generator
•	✅ Multilingual Translation Support
•	✅ Progress Tracker
•	✅ Chat with AI Instructor
•	✅ Gradio Interface (User-friendly Tabs)
•	✅ Modular and LMS-ready
🔧 Project Setup
1. Clone the Repository
   
git clone https://github.com/your-username/virtual- instructor.git
cd virtual- instructor

3. Create Virtual Environment:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

5. Install Requirements:
pip install -r requirements.txt

🔐 .env Configuration
Before running the app, you must create a .env file in the root directory with your OpenRouter API key:
OPENROUTER_API_KEY=your_openrouter_api_key_here

🏁 How to Run
python src/run.py
This will start the Gradio app locally. Access it via your browser at:
http://127.0.0.1:7860

## 📁 Directory Structure

```
Virtual-Instructor/
├── .env.example
├── requirements.txt
├── README.md
├── run.py
├── src/
│   ├── generating_syllabus.py
│   ├── flashcard_generator.py
│   ├── openrouter_llm.py
│   ├── teaching_agent.py
│   ├── multilingual_support.py
│   ├── progress_tracker.py
│   └── ...
├── data/
│   ├── conversation.aiml
│   └── ...
├── pretrained_model/
│   ├── learningFileList.aiml
│   └── aiml_pretrained_model.dump
```


🌍 Supported Languages
EduGPT supports translation to the following languages:
•	• Urdu
•	• Hindi
•	• French
•	• Spanish
•	• Arabic
•	• Chinese
💡 Future Enhancements
•	🔮 Virtual Reality (VR) Classroom Integration
•	🔮 Embedding-based Personalized Learning
•	🔮 Mobile App Deployment
•	🔮 LMS Platform Plug-in
👩‍💻 Authors
• Sara Akmal
 
