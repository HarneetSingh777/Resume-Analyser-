import os

def load_resume_data(resume_input):
  """
  Loads resume data from a file path or text input.

  Args:
    resume_input: A string representing either a file path to the resume
                  or the resume content as text.

  Returns:
    A string containing the resume content, or None if the input is invalid.
  """
  if os.path.isfile(resume_input):
    try:
      with open(resume_input, 'r', encoding='utf-8') as f:
        return f.read()
    except Exception as e:
      print(f"Error reading file: {e}")
      return None
  else:
    # Assume the input is text if it's not a file
    return resume_input

# Example usage (for testing purposes)
# resume_file_path = 'path/to/your/resume.txt' # Replace with a real path
# resume_text_input = "This is the content of my resume."
#
# file_resume_content = load_resume_data(resume_file_path)
# text_resume_content = load_resume_data(resume_text_input)
#
# if file_resume_content:
#   print("Resume content from file loaded successfully.")
#   # print(file_resume_content)
#
# if text_resume_content:
#   print("Resume content from text loaded successfully.")
#   # print(text_resume_content)

def extract_text_from_resume(resume_content):
  """
  Extracts text content from the loaded resume.

  Args:
    resume_content: A string containing the raw resume content.

  Returns:
    A string containing the extracted text content.
  """
  # In this version, we assume the input is already text.
  # Future versions could add logic here to handle different file formats
  # like PDF or DOCX using appropriate libraries.
  return resume_content

# Example usage (assuming resume_content is already loaded from the previous step)
# extracted_text = extract_text_from_resume(text_resume_content)
# if extracted_text:
#   print("Text extracted successfully.")
#   # print(extracted_text)

def identify_skills(resume_text):
  """
  Identifies key skills within the extracted resume text.

  Args:
    resume_text: A string containing the extracted text content of the resume.

  Returns:
    A list of identified skills found in the resume.
  """
  # Predefined list of common technical and soft skills.
  # This list can be expanded based on specific requirements.
  predefined_skills = [
      "python", "java", "c++", "javascript", "sql", "r", "excel",
      "data analysis", "machine learning", "deep learning", "natural language processing",
      "communication", "teamwork", "leadership", "problem-solving", "critical thinking",
      "project management", "agile", "scrum", "cloud computing", "aws", "azure", "google cloud"
  ]

  identified_skills = []
  resume_text_lower = resume_text.lower()

  for skill in predefined_skills:
    if skill in resume_text_lower:
      identified_skills.append(skill)

  return identified_skills

# Example usage (assuming extracted_text is available from the previous step)
# sample_resume_text = "Experienced data analyst with strong skills in Python, SQL, and machine learning. Excellent communication and problem-solving abilities."
# found_skills = identify_skills(sample_resume_text)

import re

def analyze_resume_content(resume_text):
  """
  Analyzes resume content to extract sections like experience, education, etc.

  Args:
    resume_text: A string containing the extracted text content of the resume.

  Returns:
    A dictionary containing the extracted content for each identified section.
  """
  analysis = {}
  # Define patterns for common sections. This can be expanded.
  section_patterns = {
      "Experience": r"experience|work experience|professional experience",
      "Education": r"education",
      "Projects": r"projects",
      "Summary": r"summary|objective",
      "Skills": r"skills|technical skills"
  }

  # Convert the entire resume text to lowercase for case-insensitive matching
  resume_text_lower = resume_text.lower()

  # Find the start and end indices of each section
  section_indices = []
  for section, pattern in section_patterns.items():
      for match in re.finditer(pattern, resume_text_lower):
          section_indices.append((match.start(), section))

  # Sort the sections by their start index
  section_indices.sort()

  # Extract content for each section
  for i in range(len(section_indices)):
      start_index, section_name = section_indices[i]
      end_index = section_indices[i+1][0] if i+1 < len(section_indices) else len(resume_text)
      analysis[section_name] = resume_text[start_index:end_index].strip()

  # If no sections were found using the patterns, return the whole text under a general key
  if not analysis:
      analysis["Full Content"] = resume_text.strip()


  return analysis

