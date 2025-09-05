import streamlit as st
import pdfplumber
import docx2txt
import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile
import plotly.graph_objects as go

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
st.markdown(
    """
    <style>
    body {
        background: url('/Users/macbook/Documents/Resume analyzer/pexels-umkreisel-app-956999.jpg');
        background-size: cover;
        font-family: 'Arial', sans-serif;
    }
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        color: #4a148c;
        margin-top: 10px;
    }
    .sub-title {
        text-align: center;
        font-size: 18px;
        color: #1a237e;
        margin-bottom: 20px;
    }
    .feedback-box {
        background: #ffffff;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0px 6px 12px rgba(0,0,0,0.08);
        color: #1a1a1a;
        animation: fadeIn 1s ease-in-out;
    }
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Prompt Templates
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

TAILOR_PROMPT = """
You are an expert resume writer. Rewrite the following resume:

{resume_text}

To align it with this job description:

{job_description}

IMPORTANT:
- Keep the format professional and ATS-friendly.
- Highlight relevant experiences, skills, and keywords from the job description.
- Do NOT fabricate experiences.
- Return only the improved resume text (no explanations).
"""

COVER_LETTER_PROMPT = """
You are an expert career consultant. Write a professional cover letter:
- Base it on this resume:
{resume_text}

- Tailor it for this job description:
{job_description}

IMPORTANT:
- Make it ATS-friendly and concise (max 400 words).
- Keep a professional tone.
- Highlight relevant experiences without fabricating.
- Return only the cover letter text.
"""

KEYWORD_PROMPT = """
Extract the top 15 keywords (skills, tools, certifications, job-related terms) from this job description:

{job_description}

Return ONLY a valid JSON list, e.g. ["Python", "Data Analysis", "Machine Learning"]
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
# Gemini Analysis
# ---------------------------
def analyze_with_gemini(text):
    prompt = PROMPT.format(resume_text=text)
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    raw_text = re.sub(r"^```json|```$", "", raw_text, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw_text)
    except Exception:
        st.error("⚠️ Could not parse Gemini response. Showing raw output below.")
        st.code(raw_text, language="json")
        return {}

# ---------------------------
# Tailor Resume
# ---------------------------
def tailor_resume(resume_text, job_description):
    prompt = TAILOR_PROMPT.format(resume_text=resume_text, job_description=job_description)
    response = model.generate_content(prompt)
    return response.text.strip()

# ---------------------------
# Cover Letter Generator
# ---------------------------
def generate_cover_letter(resume_text, job_description):
    prompt = COVER_LETTER_PROMPT.format(resume_text=resume_text, job_description=job_description)
    response = model.generate_content(prompt)
    return response.text.strip()

# ---------------------------
# Keyword Optimization
# ---------------------------
def keyword_optimization(resume_text, job_description):
    prompt = KEYWORD_PROMPT.format(job_description=job_description)
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    raw_text = re.sub(r"^```json|```$", "", raw_text, flags=re.MULTILINE).strip()

    keywords = []
    try:
        keywords = json.loads(raw_text)
    except:
        keywords = re.findall(r"\b[A-Z][a-zA-Z0-9+/#&-]{2,}\b", job_description)

    resume_lower = resume_text.lower()
    matched = [kw for kw in keywords if kw.lower() in resume_lower]
    missing = [kw for kw in keywords if kw.lower() not in resume_lower]

    return matched, missing

# ---------------------------
# Generate PDF
# ---------------------------
def create_pdf(text):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=A4)
    width, height = A4
    y = height - 50
    for line in text.split("\n"):
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, line)
        y -= 15
    c.save()
    return temp_file.name

