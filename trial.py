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
model = genai.GenerativeModel("gemini-2.5-pro")

# ---------------------------
# Modern CSS Styling
# ---------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
    }
    
    /* Main container with glassmorphism */
    .main .block-container {
        padding: 2rem 1rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        max-width: 1200px;
        margin: 2rem auto;
    }
    
    /* Header Styling */
    .main-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff, #e0e7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 1rem 0;
        text-shadow: 0 4px 20px rgba(255, 255, 255, 0.3);
        animation: fadeInUp 1s ease-out;
    }
    
    .sub-title {
        text-align: center;
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 2rem;
        font-weight: 400;
        animation: fadeInUp 1s ease-out 0.3s both;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        animation: slideInLeft 0.8s ease-out;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
        padding: 1.5rem 1rem;
    }
    
    /* Sidebar Title */
    .sidebar-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin: 1rem 0 2rem 0;
        background: linear-gradient(135deg, #ffffff, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Sidebar Cards */
    .sidebar-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .sidebar-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
        background: rgba(255, 255, 255, 0.08);
    }
    
    .sidebar-card h3 {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* File Uploader Styling */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(255, 255, 255, 0.5);
        background: rgba(255, 255, 255, 0.08);
    }
    
    [data-testid="stFileUploader"] label {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Text Area Styling */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 1rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.3) !important;
    }
    
    /* Radio Button Styling */
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255, 255, 255, 0.05) !important;
        color: rgba(255, 255, 255, 0.9) !important;
        padding: 0.8rem 1rem !important;
        border-radius: 10px !important;
        margin: 0.3rem 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
        cursor: pointer !important;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(167, 139, 250, 0.5) !important;
        transform: translateX(2px) !important;
    }
    
    /* Content Cards */
    .feedback-box {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        color: #2d3748;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .feedback-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        animation: pulse 2s infinite;
    }
    
    /* Subheader Styling */
    .stApp h2 {
        color: #ffffff !important;
        font-weight: 700 !important;
        margin: 2rem 0 1rem 0 !important;
        font-size: 2rem !important;
        text-align: center;
        background: linear-gradient(135deg, #ffffff, #e0e7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stApp h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
        margin: 1.5rem 0 1rem 0 !important;
        font-size: 1.5rem !important;
    }
    
    /* Button Styling */
    .stDownloadButton button, .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stDownloadButton button:hover, .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    }
    
    /* Icon Styling */
    .icon {
        display: inline-block;
        font-size: 1.2rem;
        margin-right: 0.5rem;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
    }
    
    /* Plotly Chart Container */
    .js-plotly-plot {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
    }
    
    /* Keyword display */
    .keyword-matched {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.2rem;
        font-weight: 500;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3);
    }
    
    .keyword-missing {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.2rem;
        font-weight: 500;
        box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3);
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .sub-title {
            font-size: 1rem;
        }
        
        .sidebar-card {
            margin-bottom: 1rem;
            padding: 1rem;
        }
        
        .feedback-box {
            padding: 1rem;
        }
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
# Sidebar Layout
# ---------------------------
with st.sidebar:
    # Profile Image with modern styling
    st.markdown("""
    <div style="display: flex; justify-content: center; margin: 1rem 0 2rem 0;">
        <div style="width: 120px; height: 120px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
            <div style="font-size: 3rem;">🤖</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">✨ Resume Analyzer</div>', unsafe_allow_html=True)

    # Upload Section
    with st.container():
        st.markdown('''
        <div class="sidebar-card">
            <h3><span class="icon">📤</span>Upload Resume</h3>
        </div>
        ''', unsafe_allow_html=True)
        file = st.file_uploader("Choose your resume file", type=["pdf", "docx", "txt"], label_visibility="collapsed")

    # Job Description
    with st.container():
        st.markdown('''
        <div class="sidebar-card">
            <h3><span class="icon">📝</span>Job Description</h3>
        </div>
        ''', unsafe_allow_html=True)
        job_desc = st.text_area("Paste job description here", placeholder="Enter the job description to optimize your resume...", label_visibility="collapsed", height=150)

    # Navigation
    with st.container():
        st.markdown('''
        <div class="sidebar-card">
            <h3><span class="icon">🧭</span>Navigation</h3>
        </div>
        ''', unsafe_allow_html=True)
        page = st.radio("Choose analysis type",
                        ["🏆 Resume Score", "📊 Detailed Feedback", "🎯 AI Tailored Resume", "✉️ Cover Letter Generator", "🔑 Keyword Optimization"], 
                        label_visibility="collapsed")

# ---------------------------
# Main Layout
# ---------------------------
st.markdown("<div class='main-title'>🚀 AI Resume Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Transform your resume with AI-powered insights and optimization</div>", unsafe_allow_html=True)

if file:
    with st.spinner("🔍 Analyzing your resume with AI..."):
        resume_text = extract_text(file)
        
    if resume_text:
        with st.spinner("🧠 AI is processing your resume..."):
            result = analyze_with_gemini(resume_text)
            
        if result:
            score = result.get("resume_score", 0)

            if page == "🏆 Resume Score":
                st.subheader("📈 Resume Performance Score")
                
                # Create custom gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Overall Resume Score", 'font': {'size': 24, 'color': '#2d3748'}},
                    delta={'reference': 80, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                    gauge={'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#2d3748"},
                          'bar': {'color': "#667eea", 'thickness': 0.8},
                          'bgcolor': "white",
                          'borderwidth': 3,
                          'bordercolor': "#e2e8f0",
                          'steps': [{'range': [0, 50], 'color': '#fed7d7'},
                                   {'range': [50, 80], 'color': '#feebc8'},
                                   {'range': [80, 100], 'color': '#c6f6d5'}],
                          'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.8, 'value': 90}}
                ))
                fig.update_layout(
                    height=400,
                    font={'color': "#2d3748", 'family': "Inter"},
                    paper_bgcolor="rgba(255,255,255,0.95)",
                    plot_bgcolor="rgba(255,255,255,0.95)"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Score interpretation
                if score >= 80:
                    st.success("🎉 Excellent! Your resume is highly optimized.")
                elif score >= 60:
                    st.warning("👍 Good resume! Some improvements can make it even better.")
                else:
                    st.error("🔧 Your resume needs significant improvements.")

            elif page == "📊 Detailed Feedback":
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("💪 Your Strengths")
                    for i, strength in enumerate(result.get("strengths", []), 1):
                        st.markdown(f"<div class='feedback-box'><strong>#{i}</strong> ⭐ {strength}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.subheader("🎯 Areas to Improve")
                    for i, improvement in enumerate(result.get("improvement_areas", []), 1):
                        st.markdown(f"<div class='feedback-box'><strong>#{i}</strong> 🔧 {improvement}</div>", unsafe_allow_html=True)
                
                # Recommended skills section
                if result.get("recommended_skills"):
                    st.subheader("🚀 Recommended Skills to Add")
                    skills_html = ""
                    for skill in result.get("recommended_skills", []):
                        skills_html += f'<span class="keyword-missing">{skill}</span> '
                    st.markdown(f"<div class='feedback-box'>{skills_html}</div>", unsafe_allow_html=True)

            elif page == "🎯 AI Tailored Resume":
                if job_desc:
                    with st.spinner("🤖 AI is tailoring your resume..."):
                        tailored_resume = tailor_resume(resume_text, job_desc)
                    
                    st.subheader("✨ AI-Optimized Resume")
                    st.text_area("Your tailored resume", tailored_resume, height=500, label_visibility="collapsed")
                    
                    # Download button
                    pdf_path = create_pdf(tailored_resume)
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="⬇️ Download Tailored Resume",
                            data=pdf_file.read(),
                            file_name="ai_tailored_resume.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.info("📝 Please provide a job description in the sidebar to generate a tailored resume.")

            elif page == "✉️ Cover Letter Generator":
                if job_desc:
                    with st.spinner("✍️ Crafting your perfect cover letter..."):
                        cover_letter = generate_cover_letter(resume_text, job_desc)
                    
                    st.subheader("📄 AI-Generated Cover Letter")
                    st.text_area("Your personalized cover letter", cover_letter, height=500, label_visibility="collapsed")
                    
                    # Download button
                    pdf_path = create_pdf(cover_letter)
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="⬇️ Download Cover Letter",
                            data=pdf_file.read(),
                            file_name="ai_cover_letter.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.info("📝 Please provide a job description in the sidebar to generate a cover letter.")

            elif page == "🔑 Keyword Optimization":
                if job_desc:
                    with st.spinner("🔍 Analyzing keywords..."):
                        matched, missing = keyword_optimization(resume_text, job_desc)
                    
                    st.subheader("🎯 Keyword Analysis Report")
                    
                    # Keyword match percentage gauge
                    total = len(matched) + len(missing)
                    if total > 0:
                        match_rate = len(matched) / total * 100
                        
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=match_rate,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Keyword Match Rate", 'font': {'size': 24, 'color': '#2d3748'}},
                            gauge={'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#2d3748"},
                                  'bar': {'color': "#10b981", 'thickness': 0.8},
                                  'bgcolor': "white",
                                  'borderwidth': 3,
                                  'bordercolor': "#e2e8f0",
                                  'steps': [{'range': [0, 40], 'color': '#fed7d7'},
                                           {'range': [40, 70], 'color': '#feebc8'},
                                           {'range': [70, 100], 'color': '#c6f6d5'}]}
                        ))
                        fig.update_layout(
                            height=350,
                            font={'color': "#2d3748", 'family': "Inter"},
                            paper_bgcolor="rgba(255,255,255,0.95)",
                            plot_bgcolor="rgba(255,255,255,0.95)"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Keywords display
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Keywords Found")
                        if matched:
                            matched_html = ""
                            for keyword in matched:
                                matched_html += f'<span class="keyword-matched">{keyword}</span> '
                            st.markdown(f"<div class='feedback-box'>{matched_html}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='feedback-box'>No keywords found in your resume.</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("❌ Missing Keywords")
                        if missing:
                            missing_html = ""
                            for keyword in missing:
                                missing_html += f'<span class="keyword-missing">{keyword}</span> '
                            st.markdown(f"<div class='feedback-box'>{missing_html}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='feedback-box'>Great! All important keywords are present.</div>", unsafe_allow_html=True)
                else:
                    st.info("📝 Please provide a job description in the sidebar to perform keyword analysis.")

        else:
            st.error("❌ Failed to analyze resume. Please try again.")
    else:
        st.error("❌ Could not extract text from the uploaded file. Please check the file format.")
else:
    # Welcome message when no file is uploaded
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.05); border-radius: 20px; backdrop-filter: blur(10px); margin: 2rem 0; border: 1px solid rgba(255,255,255,0.1);">
        <div style="font-size: 4rem; margin-bottom: 1rem; animation: pulse 2s infinite;">📄</div>
        <h3 style="color: white; margin-bottom: 1rem; font-weight: 600;">Welcome to AI Resume Analyzer!</h3>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem; line-height: 1.6; max-width: 600px; margin: 0 auto;">
            Upload your resume to get started with AI-powered analysis, optimization suggestions, 
            and personalized recommendations to boost your career prospects.
        </p>
        <div style="margin-top: 2rem; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px; min-width: 150px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏆</div>
                <div style="color: white; font-weight: 600;">Resume Scoring</div>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px; min-width: 150px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                <div style="color: white; font-weight: 600;">AI Optimization</div>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 12px; min-width: 150px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                <div style="color: white; font-weight: 600;">Detailed Analytics</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# Footer
# ---------------------------
st.markdown("""
<div style="margin-top: 4rem; padding: 2rem; text-align: center; background: rgba(255,255,255,0.05); border-radius: 16px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1);">
    <p style="color: rgba(255,255,255,0.6); margin: 0; font-size: 0.9rem;">
        🤖 Powered by Google Gemini AI • Built with ❤️ using Streamlit
    </p>
    <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
        <span style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 20px; color: rgba(255,255,255,0.8); font-size: 0.8rem;">
            ⚡ Real-time Analysis
        </span>
        <span style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 20px; color: rgba(255,255,255,0.8); font-size: 0.8rem;">
            🔒 Secure Processing
        </span>
        <span style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 20px; color: rgba(255,255,255,0.8); font-size: 0.8rem;">
            📱 Mobile Friendly
        </span>
    </div>
</div>
""", unsafe_allow_html=True)