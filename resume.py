import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
import tempfile

# Load environment variables
load_dotenv()

# Configure the API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set up the generative model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

# Function to generate a formatted resume
def generate_resume(personal_info, education, experience, skills, projects, extracurricular):
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    f"Generate a professional resume using the following details:\n\n"
                    f"Personal Information:\n{personal_info}\n\n"
                    f"Education:\n{education}\n\n"
                    f"Work Experience:\n{experience}\n\n"
                    f"Skills:\n{skills}\n\n"
                    f"Projects:\n{projects}\n\n"
                    f"Extracurricular Activities:\n{extracurricular}"
                ],
            },
        ]
    )
    
    response = chat_session.send_message("Format as a professional resume.")
    return response.text

# Function to save resume to PDF
def save_resume_to_pdf(resume_text):
    # Remove asterisks (*) from the content
    cleaned_text = resume_text.replace("*", "")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Set global margins
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)

    # Title - Center aligned with larger font size
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, "Resume", ln=True, align="C")

    # Add some spacing
    pdf.ln(10)

    # Set section title formatting
    def add_section_title(title):
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(0, 102, 204)  # Blue color for headings
        pdf.cell(0, 10, title, ln=True)
        pdf.ln(5)  # Add spacing after section title

    # Set body text formatting
    def add_body_text(content):
        pdf.set_font("Arial", "", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, content)

    # Split the cleaned text into sections and format accordingly
    sections = cleaned_text.split("**")
    for section in sections:
        if section.strip():
            if ":" not in section:  # If it looks like a title
                add_section_title(section.strip())
            else:  # If it looks like content
                add_body_text(section.strip())

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf_output_path = tmp_file.name
        pdf.output(pdf_output_path)

    return pdf_output_path


# Streamlit app
def main():
    st.title("AI-Powered Resume Builder")

    # Personal Information
    st.header("Personal Information")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    linkedin = st.text_input("LinkedIn Profile URL")
    github = st.text_input("GitHub Profile URL")

    # Format personal information to appear one below the other
    personal_info = (
        f"Full Name: {name}\n"
        f"Contact Number: {phone}\n"
        f"Email Address: {email}\n"
        f"LinkedIn Profile: {linkedin}\n"
        f"GitHub Profile: {github}\n"
    )

    # Education
    st.header("Education")
    education_entries = []
    num_edu = st.number_input("Number of Education Entries", min_value=1, max_value=5, step=1, value=1)
    for i in range(num_edu):
        degree = st.text_input(f"Degree and Major (Entry {i+1})", key=f"degree_{i}")
        school = st.text_input(f"School (Entry {i+1})", key=f"school_{i}")
        college = st.text_input(f"College (Entry {i+1})", key=f"college_{i}")
        grad_year = st.text_input(f"Graduation Year (Entry {i+1})", key=f"grad_year_{i}")
        education_entries.append(f"{degree} from {school}, {college} - {grad_year}")
    education = "\n".join(education_entries)

    # Work Experience
    st.header("Work Experience")
    experience_entries = []
    num_exp = st.number_input("Number of Work Experiences", min_value=0, max_value=5, step=1, value=0)
    for i in range(num_exp):
        position = st.text_input(f"Job Title/Position (Entry {i+1})", key=f"position_{i}")
        company = st.text_input(f"Company Name (Entry {i+1})", key=f"company_{i}")
        duration = st.text_input(f"Duration (Entry {i+1})", key=f"duration_{i}")
        description = st.text_area(f"Description (Entry {i+1})", key=f"description_{i}")
        experience_entries.append(f"{position}, {company} ({duration})\n  - {description}")
    experience = "\n".join(experience_entries)

    # Skills
    st.header("Skills")
    skills = st.text_area("Enter your skills, separated by commas")

    # Projects
    st.header("Projects")
    project_entries = []
    num_projects = st.number_input("Number of Projects", min_value=1, max_value=5, step=1, value=1)
    for i in range(num_projects):
        project_name = st.text_input(f"Project Name (Entry {i+1})", key=f"project_name_{i}")
        project_description = st.text_area(f"Description (Entry {i+1})", key=f"project_description_{i}")
        project_entries.append(f"{project_name} - {project_description}")
    projects = "\n".join(project_entries)

    # Extracurricular Activities
    st.header("Extracurricular Activities")
    extracurricular = st.text_area("Enter your extracurricular activities, separated by commas")

    # Generate Resume Button
    if st.button("Generate Resume"):
        with st.spinner("Generating resume..."):
            resume_text = generate_resume(personal_info, education, experience, skills, projects, extracurricular)
            st.subheader("Resume")
            st.write(resume_text)

            # Save resume as PDF and provide download link
            pdf_path = save_resume_to_pdf(resume_text)
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Resume as PDF",
                    data=pdf_file,
                    file_name="Resume.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    main()