# ---------------------------
# Sidebar
# ---------------------------
# ---------------------------
# Enhanced Sidebar Styling
# ---------------------------
st.markdown("""
<style>
/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #1e1e2f;
    padding: 25px 20px;  /* more breathing room */
}

/* Sidebar title */
.sidebar-title {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    text-align: center;
    margin: 20px 0 25px 0; /* more space top and bottom */
}

/* Card container */
.sidebar-card {
    background: #2a2a3d;
    padding: 18px 15px;  /* more inner spacing */
    border-radius: 14px;
    margin-bottom: 22px;  /* more space between sections */
    box-shadow: 0px 4px 12px rgba(0,0,0,0.25);
}

/* Label text inside cards */
.sidebar-card label {
    color: #cfcfd6 !important;
    font-weight: 600;
    margin-bottom: 10px;
    display: block;
}

/* File uploader adjustments */
section[data-testid="stFileUploader"] {
    margin-top: 12px;
}

/* Text area adjustments */
textarea {
    border-radius: 10px !important;
    padding: 10px !important;
}

/* Radio buttons */
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 10px 14px;  /* more click space */
    border-radius: 12px;
    margin-bottom: 8px;
    transition: all 0.2s ease-in-out;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background-color: #3b3b52;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar Layout
# ---------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135755.png", use_container_width=True)

    st.markdown('<div class="sidebar-title">📂 Resume Analyzer</div>', unsafe_allow_html=True)

    # Upload Section
    with st.container():
        st.markdown('<div class="sidebar-card">📤 <b>Upload Resume</b></div>', unsafe_allow_html=True)
        file = st.file_uploader("", type=["pdf", "docx", "txt"])

    # Job Description
    with st.container():
        st.markdown('<div class="sidebar-card">📝 <b>Paste Job Description</b></div>', unsafe_allow_html=True)
        job_desc = st.text_area("", placeholder="Enter the job description here...")

    # Navigation
    with st.container():
        st.markdown('<div class="sidebar-card">🧭 <b>Navigate</b></div>', unsafe_allow_html=True)
        page = st.radio("",
                        ["🏆 Resume Score", "📌 Feedback", "🎯 Tailored Resume", "✉️ Cover Letter", "🔑 Keywords"])


# ---------------------------
# Main Layout
# ---------------------------
st.markdown("<div class='main-title'>📄🕵🏼‍♂️ Resume Analyzer with Gemini AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Upload your resume and explore insights</div>", unsafe_allow_html=True)

if file:
    resume_text = extract_text(file)
    if resume_text:
        result = analyze_with_gemini(resume_text)
        if result:
            score = result.get("resume_score", 0)

            if page == "🏆 Resume Score":
                st.subheader("Resume Score")
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "purple"}},
                    title={'text': "Overall Score"}
                ))
                st.plotly_chart(fig, use_container_width=True)

            elif page == "📌 Feedback":
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Strengths")
                    for s in result.get("strengths", []):
                        st.markdown(f"<div class='feedback-box'>⭐ {s}</div>", unsafe_allow_html=True)
                with col2:
                    st.subheader("Areas to Improve")
                    for imp in result.get("improvement_areas", []):
                        st.markdown(f"<div class='feedback-box'>🔧 {imp}</div>", unsafe_allow_html=True)

            elif page == "🎯 Tailored Resume" and job_desc:
                tailored_resume = tailor_resume(resume_text, job_desc)
                st.subheader("Tailored Resume Preview")
                st.text_area("", tailored_resume, height=400)
                pdf_path = create_pdf(tailored_resume)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button("⬇️ Download Tailored Resume", pdf_file, "tailored_resume.pdf")

            elif page == "✉️ Cover Letter" and job_desc:
                cover_letter = generate_cover_letter(resume_text, job_desc)
                st.subheader("Cover Letter Preview")
                st.text_area("", cover_letter, height=400)
                pdf_path = create_pdf(cover_letter)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button("⬇️ Download Cover Letter", pdf_file, "cover_letter.pdf")

            elif page == "🔑 Keywords" and job_desc:
                matched, missing = keyword_optimization(resume_text, job_desc)
                st.subheader("Keyword Optimization")
                total = len(matched) + len(missing)
                if total > 0:
                    match_rate = len(matched) / total * 100
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=match_rate,
                        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "green"}},
                        title={'text': "Keyword Match %"}
                    ))
                    st.plotly_chart(fig, use_container_width=True)
                st.markdown("**✅ Matched:** " + (", ".join(matched) if matched else "None"))
                st.markdown("**❌ Missing:** " + (", ".join(missing) if missing else "None"))
