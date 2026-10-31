# tools.py
# These are the "tools" that the AI agent can ask us to run.

# Skills we look for in a resume or job description.
# (all small letters, singular form)
SKILLS = [
    "python", "java", "javascript", "sql", "mysql", "mongodb",
    "html", "css", "react", "flask", "django", "fastapi", "streamlit",
    "rest api", "json", "git", "github", "docker", "aws", "linux",
    "oop", "data structure", "pandas", "numpy",
    "machine learning", "llm", "prompt engineering",
    "langchain", "langgraph", "rag", "vector database", "ai agent",
]

# Different ways of writing the same skill
SYNONYMS = {
    " ml ": " machine learning ",
    " object oriented ": " oop ",
    " retrieval augmented generation ": " rag ",
    " agentic ai ": " ai agent ",
}

# Short advice for skills the candidate is missing
LEARNING_TIPS = {
    "rag": "Learn the idea: split documents, store them in a vector database, find the best parts, and give them to the LLM.",
    "vector database": "Try Chroma on your laptop: save a few texts and search them.",
    "langchain": "Build a small chain: prompt + LLM + output.",
    "langgraph": "Build a small graph with 2 or 3 steps.",
    "ai agent": "Build a small agent that uses tools, like this project.",
    "docker": "Put a small Python app in a Docker container.",
    "aws": "Learn EC2, S3 and IAM with the free tier.",
    "sql": "Practice joins and group by on a sample database.",
    "fastapi": "Build a small API with two or three endpoints.",
}
DEFAULT_TIP = "Do a short tutorial and add one small example to your GitHub."


def clean_text(text):
    # make everything small letters
    text = text.lower()
    # replace punctuation with spaces
    for ch in [",", ".", ":", ";", "(", ")", "/", "-", "|", "*", "#", "&", "\n", "\t"]:
        text = text.replace(ch, " ")
    # keep only one space between words
    text = " ".join(text.split())
    # add a space at the start and end so the first and last words also match
    text = " " + text + " "
    # change different spellings to one spelling
    for old, new in SYNONYMS.items():
        text = text.replace(old, new)
    return text


# TOOL 1: find the skills inside a text
def extract_skills(text):
    text = clean_text(text)
    found = []
    for skill in SKILLS:
        # the spaces make sure we match the whole word
        # (so "java" does not match "javascript")
        # the second check allows a plural, like "apis" or "agents"
        if " " + skill + " " in text or " " + skill + "s " in text:
            found.append(skill)
    return found


# TOOL 2: compare resume skills with job skills
def calculate_match(resume_skills, jd_skills):
    resume_skills = [s.lower() for s in resume_skills]
    jd_skills = [s.lower() for s in jd_skills]

    matched = []
    missing = []
    for skill in jd_skills:
        if skill in resume_skills:
            matched.append(skill)
        else:
            missing.append(skill)

    if len(jd_skills) == 0:
        score = 0
    else:
        score = round(len(matched) * 100 / len(jd_skills))

    return {"score": score, "matched": matched, "missing": missing}


# TOOL 3: give a learning tip for each missing skill
def get_learning_tips(skills):
    tips = {}
    for skill in skills:
        tips[skill.lower()] = LEARNING_TIPS.get(skill.lower(), DEFAULT_TIP)
    return {"tips": tips}


# This list tells Gemini which tools exist and what inputs they need.
# Gemini cannot see our code, it only reads this description.
TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "extract_skills",
        "description": "Find the tech skills inside the resume or the job description.",
        "parameters": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "enum": ["resume", "job_description"],
                    "description": "Which text to read.",
                }
            },
            "required": ["source"],
        },
    },
    {
        "type": "function",
        "name": "calculate_match",
        "description": "Compare resume skills with job skills. Returns a score from 0 to 100, the matched skills and the missing skills.",
        "parameters": {
            "type": "object",
            "properties": {
                "resume_skills": {"type": "array", "items": {"type": "string"}},
                "jd_skills": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["resume_skills", "jd_skills"],
        },
    },
    {
        "type": "function",
        "name": "get_learning_tips",
        "description": "Give a short learning tip for each missing skill.",
        "parameters": {
            "type": "object",
            "properties": {
                "skills": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["skills"],
        },
    },
]


# When Gemini asks for a tool, this function runs the right one.
def run_tool(name, tool_input, texts):
    try:
        if name == "extract_skills":
            source = tool_input.get("source")
            if source not in texts:
                return {"error": "Unknown source: " + str(source)}
            return {"source": source, "skills": extract_skills(texts[source])}
        elif name == "calculate_match":
            return calculate_match(tool_input.get("resume_skills", []), tool_input.get("jd_skills", []))
        elif name == "get_learning_tips":
            return get_learning_tips(tool_input.get("skills", []))
        else:
            return {"error": "Unknown tool: " + str(name)}
    except Exception as error:
        # never crash the app because of one bad tool call
        return {"error": str(error)}