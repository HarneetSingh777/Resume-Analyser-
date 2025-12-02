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
model = genai.GenerativeModel("gemini-2.5-flash")

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

SKILL_GAP_PROMPT = """
You are an expert career advisor and industry analyst. Analyze this resume and provide a comprehensive skill gap analysis:

Resume:
{resume_text}

Job Role/Industry (if provided):
{job_role}

Provide analysis in JSON format with these keys:
- current_skills (list of skills found in resume)
- industry_required_skills (list of 8-12 skills required for this role/industry)
- skill_gaps (list of missing critical skills)
- emerging_skills (list of 4-6 trending skills in this field)
- certifications (list of objects with keys: name, platform, url, priority_level, estimated_duration)
- skill_match_percentage (0-100)
- career_level_assessment (entry/mid/senior)
- next_career_steps (list of 3-4 recommended career progression steps)

For certifications, include real courses from:
- Coursera (coursera.org)
- Udemy (udemy.com) 
- LinkedIn Learning (linkedin.com/learning)
- edX (edx.org)
- Pluralsight (pluralsight.com)

Priority levels: "Critical", "High", "Medium", "Nice-to-have"
Estimated duration: "1-2 weeks", "1 month", "2-3 months", "3-6 months"

Return ONLY valid JSON, no additional text.
"""

# ---------------------------
# AI Interview Chatbot Prompts
# ---------------------------
INTERVIEW_QUESTION_PROMPT = """
You are an experienced HR interviewer. Based on this resume, generate 5 relevant interview questions that would be appropriate for this candidate's experience level and field.

Resume:
{resume_text}

Generate questions that cover:
1. Technical skills and experience
2. Behavioral/situational questions
3. Career goals and motivation
4. Problem-solving abilities
5. Industry-specific knowledge

Return response in JSON format with key "questions" containing a list of question strings.
Return ONLY valid JSON, no additional text.
"""

INTERVIEW_ANALYSIS_PROMPT = """
You are an expert interview coach. Analyze this candidate's response to the interview question and provide constructive feedback.

Question: {question}
Candidate's Answer: {answer}

Provide analysis in JSON format with these keys:
- score (1-10 rating)
- strengths (list of positive aspects)
- areas_for_improvement (list of areas to improve)
- suggestions (list of specific improvement suggestions)
- overall_feedback (brief summary)

Return ONLY valid JSON, no additional text.
"""

CHATBOT_CONVERSATION_PROMPT = """
You are a friendly and professional AI interview coach. The candidate has uploaded their resume and you're having a conversation to help them prepare for interviews.

Resume Context:
{resume_text}

Conversation History:
{chat_history}

User Message: {user_message}

Respond as a helpful interview coach. Keep responses conversational, encouraging, and focused on interview preparation. Provide specific advice based on their resume when relevant.

Return ONLY your response text, no JSON formatting.
"""


# ---------------------------
# Helper Functions
# ---------------------------
import time
from google.api_core import exceptions

def safe_generate_content(prompt, max_retries=3, timeout=30):
    """Safely generate content with retry logic and error handling"""
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except exceptions.DeadlineExceeded:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                time.sleep(wait_time)
                continue
            else:
                return None
        except Exception as e:
            if "DNS" in str(e) or "timeout" in str(e).lower() or "connection" in str(e).lower():
                if attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 3)
                    continue
                else:
                    return None
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 2)
                continue
            else:
                return None
    return None

# ---------------------------
# AI Interview Chatbot Functions
# ---------------------------
def generate_interview_questions(resume_text):
    """Generate interview questions based on resume"""
    prompt = INTERVIEW_QUESTION_PROMPT.format(resume_text=resume_text)
    result = safe_generate_content(prompt)
    if result:
        try:
            raw_text = re.sub(r"^```json|```$", "", result, flags=re.MULTILINE).strip()
            return json.loads(raw_text)
        except Exception:
            return {"questions": ["Tell me about your background and experience.", 
                               "What are your key strengths?", 
                               "Describe a challenging project you worked on.", 
                               "Where do you see yourself in 5 years?", 
                               "Why are you interested in this role?"]}
    return None

