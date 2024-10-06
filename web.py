import streamlit as st
import google.generativeai as genai
import os
import tempfile
from gtts import gTTS

# Set your Gemini API key
os.environ["GEMINI_API_KEY"] = "KEY" 

# Configure the API with the key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

st.title("EDUACE - Student Exam Preparation Assistant")

# Initialize session states for question bank, audio, and mock question papers
if 'question_bank' not in st.session_state:
    st.session_state.question_bank = {}

if 'audio_topics' not in st.session_state:
    st.session_state.audio_topics = {}

if 'mock_qps' not in st.session_state:
    st.session_state.mock_qps = {}

# Sidebar for topic selection
st.sidebar.title("Options")
selected_task = st.sidebar.selectbox("Select Task", ["Explain Topic", "View Question Bank", "Take Test", "Audio Topics", "Mock QP"])

# Function to generate explanation using Gemini API
def generate_explanation(topic, curriculum):
    prompt = f"Provide a detailed explanation of the following topic: {topic} from the {curriculum} curriculum without images and also provide chapter/page from the respective textbook."
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# Function to generate quiz questions
def generate_quiz(explanation):
    prompt = f"Generate quiz questions based on the following content: {explanation}. Give the question in one line followed by MCQ options in new lines. Provide all answers at the end with 1 line explanation."
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# Function to convert explanation to audio
def generate_audio(explanation, topic):
    tts = gTTS(explanation)
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    tts.save(f"{temp_file.name}.mp3")
    audio_file_path = f"{temp_file.name}.mp3"
    st.session_state.audio_topics[topic] = audio_file_path
    return audio_file_path

# Function to generate a sample question paper
def generate_question_paper(subject):
    prompt = f"Generate a sample mock question paper for the subject: {subject}. from class 12 cbse board"
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# Main logic for the selected task
if selected_task == "Explain Topic":
    st.header("Topic Explanation")
    topic = st.text_input("Enter the topic you want explained:", "")
    curriculum = st.selectbox("Select Curriculum", ["CBSE", "TN-ST", "ISCE", "Other"])
    
    if st.checkbox("Generate Explanation"):
        if topic:
            explanation = generate_explanation(topic, curriculum)
            st.subheader("Explanation:")
            st.markdown("---")
            st.write(explanation)
            st.markdown("---")
            # Generate audio for the explanation
            if st.checkbox("Generate Audio Explanation"):
                st.write("Please wait while the audio is being generated")
                audio_file = generate_audio(explanation, topic)
                st.audio(audio_file)
                st.markdown("---")
            # Use a checkbox to generate quiz questions
            if st.checkbox("Generate Quiz Questions"):
                quiz_questions = generate_quiz(explanation)
                st.subheader("Quiz Questions:")
                st.write(quiz_questions)

                # Store quiz questions in the session state
                if topic not in st.session_state.question_bank:
                    st.session_state.question_bank[topic] = quiz_questions
        else:
            st.warning("Please enter a topic to explain.")

elif selected_task == "View Question Bank":
    st.header("Question Bank")
    if st.session_state.question_bank:
        for topic, questions in st.session_state.question_bank.items():
            st.subheader(topic)
            st.write(questions)
    else:
        st.write("No questions have been generated yet.")

elif selected_task == "Audio Topics":
    st.header("Audio Explanations")
    if st.session_state.audio_topics:
        for topic, audio_path in st.session_state.audio_topics.items():
            st.subheader(topic)
            st.audio(audio_path)
    else:
        st.write("No audio files generated yet.")

elif selected_task == "Take Test":
    st.header("AI Proctored Test")
    st.write("This is a simulated AI-proctored test environment.")
    subject = st.text_input("Enter the subject for the test:", "")

    if st.button("Generate Question Paper"):
        if subject:
            question_paper = generate_question_paper(subject)
            st.subheader("Sample Question Paper:")
            st.write(question_paper)

            # Add the generated question paper to Mock QP sidebar
            st.session_state.mock_qps[subject] = question_paper
        else:
            st.warning("Please enter a subject.")

    # File uploader for submitting the test
    st.subheader("Upload Your Test Answer File")
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is not None:
        st.write("File uploaded successfully.")
        st.write("File name:", uploaded_file.name)
    else:
        st.write("Please upload your test answer file.")

elif selected_task == "Mock QP":
    st.header("Mock Question Papers")
    if st.session_state.mock_qps:
        for subject, qp in st.session_state.mock_qps.items():
            st.subheader(subject)
            st.write(qp)
    else:
        st.write("No mock question papers have been generated yet.")
