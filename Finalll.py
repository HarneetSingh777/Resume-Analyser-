import streamlit as st
import pdfplumber
import docx2txt
import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------------------
# Custom CSS Styling
# ---------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(160deg, #e0f7fa, #f4f6f9);
    font-family: 'Arial', sans-serif;
}
.title {
    text-align: center;
    font-size: 48px;
    font-weight: bold;
    color: #4a148c;
    margin-top: 20px;
}
.subtitle {
    text-align: center;
    font-size: 20px;
    color: #1a237e;
    margin-bottom: 40px;
}
.upload-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.12);
    text-align: center;
    margin-bottom: 40px;
}
.feedback-box {
    background: #ffffff;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 20px;
    box-shadow: 0px 6px 12px rgba(0,0,0,0.08);
    color: #1a1a1a;
}
.strengths { border-left: 5px solid #2e7d32; }
.improvements { border-left: 5px solid #f9a825; }
.skills { border-left: 5px solid #1565c0; }
.section-title {
    font-size: 26px;
    font-weight: bold;
    margin-top: 30px;
    margin-bottom: 15px;
    color: #4a148c;
}
.progress-bar {
    height: 25px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)



# ---------------------------
# Prompt Template
# ---------------------------
PROMPT = """
You are an expert career coach. Analyze this resume text:

{resume_text}

IMPORTANT:
- Reply ONLY with a valid JSON object.
- Do NOT include explanations, markdown, or extra text.
- Ensure keys are exactly:
  resume_score (int 0–100),
  structure_feedback (list of strings),
  strengths (list of strings),
  improvement_areas (list of strings),
  recommended_skills (list of strings),
  recommended_courses (dict with skill: list of 2 courses)
"""

# ---------------------------
# File Extraction
# ---------------------------
def extract_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = docx2txt.process(file)
    elif file.type == "text/plain":
        text = file.read().decode("utf-8")
    return text

# ---------------------------
# Gemini Analysis (Safe JSON)
# ---------------------------
def analyze_with_gemini(text):
    prompt = PROMPT.format(resume_text=text)
    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Remove ```json or ``` wrappers if Gemini adds them
    raw_text = re.sub(r"^```json|```$", "", raw_text, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw_text)
    except Exception:
        st.error("⚠️ Could not parse Gemini response. Showing raw output below.")
        st.code(raw_text, language="json")
        return {}

# ---------------------------
# Streamlit UI
# ---------------------------
st.markdown("<div class='title'>📄 Resume Analyzer with Gemini AI</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Upload your resume and get instant AI-powered feedback</div>", unsafe_allow_html=True)

file = st.file_uploader("Upload Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

if file:
    resume_text = extract_text(file)

    if resume_text:
        st.info("Analyzing resume with Gemini AI... ⏳")

        result = analyze_with_gemini(resume_text)

        if result:
            # Resume Score
            score = result.get("resume_score", None)
            if score is not None:
                st.markdown("<div class='section-title'>🏆 Resume Score</div>", unsafe_allow_html=True)
                st.progress(score / 100)
                st.success(f"Your Resume Score: {score}/100")

            # Structure Feedback
            st.markdown("<div class='section-title'>📌 Structure Feedback</div>", unsafe_allow_html=True)
            for msg in result.get("structure_feedback", []):
                st.markdown(f"<div class='feedback-box'>✅ {msg}</div>", unsafe_allow_html=True)

            # Strengths
            st.markdown("<div class='section-title'>💪 Strengths</div>", unsafe_allow_html=True)
            for s in result.get("strengths", []):
                st.markdown(f"<div class='feedback-box'>⭐ {s}</div>", unsafe_allow_html=True)

            # Areas to Improve
            st.markdown("<div class='section-title'>⚠️ Areas to Improve</div>", unsafe_allow_html=True)
            for area in result.get("improvement_areas", []):
                st.markdown(f"<div class='feedback-box'>🔧 {area}</div>", unsafe_allow_html=True)

            # Recommended Skills & Courses
            st.markdown("<div class='section-title'>🚀 Recommended Skills & Courses</div>", unsafe_allow_html=True)
            for skill, courses in result.get("recommended_courses", {}).items():
                st.markdown(f"<div class='feedback-box'><b>{skill}</b>: {', '.join(courses)}</div>", unsafe_allow_html=True)