def analyze_interview_response(question, answer):
    """Analyze candidate's response to interview question"""
    prompt = INTERVIEW_ANALYSIS_PROMPT.format(question=question, answer=answer)
    result = safe_generate_content(prompt)
    if result:
        try:
            raw_text = re.sub(r"^```json|```$", "", result, flags=re.MULTILINE).strip()
            return json.loads(raw_text)
        except Exception:
            return {
                "score": 7,
                "strengths": ["Provided a response", "Engaged with the question"],
                "areas_for_improvement": ["Could provide more specific examples"],
                "suggestions": ["Add concrete examples to support your points"],
                "overall_feedback": "Good effort, consider adding more detail and specific examples."
            }
    return None

def chatbot_conversation(resume_text, chat_history, user_message):
    """Handle chatbot conversation"""
    prompt = CHATBOT_CONVERSATION_PROMPT.format(
        resume_text=resume_text,
        chat_history=chat_history,
        user_message=user_message
    )
    result = safe_generate_content(prompt)
    return result if result else "I'm here to help you prepare for interviews. What would you like to discuss?"

# ---------------------------
# Session State Initialization
# ---------------------------
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'interview_questions' not in st.session_state:
    st.session_state.interview_questions = []
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'interview_scores' not in st.session_state:
    st.session_state.interview_scores = []
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0

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
def analyze_with_gemini(resume_text):
    """Analyze resume with Gemini AI and return structured results"""
    def _fallback(reason):
        st.warning(f"{reason} Showing a quick offline analysis instead.")
        return generate_fallback_analysis(resume_text)

    if not GEMINI_API_KEY:
        return _fallback("Gemini API key is missing or invalid.")

    if len(resume_text) > 8000:
        resume_text = resume_text[:8000] + "..."
    
    prompt = PROMPT.format(resume_text=resume_text)
    result = safe_generate_content(prompt)
    
    if result:
        raw_text = re.sub(r"^```json|```$", "", result, flags=re.MULTILINE).strip()
        try:
            return json.loads(raw_text)
        except Exception:
            st.error("⚠️ Could not parse Gemini response. Showing raw output below.")
            st.code(raw_text, language="json")
            return _fallback("Gemini returned an unexpected format.")
    else:
        return _fallback("Gemini could not be reached right now.")

# ---------------------------
# Tailor Resume
# ---------------------------
def tailor_resume(resume_text, job_description):
    """Generate tailored resume using Gemini AI"""
    prompt = TAILORING_PROMPT.format(resume_text=resume_text, job_description=job_description)
    result = safe_generate_content(prompt)
    return result.strip() if result else "Unable to generate tailored resume. Please try again."

# ---------------------------
# Cover Letter Generator
# ---------------------------
def generate_cover_letter(resume_text, job_description):
    """Generate cover letter using Gemini AI"""
    prompt = COVER_LETTER_PROMPT.format(resume_text=resume_text, job_description=job_description)
    result = safe_generate_content(prompt)
    return result.strip() if result else "Unable to generate cover letter. Please try again."

# ---------------------------
# Skill Gap Analysis
# ---------------------------
def analyze_skill_gaps(resume_text, job_role=""):
    """Analyze skill gaps using Gemini AI"""
    prompt = SKILL_GAP_PROMPT.format(resume_text=resume_text, job_role=job_role)
    result = safe_generate_content(prompt)
    if not result:
        return None
    raw_text = result.strip()
    raw_text = re.sub(r"^```json|```$", "", raw_text, flags=re.MULTILINE).strip()
    
    try:
        return json.loads(raw_text)
    except Exception as e:
        st.error(f"⚠️ Could not parse skill gap analysis. Error: {str(e)}")
        return None

def fallback_resume_score(resume_text):
    """Generate basic resume score when AI fails"""
    score = 0
    text_lower = resume_text.lower()
    
    # Check for contact information (20 points)
    if any(keyword in text_lower for keyword in ['email', '@', 'phone', 'contact']):
        score += 20
    
    # Check for experience section (25 points)
    if any(keyword in text_lower for keyword in ['experience', 'work', 'employment', 'career']):
        score += 25
    
    # Check for education section (20 points)
    if any(keyword in text_lower for keyword in ['education', 'degree', 'university', 'college']):
        score += 20
    
    # Check for skills section (20 points)
    if any(keyword in text_lower for keyword in ['skills', 'technical', 'proficient', 'expertise']):
        score += 20
    
    # Check for action verbs (10 points)
    action_verbs = ['managed', 'developed', 'created', 'implemented', 'designed', 'led', 'achieved']
    if any(verb in text_lower for verb in action_verbs):
        score += 10
    
    # Check resume length (5 points)
    if 200 <= len(resume_text.split()) <= 800:
        score += 5
    
    return min(score, 100)

