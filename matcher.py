"""
AI Resume Matcher - Core Logic
Extracts text from resume files, sends it + a job description to an LLM,
and returns a structured match report (score, matched/missing keywords, suggestions).
"""

import json
import os
from io import BytesIO

from openai import OpenAI
from pypdf import PdfReader
from docx import Document

# ---------------------------------------------------------------------------
# 1. Client setup
# ---------------------------------------------------------------------------
# Reads OPENAI_API_KEY from environment. Set it before running:
#   export OPENAI_API_KEY="sk-..."   (Mac/Linux)
#   set OPENAI_API_KEY="sk-..."      (Windows cmd)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

MODEL_NAME = "gpt-4o-mini"  # cheap + fast; swap for any chat model you have access to


# ---------------------------------------------------------------------------
# 2. Text extraction
# ---------------------------------------------------------------------------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from an uploaded PDF (as bytes)."""
    reader = PdfReader(BytesIO(file_bytes))
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract raw text from an uploaded DOCX (as bytes)."""
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_resume_text(uploaded_file) -> str:
    """
    Dispatch based on file extension.
    `uploaded_file` is a Streamlit UploadedFile object (has .name and .read()).
    """
    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif filename.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")


# ---------------------------------------------------------------------------
# 3. Prompt construction
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) resume screener.
Your job is to compare a candidate's resume against a job description and return
an honest, specific evaluation.

Rules:
- Score strictly based on keyword and skill overlap, not general impressiveness.
- "matched_keywords" = skills/tools/keywords present in BOTH the resume and JD.
- "missing_keywords" = important skills/tools from the JD that are absent from the resume.
- "suggestions" = 3-5 concrete, specific edits the candidate could make (not generic advice).
- Respond with ONLY valid JSON. No markdown, no code fences, no commentary.

JSON schema:
{
  "match_score": <integer 0-100>,
  "matched_keywords": [<string>, ...],
  "missing_keywords": [<string>, ...],
  "suggestions": [<string>, ...],
  "summary": "<1-2 sentence honest overall assessment>"
}
"""

def build_user_prompt(resume_text: str, jd_text: str) -> str:
    return f"""JOB DESCRIPTION:
{jd_text}

---

RESUME:
{resume_text}

---

Compare the resume against the job description and return the JSON evaluation."""


# ---------------------------------------------------------------------------
# 4. LLM call + structured output parsing
# ---------------------------------------------------------------------------
def get_match_report(resume_text: str, jd_text: str) -> dict:
    """
    Calls the LLM with the resume + JD and returns a parsed dict matching
    the schema described in SYSTEM_PROMPT. Raises a clear error if parsing fails.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.2,  # low temperature = more consistent scoring
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(resume_text, jd_text)},
        ],
    )

    raw_output = response.choices[0].message.content.strip()

    # Defensive cleanup in case the model wraps output in ```json ... ```
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        if raw_output.lower().startswith("json"):
            raw_output = raw_output[4:].strip()

    try:
        report = json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model did not return valid JSON. Raw output:\n{raw_output}"
        ) from e

    return report


# ---------------------------------------------------------------------------
# 5. Quick manual test (run: python matcher.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample_resume = """
    Python developer with experience in Django, REST APIs, and MySQL.
    Built automation scripts and worked with Git/GitHub.
    """
    sample_jd = """
    Looking for an AI Engineer with experience in Python, OpenAI/GPT APIs,
    LangChain, prompt engineering, and n8n automation.
    """

    result = get_match_report(sample_resume, sample_jd)
    print(json.dumps(result, indent=2))
