# app.py
# The web page. Run it with:  streamlit run app.py

import streamlit as st

from agent import run_agent
from utils import read_pdf

st.set_page_config(page_title="AI Job Application Agent", layout="wide")

st.title("AI Job Application Agent")
st.write("Paste your resume and a job description. The agent will find the match score, "
         "the missing skills, resume improvements and a cover letter.")

# Option to fill the boxes with sample text
use_sample = st.checkbox("Use sample resume and job description")
if use_sample:
    default_resume = open("sample/resume.txt").read()
    default_jd = open("sample/job_description.txt").read()
else:
    default_resume = ""
    default_jd = ""

# Two columns: resume on the left, job description on the right
col1, col2 = st.columns(2)

with col1:
    pdf_file = st.file_uploader("Upload resume PDF (optional, used instead of the text box)", type="pdf")
    resume_text = st.text_area("Your resume", value=default_resume, height=300)

with col2:
    jd_text = st.text_area("Job description", value=default_jd, height=300)

# When the button is clicked
if st.button("Run agent"):

    # if a PDF was uploaded, read the text from it
    if pdf_file is not None:
        try:
            resume_text = read_pdf(pdf_file)
        except Exception as error:
            st.error("Could not read the PDF: " + str(error))
            st.stop()

    # both boxes must have text
    if resume_text.strip() == "" or jd_text.strip() == "":
        st.warning("Please fill in both the resume and the job description.")
        st.stop()

    # run the agent
    with st.spinner("The agent is working..."):
        try:
            answer, tool_calls = run_agent(resume_text, jd_text)
        except Exception as error:
            st.error("Something went wrong: " + str(error))
            st.stop()

    # find the match score in the tool calls
    score = None
    for call in tool_calls:
        if call["name"] == "calculate_match":
            score = call["output"].get("score")

    if score is not None:
        st.metric("Match score", str(score) + "%")
        st.progress(score / 100)

    # show every tool the agent used
    with st.expander("What the agent did (" + str(len(tool_calls)) + " tool calls)"):
        number = 1
        for call in tool_calls:
            st.write("Step " + str(number) + ": " + call["name"])
            st.json({"input": call["input"], "output": call["output"]})
            number = number + 1

    # show the final report
    st.markdown(answer)