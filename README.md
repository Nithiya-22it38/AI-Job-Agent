# 🤖 AI Job Application Agent

A tool-calling AI agent that compares your resume with a job description, scores the match,
finds missing skills, suggests resume improvements and writes a short cover letter.

## Why this project
It shows the core of agentic AI: the LLM decides **which tool to call and in what order**,
our Python code runs the tool, and the result goes back to the LLM until it can answer.

## Features
- Tool calling with 3 tools: `extract_skills`, `calculate_match`, `get_learning_tips`
- Agent loop with a turn limit and error handling
- Match score, matched/missing skills, resume tips, cover letter
- Resume PDF upload
- "What the agent did" panel showing every tool call (great for demos)

## Tech stack
Python, Streamlit, Gemini API (function calling), JSON, pypdf, Git/GitHub

## Project structure
```
job-agent/
├── app.py              # Streamlit UI
├── agent.py            # Agent loop (model <-> tools)
├── tools.py            # Tool functions + schemas
├── utils.py            # PDF reading
├── sample/             # Sample resume and job description
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup
```bash
git clone <your-repo-url> && cd job-agent
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then add your GEMINI_API_KEY
streamlit run app.py
```

## How it works
1. User pastes the resume and job description.
2. The model gets the tool list and calls `extract_skills` for both texts.
3. The model passes both skill lists to `calculate_match`.
4. For missing skills it calls `get_learning_tips`.
5. When no more tools are needed, it writes the final report.

## Future improvements
- Add RAG over a folder of past resumes
- Add a LangGraph version of the workflow
- Add tests and deploy to Streamlit Community Cloud

## Screenshots
_Add 2-3 screenshots here._

## Demo
_Add your demo video link here._