# Example usage (assuming extracted_text is available from the previous step)
# sample_resume_text_for_analysis = """
# Summary: Highly motivated individual with a strong background in data analysis.
#
# Experience:
# Data Analyst at ABC Corp (2020-Present)
# - Analyzed large datasets using Python and SQL.
# - Developed dashboards for reporting.
#
# Education:
# Bachelor of Science in Computer Science from XYZ University (2016-2020)
#
# Skills: Python, SQL, Machine Learning
# """
#
# analyzed_content = analyze_resume_content(sample_resume_text_for_analysis)
# print("Analyzed Content:", analyzed_content)

def generate_feedback(identified_skills, analyzed_content):
  """
  Generates feedback based on identified skills and overall analysis.

  Args:
    identified_skills: A list of identified skills.
    analyzed_content: A dictionary containing analyzed resume sections.

  Returns:
    A list of feedback messages.
  """
  feedback_list = []

  # Step 3: Acknowledge identified skills
  if identified_skills:
    feedback_list.append(f"Great job! We identified the following skills in your resume: {', '.join(identified_skills)}.")
  else:
    # Step 6: Suggest including relevant skills if none were found
    feedback_list.append("We couldn't identify specific skills in your resume. Consider adding a dedicated 'Skills' section or highlighting your skills within your experience descriptions.")


  # Step 4: Indicate sections found
  if analyzed_content:
    feedback_list.append("We analyzed your resume and found the following sections:")
    for section in analyzed_content.keys():
      feedback_list.append(f"- {section}")
  else:
      feedback_list.append("We were unable to identify distinct sections in your resume. Organizing your resume with clear headings for sections like 'Experience', 'Education', and 'Skills' can improve readability.")


  # Step 5: Suggest missing or sections to elaborate upon
  key_sections = ["Experience", "Education", "Skills"]
  found_sections = analyzed_content.keys()
  missing_sections = [section for section in key_sections if section not in found_sections]

  if missing_sections:
    feedback_list.append(f"Consider adding or elaborating on the following key sections: {', '.join(missing_sections)}.")

  # Step 7: Add a general feedback message
  feedback_list.append("Remember to review and refine your resume for clarity, conciseness, and relevance to the jobs you're applying for. Good luck!")

  return feedback_list

# Example Usage (assuming identified_skills and analyzed_content are available)
# sample_identified_skills = ["python", "sql", "machine learning"]
# sample_analyzed_content = {
#     "Summary": "...",
#     "Experience": "...",
#     "Education": "..."
# }
#
# feedback = generate_feedback(sample_identified_skills, sample_analyzed_content)
# for message in feedback:
#   print(message)

def analyze_resume(resume_input):
  """
  Analyzes a resume and generates feedback.

  Args:
    resume_input: A string representing either a file path to the resume
                  or the resume content as text.

  Returns:
    A dictionary containing the identified skills and feedback messages,
    or None if the resume could not be processed.
  """
  # 1. Load and read the resume
  resume_content = load_resume_data(resume_input)
  if not resume_content:
    return {"error": "Could not load resume data."}

  # 2. Extract text
  extracted_text = extract_text_from_resume(resume_content)

  # 3. Identify key skills
  identified_skills = identify_skills(extracted_text)

  # 4. Analyze resume content
  analyzed_content = analyze_resume_content(extracted_text)

  # 5. Provide feedback
  feedback = generate_feedback(identified_skills, analyzed_content)

  return {
      "identified_skills": identified_skills,
      "feedback": feedback
  }

# Example Usage:
# Assuming 'path/to/your/resume.txt' is a valid file path or resume_text is a string with resume content
# analysis_results = analyze_resume('path/to/your/resume.txt')
# # or
# # analysis_results = analyze_resume("This is the content of my resume with Python and SQL skills.")

# if "error" in analysis_results:
#   print(analysis_results["error"])
# else:
#   print("Identified Skills:", analysis_results["identified_skills"])
#   print("\nFeedback:")
#   for message in analysis_results["feedback"]:
#     print(message)