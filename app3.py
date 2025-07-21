import streamlit as st
import os
import json

# Ensure directories exist
if not os.path.exists("applicant_data"):
    st.error("The applicant_data directory does not exist.")

if not os.path.exists("applicant_score"):
    st.error("The applicant_score directory does not exist.")

# Load applicants from applicant_data
applicants = [f[:-5] for f in os.listdir("applicant_data") if f.endswith(".json")]

# Streamlit app
st.title("Applicant Data Viewer")

# Select applicant
selected_applicant = st.selectbox("Select an applicant:", applicants)

if selected_applicant:
    # Display resume data
    resume_path = os.path.join("applicant_data", f"{selected_applicant}.json")
    if os.path.exists(resume_path):
        st.subheader("Resume Data")
        with open(resume_path, "r") as file:
            resume_data = json.load(file)
            st.json(resume_data)
    else:
        st.error("Resume data not found.")

    # Display scores
    score_path = os.path.join("applicant_score", f"{selected_applicant}_score.json")
    if os.path.exists(score_path):
        st.subheader("Scores")
        with open(score_path, "r") as file:
            scores = json.load(file)
            st.json(scores)
    else:
        st.error("Scores not found.")
