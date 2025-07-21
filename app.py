import streamlit as st
import os
import json
from openai import OpenAI
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from pdf2image import convert_from_bytes
import io
import base64
import requests


load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Ensure the applicant_data and applicant_score directories exist
if not os.path.exists("applicant_data"):
    os.makedirs("applicant_data")

if not os.path.exists("applicant_score"):
    os.makedirs("applicant_score")

# Read vacancy.md file
def read_vacancy():
    if os.path.exists("vacancy.md"):
        with open("vacancy.md", "r") as file:
            return file.read()
    else:
        return "The vacancy.md file does not exist. Please add the file to the application directory."
    
def pdf_to_images(pdf_file):
    try:
        return convert_from_bytes(pdf_file.read())
    except Exception as e:
        return f"Error converting PDF to images: {str(e)}"
    
def extract_text_from_image(img_base64: str) -> str:
    """Extract text from simple document image"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an OCR assistant. Extract all text from the image and format it properly as markdown. Preserve paragraph structure, headings, bullet points, and tables as much as possible.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content
    
def extract_text_with_ocr(images):
    texts = []

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    for idx, image in enumerate(images):
        try:
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode()

            texts.append(extract_text_from_image(image_base64))

        except Exception as e:
            texts.append(f"Error on page {idx + 1}: {str(e)}")

    return "\n".join(texts)


# Extract text from PDF
def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

# Extract information from document using OpenAI API
def extract_information(document_content):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Extract the following fields with json format from this document: name, email, phone_number, Education (degree and GPA), skills, certification, projects, experience (job_title, month_count).\n\nDocument:\n{document_content}"}
            ]
        )
        return completion.choices[0].message.content.replace('json','').replace('```','')
    except Exception as e:
        return json.dumps({"error": str(e)})

# Extract vacancy details using OpenAI API
def extract_vacancy_details(vacancy_content):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Extract the following fields with json format from this vacancy description: job_title, minimum_year_of_experience, skills, responsibilities.\n\nVacancy Description:\n{vacancy_content}"}
            ]
        )
        return completion.choices[0].message.content.replace('json','').replace('```','')
    except Exception as e:
        return json.dumps({"error": str(e)})

# Score Resume Function
def score_resume(vacancy_json, resume_json):
    try:
        # Skill Score
        skills_score_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"On a scale from 0 to 100, how relevant are these skills:\nResume Skills: {resume_json['skills']}\nVacancy Skills: {vacancy_json['skills']}\nPlease provide only the score."}
            ]
        )
        skills_score = int(skills_score_response.choices[0].message.content.strip())

        # Experience Score
        experience_score_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"On a scale from 0 to 100, how relevant is this experience:\nResume Experience: {resume_json['experience']}\nVacancy Experience: Minimum {vacancy_json['minimum_year_of_experience']} years experience needed.\nPlease provide only the score."}
            ]
        )
        experience_score = int(experience_score_response.choices[0].message.content.strip())

        # Education Score
        education_score_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"On a scale from 0 to 100, how relevant is this education and GPA:\nResume Education: {resume_json['Education']}\nVacancy Job Title: {vacancy_json['job_title']}\nVacancy Responsibilities: {vacancy_json['responsibilities']}\nPlease provide only the score."}
            ]
        )
        education_score = int(education_score_response.choices[0].message.content.strip())

        # Total Score Calculation
        total_score = (0.2 * skills_score) + (0.6 * experience_score) + (0.2 * education_score)

        return {
            "skills_score": skills_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "total_score": total_score
        }

    except Exception as e:
        return {"error": str(e)}

# App title
st.title("AI for Talent Acquisition: Resume Scoring Demo")

# Display Vacancy section
st.subheader("The Vacancy")
vacancy_content = read_vacancy()
st.markdown(vacancy_content)

# Analyze and save vacancy details
vacancy_info = None
if os.path.exists("vacancy.json"):
    with open("vacancy.json", "r") as file:
        vacancy_info = json.load(file)
    st.subheader("Extracted Vacancy Details (Loaded from File)")
    st.json(vacancy_info)
else:
    if st.button("Analyze Vacancy"):
        vacancy_details = extract_vacancy_details(vacancy_content)
        try:
            vacancy_info = json.loads(vacancy_details)
            with open("vacancy.json", "w") as file:
                json.dump(vacancy_info, file, indent=2)
            st.subheader("Extracted Vacancy Details")
            st.json(vacancy_info)
        except json.JSONDecodeError:
            st.error("Failed to parse vacancy details.")

# Document Processing Section
st.subheader("Document Processing")
use_ocr = st.checkbox("Use OCR (GPT-4.1-mini image extraction)")

# Input for the number of documents to process
document_count = st.number_input(
    "How many documents do you want to process?", min_value=1, max_value=100, step=1
)

# Upload buttons for each document
uploaded_files = []
st.write("Upload Documents")
for i in range(int(document_count)):
    uploaded_file = st.file_uploader(f"Upload Document {i+1}", type=["pdf"], key=f"file_uploader_{i}")
    if uploaded_file is not None:
        uploaded_files.append(uploaded_file)

# Analyze button
if st.button("Analyze Resumes") and uploaded_files and vacancy_info:
    st.subheader("Uploaded Files and Extracted Information")
    extracted_data = []
    resume_scores = []

    for uploaded_file in uploaded_files:
        st.write(f"**{uploaded_file.name}**")
        resume_json_path = os.path.join("applicant_data", f"{uploaded_file.name}.json")

        # Check if resume JSON exists
        if os.path.exists(resume_json_path):
            with open(resume_json_path, "r") as file:
                extracted_info = json.load(file)
            st.write("Loaded from file:")
            st.json(extracted_info)
        else:
            # Extract text from PDF
            if use_ocr:
                images = pdf_to_images(uploaded_file)
                if isinstance(images, str) and images.startswith("Error"):
                    st.error(images)
                    continue
                file_content = extract_text_with_ocr(images)
            else:
                file_content = extract_text_from_pdf(uploaded_file)


            if "Error" in file_content:
                st.error(file_content)
                continue

            # Extract information using OpenAI API
            extracted_json = extract_information(file_content)
            try:
                extracted_info = json.loads(extracted_json)
                with open(resume_json_path, "w") as file:
                    json.dump(extracted_info, file, indent=2)
                st.json(extracted_info)
            except json.JSONDecodeError:
                st.error("Failed to parse extracted information.")
                continue

        # Score the resume
        scores = score_resume(vacancy_info, extracted_info)
        scores_path = os.path.join("applicant_score", f"{uploaded_file.name}_score.json")
        with open(scores_path, "w") as file:
            json.dump(scores, file, indent=2)
        scores["file_name"] = uploaded_file.name
        resume_scores.append(scores)
        st.subheader("Resume Score")
        st.json(scores)

        extracted_data.append({"file_name": uploaded_file.name, "data": extracted_info})

    # Rank resumes based on total score
    if resume_scores:
        ranked_resumes = sorted(resume_scores, key=lambda x: x["total_score"], reverse=True)
        st.subheader("Ranked Resumes")
        for idx, resume in enumerate(ranked_resumes):
            st.write(f"Rank {idx + 1}: {resume['file_name']} with Total Score: {resume['total_score']}")

    # Option to download extracted data
    if extracted_data:
        st.download_button(
            label="Download Extracted Data as JSON",
            data=json.dumps(extracted_data, indent=2),
            file_name="extracted_data.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown("**Note:** Please ensure all documents are in the correct format.")