def generate_fallback_analysis(resume_text):
    """Produce heuristic feedback when Gemini analysis is unavailable"""
    text_lower = resume_text.lower()
    score = fallback_resume_score(resume_text)
    structure_feedback = []
    strengths = []
    improvement_areas = []

    section_checks = [
        ("Professional summary", ["summary", "objective"], "Add a short professional summary at the top."),
        ("Experience", ["experience", "work history", "employment"], "Detail your work experience with bullet points and metrics."),
        ("Education", ["education", "university", "college", "degree"], "Highlight your education section with relevant coursework."),
        ("Skills", ["skill", "technical", "expertise"], "List a focused skills section that mirrors the roles you target."),
    ]

    for label, keywords, tip in section_checks:
        if any(keyword in text_lower for keyword in keywords):
            structure_feedback.append(f"✅ {label} section detected.")
            strengths.append(f"Includes a {label.lower()} that helps recruiters scan quickly.")
        else:
            structure_feedback.append(f"⚠️ Consider adding a dedicated {label.lower()} section.")
            improvement_areas.append(tip)

    word_count = len(resume_text.split())
    if word_count < 200:
        improvement_areas.append("Resume is quite short—expand on key accomplishments and responsibilities.")
    elif word_count > 900:
        improvement_areas.append("Resume is lengthy—condense older roles and keep bullets sharp.")
    else:
        strengths.append("Resume length is within a recruiter-friendly range.")

    if re.search(r"\d+%|\$|\b\d+\b", resume_text):
        strengths.append("Uses metrics to quantify impact.")
    else:
        improvement_areas.append("Incorporate measurable results (%, $, #) to strengthen achievements.")

    base_skills = ["Leadership", "Communication", "Problem Solving", "Stakeholder Management", "Data Literacy", "Project Planning"]
    recommended_skills = [skill for skill in base_skills if skill.lower() not in text_lower][:4]
    if not recommended_skills:
        recommended_skills = base_skills[:3]

    course_library = {
        "Leadership": [
            "Coursera – Strategic Leadership and Management",
            "LinkedIn Learning – Developing Executive Presence"
        ],
        "Communication": [
            "Udemy – Business Communication Skills",
            "LinkedIn Learning – Communicating with Confidence"
        ],
        "Problem Solving": [
            "Coursera – Creative Problem Solving",
            "edX – Critical Thinking & Problem-Solving"
        ],
        "Stakeholder Management": [
            "Udemy – Stakeholder Engagement Essentials",
            "Coursera – Project Management Principles and Practices"
        ],
        "Data Literacy": [
            "Coursera – Data Analysis with Excel",
            "LinkedIn Learning – Data Fluency"
        ],
        "Project Planning": [
            "Coursera – Initiating and Planning Projects",
            "edX – Project Management for Professionals"
        ],
    }

    recommended_courses = {}
    for skill in recommended_skills[:3]:
        courses = course_library.get(
            skill,
            [
                f"Coursera – {skill} Fundamentals",
                f"LinkedIn Learning – {skill} Essential Training",
            ],
        )
        recommended_courses[skill] = courses

    return {
        "resume_score": score,
        "structure_feedback": structure_feedback,
        "strengths": strengths or ["Shows initiative by outlining key experience and education."],
        "improvement_areas": improvement_areas or ["Polish formatting and emphasize accomplishments."],
        "recommended_skills": recommended_skills,
        "recommended_courses": recommended_courses,
        "analysis_source": "fallback",
    }

# ---------------------------
# Additional Helper Functions
# ---------------------------
def keyword_optimization(resume_text, job_description):
    """Analyze keyword match between resume and job description"""
    resume_words = set(resume_text.lower().split())
    job_words = set(job_description.lower().split())
    
    # Filter out common words
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
    job_keywords = [word for word in job_words if len(word) > 3 and word not in common_words]
    
    matched = [word for word in job_keywords if word in resume_words]
    missing = [word for word in job_keywords if word not in resume_words]
    
    return matched[:10], missing[:10]  # Return top 10 of each

