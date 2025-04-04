
import streamlit as st
import google.generativeai as genai
import os
import tempfile
from gtts import gTTS
import cv2
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Initialize the face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

st.title("EDUACE - Student Exam Preparation Assistant")

# Initialize session states
if 'question_bank' not in st.session_state:
    st.session_state.question_bank = {}
if 'audio_topics' not in st.session_state:
    st.session_state.audio_topics = {}
if 'mock_qps' not in st.session_state:
    st.session_state.mock_qps = {}

# Sidebar for task selection
st.sidebar.title("Options")
selected_task = st.sidebar.selectbox("Select Task", ["Explain Topic", "View Question Bank", "Take Test", "Audio Topics", "Mock QP"])

# Functions for generating content with the Gemini API
def generate_explanation(topic, curriculum):
    prompt = f"Provide a detailed explanation of the following topic: {topic} from the {curriculum} curriculum without images and also provide chapter/page from the respective textbook."
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def generate_quiz(explanation):
    prompt = f"Generate quiz questions based on the following content: {explanation}. Give the question in one line followed by MCQ options in new lines. Provide all answers at the end with 1 line explanation."
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

def generate_audio(explanation, topic):
    tts = gTTS(explanation[:600])
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    tts.save(f"{temp_file.name}.mp3")
    audio_file_path = f"{temp_file.name}.mp3"
    st.session_state.audio_topics[topic] = audio_file_path
    return audio_file_path

def generate_question_paper(subject):
    prompt = f"Generate a sample mock question paper for the subject: {subject} from class 12 CBSE board with max marks and timings. Give each question in a new line"
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# Function to detect faces in a frame
def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    return frame, faces

# WebRTC Video Processor for AI Proctoring
class FaceDetectionProcessor(VideoProcessorBase):
    def __init__(self):
        self.face_not_detected_start = None
        self.not_facing_flag = False
        self.multiple_faces_flag = False

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 128, 128), 2)

        num_faces = len(faces)

        if num_faces == 0:
            if not self.face_not_detected_start:
                self.face_not_detected_start = datetime.now()
            elif (datetime.now() - self.face_not_detected_start).seconds > 5:
                if not self.not_facing_flag:
                    st.warning("Warning: Face not detected for over 5 seconds!")
                    self.not_facing_flag = True
        elif num_faces == 1:
            self.face_not_detected_start = None
            self.not_facing_flag = False
            self.multiple_faces_flag = False
        else:
            if not self.multiple_faces_flag:
                st.error("Warning: Multiple faces detected! Ensure only one person is in view.")
                self.multiple_faces_flag = True

        return frame.from_ndarray(img, format="bgr24")

rtc_config = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})
if selected_task == "Take Test":
    st.header("AI Proctored Test")
    subject = st.text_input("Enter the subject for the test:", "")
    start_proctoring = st.checkbox("Enable AI Proctoring")
    
    if st.button("Generate Question Paper"):
        if subject:
            question_paper = f"Sample question paper for {subject}"
            st.session_state.mock_qps[subject] = question_paper
            st.subheader("Sample Question Paper:")
            st.write(question_paper)
        else:
            st.warning("Please enter a subject.")
    
    if start_proctoring:
        st.write("AI Proctoring is now active. Please ensure you are facing the camera.")
        webrtc_streamer(key="proctoring", video_processor_factory=FaceDetectionProcessor, rtc_configuration=rtc_config)
        
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
    subject = st.text_input("Enter the subject for the test:", "")
    # Start AI Proctoring
    start_proctoring = st.checkbox("Enable AI Proctoring")
    if st.button("Generate Question Paper"):
        if subject:
            question_paper = generate_question_paper(subject)
            st.session_state.mock_qps[subject] = question_paper
            st.subheader("Sample Question Paper:")
            st.write(question_paper)
            
            # File uploader for submitting the test
            st.subheader("Upload Your Test Answer File")
            uploaded_file = st.file_uploader("Choose a file")
        
            if uploaded_file is not None:
                st.write("File uploaded successfully.")
                st.write("File name:", uploaded_file.name)
            else:
                st.write("Please upload your test answer file.")
        else:
            st.warning("Please enter a subject.")
            
    if start_proctoring:
        st.write("AI Proctoring is now active. Please ensure you are facing the camera.")
        video_stream = cv2.VideoCapture(0)

        if not video_stream.isOpened():
            st.error("Could not open video stream. Ensure your camera is working.")
        else:
            not_facing_alert_container = st.empty()
            multiple_faces_alert_container = st.empty()
            face_not_detected_start = None
            multiple_faces_flag = False
            not_facing_flag = False

            with st.empty():
                while True:
                    ret, frame = video_stream.read()
                    if not ret:
                        break

                    frame = cv2.flip(frame, 1)
                    frame, faces = detect_faces(frame)

                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 128, 128), 2)

                    num_faces = len(faces)

                    if num_faces == 0:
                        if not face_not_detected_start:
                            face_not_detected_start = datetime.now()
                        elif (datetime.now() - face_not_detected_start).seconds > 5:
                            if not not_facing_flag:
                                not_facing_alert_container.warning("Warning: Face not detected for over 5 seconds!")
                                not_facing_flag = True
                    elif num_faces == 1:
                        face_not_detected_start = None
                        not_facing_alert_container.empty()
                        not_facing_flag = False
                        multiple_faces_flag = False
                        multiple_faces_alert_container.empty()
                    else:
                        if not multiple_faces_flag:
                            multiple_faces_alert_container.error("Warning: Multiple faces detected! Ensure only one person is in view.")
                            multiple_faces_flag = True

                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    st.image(rgb_frame, channels="RGB")

            video_stream.release()

elif selected_task == "Mock QP":
    st.header("Mock Question Papers")
    if st.session_state.mock_qps:
        for subject, qp in st.session_state.mock_qps.items():
            st.subheader(subject)
            st.write(qp)
    else:
        st.write("No mock question papers have been generated yet.")
