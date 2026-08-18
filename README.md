AI Resume Matcher
An AI-powered tool that compares a resume against a job description and returns
an ATS-style match score, matched/missing keywords, and specific improvement
suggestions — powered by the OpenAI API.
Features
Upload resume as PDF, DOCX, or TXT
Paste any job description
Get a structured JSON evaluation:
Match score (0–100)
Matched keywords
Missing keywords
Concrete, specific suggestions to improve the resume
Simple Streamlit web UI — no setup beyond pip install
Tech Stack
Python
OpenAI API (chat completions, structured JSON output)
pypdf / python-docx for resume text extraction
Streamlit for the UI
Setup
Bash
Set your OpenAI API key:
Bash
Run
Bash
Then open the local URL Streamlit prints (usually http://localhost:8501).
How it works
matcher.py extracts raw text from the uploaded resume file.
The resume text + job description are sent to the OpenAI API with a
system prompt instructing the model to act as an ATS screener and return
strict JSON.
The JSON response is parsed and rendered in the Streamlit UI.
Roadmap / Possible Extensions
[ ] Add a RAG layer: retrieve resume best-practice snippets from a small
vector store (FAISS/Chroma) and inject them into the prompt for more
grounded suggestions.
[ ] Support batch-scoring multiple resumes against one JD.
[ ] Export the report as a downloadable PDF.
[ ] Deploy to Streamlit Community Cloud for a live demo link.
License
MIT