def create_pdf(content):
    """Create PDF from text content"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=A4)
    
    # Simple text wrapping for PDF
    lines = content.split('\n')
    y_position = 750
    
    for line in lines:
        if y_position < 50:
            c.showPage()
            y_position = 750
        
        # Wrap long lines
        if len(line) > 80:
            words = line.split(' ')
            current_line = ''
            for word in words:
                if len(current_line + word) < 80:
                    current_line += word + ' '
                else:
                    c.drawString(50, y_position, current_line.strip())
                    y_position -= 15
                    current_line = word + ' '
            if current_line:
                c.drawString(50, y_position, current_line.strip())
                y_position -= 15
        else:
            c.drawString(50, y_position, line)
            y_position -= 15
    
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
                        ["🏆 Resume Score", "📊 Detailed Feedback", "📈 Skill Gap Analysis", "🎯 AI Tailored Resume", "✉️ Cover Letter Generator", "🔑 Keyword Optimization", "🤖 AI Interview Chatbot"], 
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

            elif page == "📈 Skill Gap Analysis":
                # Job role input for better analysis
                job_role = st.text_input("🎯 Target Job Role/Industry (optional)", 
                                       placeholder="e.g., Data Scientist, Software Engineer, Marketing Manager",
                                       help="Specify your target role for more accurate skill gap analysis")
                
                with st.spinner("🔍 Analyzing skill gaps and industry requirements..."):
                    skill_analysis = analyze_skill_gaps(resume_text, job_role)
                
                if skill_analysis:
                    # Skill Match Percentage
                    match_percentage = skill_analysis.get("skill_match_percentage", 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>🎯 Skill Match Score</h3>
                        <div class="score-circle">
                            <span class="score-number">{match_percentage}%</span>
                        </div>
                        <p>Industry Alignment</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Career Level Assessment
                    career_level = skill_analysis.get("career_level_assessment", "Unknown")
                    level_emoji = {"entry": "🌱", "mid": "🚀", "senior": "👑"}.get(career_level.lower(), "📊")
                    st.info(f"{level_emoji} **Career Level Assessment:** {career_level.title()} Level")
                    
                    # Skills Comparison
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Your Current Skills")
                        current_skills = skill_analysis.get("current_skills", [])
                        for skill in current_skills[:10]:  # Show top 10
                            st.markdown(f"<div class='feedback-box'>✓ {skill}</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("🎯 Industry Required Skills")
                        required_skills = skill_analysis.get("industry_required_skills", [])
                        for skill in required_skills:
                            st.markdown(f"<div class='feedback-box'>🔹 {skill}</div>", unsafe_allow_html=True)
                    
                    # Skill Gaps
                    skill_gaps = skill_analysis.get("skill_gaps", [])
                    if skill_gaps:
                        st.subheader("⚠️ Critical Skill Gaps")
                        gaps_html = ""
                        for gap in skill_gaps:
                            gaps_html += f'<span class="keyword-missing">{gap}</span> '
                        st.markdown(f"<div class='feedback-box'>{gaps_html}</div>", unsafe_allow_html=True)
                    
                    # Emerging Skills
                    emerging_skills = skill_analysis.get("emerging_skills", [])
                    if emerging_skills:
                        st.subheader("🔥 Trending Skills in Your Field")
                        emerging_html = ""
                        for skill in emerging_skills:
                            emerging_html += f'<span class="keyword-found">{skill}</span> '
                        st.markdown(f"<div class='feedback-box'>{emerging_html}</div>", unsafe_allow_html=True)
                    
                    # Certification Recommendations
                    certifications = skill_analysis.get("certifications", [])
                    if certifications:
                        st.subheader("🎓 Recommended Certifications & Courses")
                        
                        # Group by priority
                        priority_groups = {"Critical": [], "High": [], "Medium": [], "Nice-to-have": []}
                        for cert in certifications:
                            priority = cert.get("priority_level", "Medium")
                            priority_groups[priority].append(cert)
                        
                        for priority, certs in priority_groups.items():
                            if certs:
                                priority_emoji = {"Critical": "🚨", "High": "⭐", "Medium": "📚", "Nice-to-have": "💡"}
                                st.markdown(f"**{priority_emoji.get(priority, '📚')} {priority} Priority**")
                                
                                for cert in certs:
                                    platform_emoji = {
                                        "coursera.org": "🎓",
                                        "udemy.com": "📖", 
                                        "linkedin.com/learning": "💼",
                                        "edx.org": "🏛️",
                                        "pluralsight.com": "💻"
                                    }
                                    
                                    platform = cert.get("platform", "")
                                    emoji = next((v for k, v in platform_emoji.items() if k in platform), "🔗")
                                    
                                    st.markdown(f"""
                                    <div class='feedback-box'>
                                        <strong>{emoji} {cert.get('name', 'Course')}</strong><br>
                                        <small>⏱️ Duration: {cert.get('estimated_duration', 'N/A')} | 
                                        Platform: {cert.get('platform', 'N/A')}</small><br>
                                        <a href="{cert.get('url', '#')}" target="_blank" style="color: #667eea;">🔗 View Course</a>
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    # Career Progression Steps
                    career_steps = skill_analysis.get("next_career_steps", [])
                    if career_steps:
                        st.subheader("🚀 Recommended Career Steps")
                        for i, step in enumerate(career_steps, 1):
                            st.markdown(f"<div class='feedback-box'><strong>Step {i}:</strong> {step}</div>", unsafe_allow_html=True)
                
                else:
                    st.error("⚠️ Unable to perform skill gap analysis. Please try again.")

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

            elif page == "🤖 AI Interview Chatbot":
                st.subheader("🤖 AI Interview Practice Chatbot")
                st.markdown("<div class='feedback-box'>Practice your interview skills with our AI-powered chatbot that generates questions based on your resume.</div>", unsafe_allow_html=True)
                
                # Interview Mode Selection
                interview_mode = st.radio(
                    "Choose Interview Mode:",
                    ["💬 Conversational Chat", "📋 Structured Interview"],
                    horizontal=True
                )
                
                if interview_mode == "💬 Conversational Chat":
                    # Conversational Chat Mode
                    st.markdown("### 💬 Chat with AI Interview Coach")
                    
                    # Display chat history
                    if st.session_state.chat_history:
                        for i, message in enumerate(st.session_state.chat_history):
                            if message["role"] == "assistant":
                                st.markdown(f"""
                                <div style="background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #667eea;">
                                    <strong>🤖 AI Coach:</strong> {message["content"]}
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #10b981;">
                                    <strong>👤 You:</strong> {message["content"]}
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Chat input
                    user_input = st.text_input("💬 Type your message:", key="chat_input", placeholder="Ask me anything about interview preparation...")
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("Send 📤", key="send_chat"):
                            if user_input:
                                # Add user message to history
                                st.session_state.chat_history.append({"role": "user", "content": user_input})
                                
                                # Get AI response
                                chat_history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history[-5:]])
                                ai_response = chatbot_conversation(resume_text, chat_history_str, user_input)
                                
                                # Add AI response to history
                                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                                st.rerun()
                    
                    with col2:
                        if st.button("🔄 Reset Chat", key="reset_chat"):
                            st.session_state.chat_history = []
                            st.rerun()
                
                else:
                    # Structured Interview Mode
                    st.markdown("### 📋 Structured Interview Practice")
                    
                    # Generate questions if not already done
                    if not st.session_state.interview_questions:
                        with st.spinner("🤖 Generating interview questions based on your resume..."):
                            questions_data = generate_interview_questions(resume_text)
                            if questions_data and "questions" in questions_data:
                                st.session_state.interview_questions = questions_data["questions"]
                            else:
                                st.session_state.interview_questions = [
                                    "Tell me about your background and experience.",
                                    "What are your key strengths?",
                                    "Describe a challenging project you worked on.",
                                    "Where do you see yourself in 5 years?",
                                    "Why are you interested in this role?"
                                ]
                    
                    # Display current question
                    if st.session_state.question_index < len(st.session_state.interview_questions):
                        current_q = st.session_state.interview_questions[st.session_state.question_index]
                        st.session_state.current_question = current_q
                        
                        # Progress indicator
                        progress = (st.session_state.question_index + 1) / len(st.session_state.interview_questions)
                        st.progress(progress, text=f"Question {st.session_state.question_index + 1} of {len(st.session_state.interview_questions)}")
                        
                        st.markdown(f"""
                        <div style="background: rgba(102, 126, 234, 0.1); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border-left: 5px solid #667eea;">
                            <h4 style="color: #667eea; margin-bottom: 1rem;">🎤 Interview Question:</h4>
                            <p style="font-size: 1.1rem; line-height: 1.6; margin: 0;">{current_q}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Answer input
                        user_answer = st.text_area("✍️ Your Answer:", height=150, key=f"answer_{st.session_state.question_index}", placeholder="Take your time to provide a thoughtful response...")
                        
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            if st.button("📝 Submit Answer", key="submit_answer"):
                                if user_answer.strip():
                                    with st.spinner("🤖 Analyzing your response..."):
                                        analysis = analyze_interview_response(current_q, user_answer)
                                        if analysis:
                                            st.session_state.interview_scores.append({
                                                "question": current_q,
                                                "answer": user_answer,
                                                "analysis": analysis
                                            })
                                            st.session_state.question_index += 1
                                            st.rerun()
                                else:
                                    st.warning("Please provide an answer before submitting.")
                        
                        with col2:
                            if st.button("⏭️ Skip Question", key="skip_question"):
                                st.session_state.question_index += 1
                                st.rerun()
                        
                        with col3:
                            if st.button("🔄 Reset", key="reset_interview"):
                                st.session_state.interview_questions = []
                                st.session_state.question_index = 0
                                st.session_state.interview_scores = []
                                st.rerun()
                    
                    else:
                        # Interview completed
                        st.success("🎉 Interview Practice Completed!")
                        
                        if st.session_state.interview_scores:
                            # Calculate overall score
                            total_score = sum([score["analysis"].get("score", 0) for score in st.session_state.interview_scores])
                            avg_score = total_score / len(st.session_state.interview_scores)
                            
                            # Display overall performance
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number+delta",
                                value=avg_score,
                                domain={'x': [0, 1], 'y': [0, 1]},
                                title={'text': "Overall Interview Score", 'font': {'size': 20, 'color': '#2d3748'}},
                                gauge={'axis': {'range': [0, 10], 'tickwidth': 2, 'tickcolor': "#2d3748"},
                                      'bar': {'color': "#667eea", 'thickness': 0.8},
                                      'bgcolor': "white",
                                      'borderwidth': 3,
                                      'bordercolor': "#e2e8f0",
                                      'steps': [{'range': [0, 4], 'color': '#fed7d7'},
                                               {'range': [4, 7], 'color': '#feebc8'},
                                               {'range': [7, 10], 'color': '#c6f6d5'}]}
                            ))
                            fig.update_layout(
                                height=300,
                                font={'color': "#2d3748", 'family': "Inter"},
                                paper_bgcolor="rgba(255,255,255,0.95)",
                                plot_bgcolor="rgba(255,255,255,0.95)"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Detailed feedback
                            st.subheader("📊 Detailed Feedback")
                            for i, score_data in enumerate(st.session_state.interview_scores, 1):
                                with st.expander(f"Question {i}: {score_data['question'][:50]}..."):
                                    analysis = score_data["analysis"]
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Score", f"{analysis.get('score', 0)}/10")
                                    
                                    st.markdown("**Your Answer:**")
                                    st.text_area("", score_data["answer"], height=100, disabled=True, key=f"review_answer_{i}")
                                    
                                    if "strengths" in analysis:
                                        st.markdown("**✅ Strengths:**")
                                        for strength in analysis["strengths"]:
                                            st.markdown(f"• {strength}")
                                    
                                    if "areas_for_improvement" in analysis:
                                        st.markdown("**📈 Areas for Improvement:**")
                                        for improvement in analysis["areas_for_improvement"]:
                                            st.markdown(f"• {improvement}")
                                    
                                    if "suggestions" in analysis:
                                        st.markdown("**💡 Suggestions:**")
                                        for suggestion in analysis["suggestions"]:
                                            st.markdown(f"• {suggestion}")
                        
                        if st.button("🔄 Start New Interview", key="new_interview"):
                            st.session_state.interview_questions = []
                            st.session_state.question_index = 0
                            st.session_state.interview_scores = []
                            st.rerun()

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
