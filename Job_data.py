# Resume Analyzer: Extracts skills and suggests improvements
import streamlit as st
import re
from PyPDF2 import PdfReader

IN_DEMAND_SKILLS = [
    'Python', 'Java', 'SQL', 'Machine Learning', 'Data Analysis', 'Communication',
    'Project Management', 'Cloud Computing', 'Leadership', 'Problem Solving',
    'Teamwork', 'AI', 'Deep Learning', 'NLP', 'Docker', 'Kubernetes', 'AWS', 'Azure'
]

ENHANCEMENT_TIPS = [
    "Add measurable achievements (e.g., 'Increased sales by 20%').",
    "Include certifications relevant to your field.",
    "Highlight leadership or teamwork experiences.",
    "Mention familiarity with latest tools/technologies.",
    "Tailor your resume for the job description.",
    "Use action verbs and keep formatting clean."
]

def extract_skills(resume_text):
    found_skills = set()
    for skill in IN_DEMAND_SKILLS:
        pattern = r'\\b' + re.escape(skill) + r'\\b'
        if re.search(pattern, resume_text, re.IGNORECASE):
            found_skills.add(skill)
    return list(found_skills)

def suggest_improvements(found_skills):
    missing_skills = [skill for skill in IN_DEMAND_SKILLS if skill not in found_skills]
    suggestions = []
    if missing_skills:
        suggestions.append(f"Consider learning or highlighting these in-demand skills: {', '.join(missing_skills[:5])}")
    suggestions.extend(ENHANCEMENT_TIPS)
    return suggestions

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def main():
    st.title("Resume Analyzer")
    st.write("Upload your resume as a PDF to analyze your skills and get enhancement suggestions.")

    uploaded_file = st.file_uploader("Choose a PDF resume", type=["pdf"])
    if uploaded_file is not None:
        resume_text = extract_text_from_pdf(uploaded_file)
        if resume_text:
            skills = extract_skills(resume_text)
            suggestions = suggest_improvements(skills)
            st.subheader("Skills found in resume:")
            st.write(', '.join(skills) if skills else "None detected.")
            st.subheader("Suggestions to enhance your resume:")
            for tip in suggestions:
                st.write("-", tip)
        else:
            st.error("Could not extract text from the PDF. Please try another file.")

if __name__ == "__main__":
    main()
JOB_DESCRIPTIONS = [
    {
        "id": "1",
        "title": "Data Scientist",
        "description": "Develop and implement machine learning models, analyze large datasets, and build predictive algorithms.",
        "skills": ["Python", "R", "SQL", "Machine Learning", "Data Analysis", "Pandas", "NumPy", "Scikit-learn", "Keras", "TensorFlow"],
        "keywords": ["analysis", "model", "data", "predictive", "algorithm", "statistics"]
    },
    {
        "id": "2",
        "title": "Full-Stack Developer",
        "description": "Design, develop, and maintain web applications using both front-end and back-end technologies.",
        "skills": ["JavaScript", "React", "Node.js", "Python", "Flask", "Django", "HTML", "CSS", "SQL", "MongoDB"],
        "keywords": ["web", "full-stack", "developer", "backend", "frontend", "API"]
    },
    {
        "id": "3",
        "title": "Technical Project Manager",
        "description": "Lead technical projects from conception to completion, manage resources, and communicate with stakeholders.",
        "skills": ["Project Management", "Agile", "Scrum", "JIRA", "Communication", "Leadership", "Budgeting", "Risk Management"],
        "keywords": ["project", "manager", "technical", "lead", "agile", "stakeholders"]
    },
    {
        "id": "4",
        "title": "UX/UI Designer",
        "description": "Create intuitive and aesthetically pleasing user interfaces and experiences for web and mobile applications.",
        "skills": ["Figma", "Sketch", "Adobe XD", "UI/UX Design", "Wireframing", "Prototyping", "User Research"],
        "keywords": ["design", "user", "interface", "experience", "UX", "UI", "prototyping"]
    }
]
