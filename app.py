import streamlit as st
from transformers import pipeline
from gtts import gTTS
from fpdf import FPDF
import os

# Load pipelines with correct models
text_generator = pipeline("text-generation", model="gpt2")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
qa_generator = pipeline("text2text-generation", model="valhalla/t5-small-qg-hl")

# Sample Q/A for demonstration
sample_qa = {
    "Question": "What is the process of photosynthesis?",
    "Answer": "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods with the help of chlorophyll."
}

st.title("GenAI-Powered Student Exam Preparation Assistant")

# Sidebar for topic selection
st.sidebar.title("Options")
selected_task = st.sidebar.selectbox("Select Task", ["Explain Topic", "View Question Bank", "Sample Q/A", "Take Test"])

def generate_explanation(topic):
    prompt = f"Provide a detailed explanation of the following topic: {topic} in simple terms."
    explanation = text_generator(prompt, max_length=500, num_return_sequences=1, temperature=0.7)
    return explanation[0]['generated_text']

def generate_quiz(explanation):
    prompt = f"Generate a quiz question based on the following content: {explanation}"
    quiz_question = qa_generator(prompt, max_length=150, num_return_sequences=1)
    return quiz_question[0]['generated_text']

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_file = "explanation.mp3"
    tts.save(audio_file)
    return audio_file

if selected_task == "Explain Topic":
    st.header("Topic Explanation")
    topic = st.text_input("Enter the topic you want explained:", "")
    
    if st.button("Generate Explanation"):
        if topic:
            explanation = generate_explanation(topic)
            st.subheader("Explanation:")
            st.write(explanation)
            
            # Generate and display audio
            audio_file = text_to_speech(explanation)
            st.audio(audio_file, format='audio/mp3')

            # Add the Quiz button only after the explanation is shown
            if st.button("Generate Quiz Questions"):
                quiz_question = generate_quiz(explanation)
                st.subheader("Quiz Question:")
                st.write(quiz_question)
        else:
            st.warning("Please enter a topic to explain.")

elif selected_task == "View Question Bank":
    st.header("Question Bank")
    st.write("Feature to view and manage the question bank will be added here.")

elif selected_task == "Sample Q/A":
    st.header("Sample Question and Answer")
    st.write("**Question:**")
    st.write(sample_qa["Question"])
    st.write("**Answer:**")
    st.write(sample_qa["Answer"])

elif selected_task == "Take Test":
    st.header("AI-Proctored Test")
    st.write("This is a simulated AI-proctored test environment.")
    
    # Example questions for the test
    questions = [
        "What is the capital of France?",
        "Explain the law of demand.",
        "Describe the water cycle."
    ]
    
    user_answers = []
    
    for i, question in enumerate(questions):
        st.subheader(f"Question {i + 1}: {question}")
        answer = st.text_input(f"Your Answer for Question {i + 1}", key=f"answer_{i}")
        user_answers.append(answer)
    
    # Start the camera feed using HTML and JavaScript
    st.write("### Please allow camera access for proctoring.")
    st.markdown("""
    <video id="video" width="400" height="300" autoplay></video>
    <script>
        const video = document.getElementById('video');
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
            })
            .catch(err => {
                console.error("Error accessing webcam: ", err);
            });
    </script>
    """, unsafe_allow_html=True)
    
    if st.button("Submit Answers"):
        # Generate a PDF from the user's answers
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for i, answer in enumerate(user_answers):
            pdf.cell(200, 10, txt=f"Question {i + 1}: {questions[i]}", ln=True)
            pdf.cell(200, 10, txt=f"Your Answer: {answer}", ln=True)
            pdf.cell(200, 10, txt="", ln=True)  # Add a blank line for spacing
        
        pdf_file_path = "user_answers.pdf"
        pdf.output(pdf_file_path)

        st.success("Your answers have been submitted and saved to PDF!")
        
        # Provide the PDF for download
        with open(pdf_file_path, "rb") as f:
            st.download_button("Download Your Answers PDF", f, file_name=pdf_file_path)

# Ensure to clean up any generated audio files
if os.path.exists("explanation.mp3"):
    os.remove("explanation.mp3")