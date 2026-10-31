# agent.py
# This file talks to Gemini and runs the "agent loop":
#   1. send a message to Gemini
#   2. if Gemini asks for a tool, we run it and send the result back
#   3. repeat until Gemini gives the final answer

import json
import os

from dotenv import load_dotenv
from google import genai

from tools import TOOL_SCHEMAS, run_tool

# read the API key from the .env file
load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
MAX_ROUNDS = 8  # stop after 8 rounds so the loop can never run forever

# Instructions for Gemini
PROMPT = """You are a job application assistant that helps freshers.

Follow these steps:
1. Call extract_skills for the resume.
2. Call extract_skills for the job description.
3. Call calculate_match with the two skill lists.
4. If there are missing skills, call get_learning_tips for them.
5. Write the final answer.

Rules:
- Never invent skills, projects or experience.
- Use only facts from the resume.
- Use the tool results for the score and the skill lists.

Write the final answer in Markdown with these headings:
## Match Summary
## Matched Skills
## Missing Skills (with learning tips)
## 3 Resume Improvements
## Cover Letter
Keep the cover letter under 150 words and end it with [Your Name].
"""


def run_agent(resume, job_description):
    # check that the API key is there
    if not os.getenv("GEMINI_API_KEY"):
        raise Exception("GEMINI_API_KEY is missing. Add it to your .env file.")

    client = genai.Client()

    # the tools read the texts from here
    texts = {"resume": resume, "job_description": job_description}

    # first message to Gemini
    message = PROMPT + "\n\nRESUME:\n" + resume + "\n\nJOB DESCRIPTION:\n" + job_description

    previous_id = None   # no earlier conversation yet
    tool_calls = []      # we save every tool call to show it on the page

    for round_number in range(MAX_ROUNDS):
        # send the message to Gemini
        try:
            reply = client.interactions.create(
                model=MODEL,
                input=message,
                tools=TOOL_SCHEMAS,
                previous_interaction_id=previous_id,
            )
        except Exception as error:
            if "429" in str(error) or "RESOURCE_EXHAUSTED" in str(error):
                raise Exception("Gemini free limit reached. Please wait a minute and try again.")
            raise error

        # check if Gemini wants to use any tools
        tool_results = []
        for step in reply.steps:
            if step.type == "function_call":
                tool_input = dict(step.arguments or {})
                tool_output = run_tool(step.name, tool_input, texts)

                tool_calls.append({"name": step.name, "input": tool_input, "output": tool_output})

                tool_results.append({
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [{"type": "text", "text": json.dumps(tool_output)}],
                })

        # no tools asked = Gemini is finished, so this is the final answer
        if len(tool_results) == 0:
            return reply.output_text, tool_calls

        # otherwise send the tool results back and go again
        message = tool_results
        previous_id = reply.id

    raise Exception("The agent could not finish. Please try again.")