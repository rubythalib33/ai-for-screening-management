import streamlit as st
import os
import json
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Ensure the interview_answer and applicant_score directories exist
if not os.path.exists("interview_answer"):
    os.makedirs("interview_answer")

if not os.path.exists("applicant_score"):
    os.makedirs("applicant_score")

# Load interview questions from interview.json
if os.path.exists("interview.json"):
    with open("interview.json", "r") as file:
        questions = json.load(file)
else:
    st.error("The interview.json file does not exist. Please add the file to the application directory.")
    questions = {"interviews": {"HR": [], "User": []}}

# Load applicants from applicant_data
applicants = [f[:-5] for f in os.listdir("applicant_data") if f.endswith(".json")]

# Streamlit app
st.title("Interview Questions")

# Select applicant
selected_applicant = st.selectbox("Select an applicant:", applicants)

# Select interview type
interview_type = st.selectbox("Select interview type:", ["HR", "User"])


st.subheader(f"Interview Questions for {selected_applicant} - {interview_type} Interview")

answers = {}

for idx, question in enumerate(questions["interviews"].get(interview_type, []), 1):
    answer = st.text_area(f"{idx}. {question}", key=f"q_{idx}")
    answers[question] = answer

# Save answers and scores to JSON
if st.button("Submit Answers and Save Scores"):
    scores = {}

    for question, answer in answers.items():
        if answer:
            # Score the answer using OpenAI API
            try:
                score_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "developer", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"On a scale from 0 to 100, how good is the answer '{answer}' based on the question: '{question}'? Please provide only the score."}
                    ]
                )
                scores[question] = int(score_response.choices[0].message.content.strip())
            except Exception as e:
                scores[question] = f"Error: {str(e)}"

    # Calculate total score for the interview
    total_score = sum(score for score in scores.values() if isinstance(score, int))
    num_questions = len([score for score in scores.values() if isinstance(score, int)])
    average_score = total_score / num_questions if num_questions > 0 else 0

    answers_path = os.path.join("interview_answer", f"{selected_applicant}_{interview_type}_answers.json")
    with open(answers_path, "w") as file:
        json.dump({"answers": answers, "scores": scores, "total_score": average_score}, file, indent=2)

    # Save the total score to applicant_score JSON
    score_path = os.path.join("applicant_score", f"{selected_applicant}_score.json")
    if os.path.exists(score_path):
        with open(score_path, "r") as file:
            applicant_score = json.load(file)
    else:
        applicant_score = {}

    applicant_score[f"{interview_type.lower()}_interview_score"] = average_score

    with open(score_path, "w") as file:
        json.dump(applicant_score, file, indent=2)

    st.success(f"Answers and scores saved to {answers_path} and {score_path}")