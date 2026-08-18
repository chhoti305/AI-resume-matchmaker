"""
AI Resume Matcher - Streamlit UI
Run with: streamlit run app.py
"""

import streamlit as st
from matcher import extract_resume_text, get_match_report

st.set_page_config(page_title="AI Resume Matcher", page_icon="📄", layout="centered")

st.title("📄 AI Resume Matcher")
st.caption("Upload your resume and paste a job description to get an ATS-style match score.")

col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

with col2:
    jd_text = st.text_area("Paste Job Description", height=220, placeholder="Paste the full JD here...")

analyze_clicked = st.button("🔍 Analyze Match", type="primary", use_container_width=True)

if analyze_clicked:
    if not resume_file:
        st.error("Please upload a resume file.")
    elif not jd_text.strip():
        st.error("Please paste a job description.")
    else:
        with st.spinner("Extracting resume text..."):
            try:
                resume_text = extract_resume_text(resume_file)
            except Exception as e:
                st.error(f"Couldn't read the resume file: {e}")
                st.stop()

        if len(resume_text.strip()) < 50:
            st.warning("Very little text was extracted from the resume — check the file isn't a scanned image.")

        with st.spinner("Scoring against job description..."):
            try:
                report = get_match_report(resume_text, jd_text)
            except Exception as e:
                st.error(f"Something went wrong calling the AI model: {e}")
                st.stop()

        # --- Results ---
        st.divider()
        score = report.get("match_score", 0)
        st.metric("Match Score", f"{score}/100")
        st.progress(min(max(score, 0), 100) / 100)

        st.write(f"**Summary:** {report.get('summary', '')}")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("✅ Matched Keywords")
            for kw in report.get("matched_keywords", []):
                st.write(f"- {kw}")

        with c2:
            st.subheader("❌ Missing Keywords")
            for kw in report.get("missing_keywords", []):
                st.write(f"- {kw}")

        st.subheader("💡 Suggestions")
        for i, s in enumerate(report.get("suggestions", []), 1):
            st.write(f"{i}. {s}")

st.divider()
st.caption("Built with Python, OpenAI API, and Streamlit.")
