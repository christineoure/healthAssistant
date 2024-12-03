import streamlit as st
from streamlit_webrtc import webrtc_streamer
from PIL import Image
import re
import google.generativeai as genai
from datetime import datetime

# Configure the Google Generative AI (Gemini API)
genai.configure(api_key="AIzaSyDeg4BHbJaM7tGocs4t6RJ4u7pI_2NpPOU")  # Replace with your actual API key
model_name = "gemini-1.5-flash"

# Specialist recommendations based on keywords
SPECIALIST_MAPPING = {
    "headache": "Neurologist",
    "fever": "General Physician",
    "rash": "Dermatologist",
    "cough": "Pulmonologist",
    "chest pain": "Cardiologist",
    "stomach ache": "Gastroenterologist",
    "back pain": "Orthopedist",
    "anxiety": "Psychiatrist",
    "depression": "Psychiatrist",
    "diabetes": "Endocrinologist",
}

# Define a text-cleaning function
def clean_text(text):
    """Preprocess user input."""
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'http\S+|www\S+', '', text, flags=re.MULTILINE)  # Remove links
    text = re.sub(r'[^A-Za-z\s]', '', text)  # Remove punctuation and numbers
    text = text.lower()  # Convert to lowercase
    return text.strip()

# Define a function to generate a response from Gemini API
def get_gemini_response(user_input):
    """Send the input to Google Generative AI and get a response."""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Recommend a specialist based on the user input
def recommend_specialist(cleaned_input):
    """Recommend a specialist based on the user's symptoms."""
    for keyword, specialist in SPECIALIST_MAPPING.items():
        if keyword in cleaned_input:
            return specialist
    return "General Physician"

# Streamlit app interface
st.set_page_config(page_title="Health Assistant", page_icon="🩺")

# App title and description
st.title("🩺 Health Assistant")
st.markdown("""
Welcome to the **Health Assistant**!  
Describe your symptoms, and we'll provide a diagnosis, recommend a specialist, or connect you with a doctor for real-time interaction.
""")

# Sidebar options
st.sidebar.title("Options")
st.sidebar.header("📅 Book a Session with a Doctor")

# Dropdown for selecting a specialist
specialist_dropdown = st.sidebar.selectbox(
    "Choose a specialist:",
    ["Select a Specialist", "Neurologist", "Dermatologist", "Pulmonologist", "Cardiologist",
     "Gastroenterologist", "Orthopedist", "Psychiatrist", "Endocrinologist", "General Physician"]
)

# Allow users to select a date and time
session_date = st.sidebar.date_input("Select a date for your session:")
session_time = st.sidebar.time_input("Select a time for your session:")

# Button to confirm booking
if st.sidebar.button("Confirm Booking"):
    if specialist_dropdown == "Select a Specialist":
        st.sidebar.warning("Please select a specialist before booking.")
    else:
        # Format the selected date and time
        booking_datetime = datetime.combine(session_date, session_time)
        
        # Display success message
        st.sidebar.success(
            f"Session with **{specialist_dropdown}** successfully booked on "
            f"**{booking_datetime.strftime('%A, %d %B %Y at %I:%M %p')}**."
        )

# Chat UI and Specialist Recommendation
st.header("Chat with Virtual Doctor")
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# User input section
user_input = st.text_input("📝 Describe your symptoms or ask a question:")

if st.button("Send"):
    if user_input:
        # Display user message
        st.session_state["messages"].append({"role": "user", "content": user_input})

        # Clean the user input
        cleaned_input = clean_text(user_input)

        # Get AI response
        with st.spinner("Processing..."):
            ai_response = get_gemini_response(cleaned_input)

        # Display AI message
        st.session_state["messages"].append({"role": "ai", "content": ai_response})

        # Recommend a specialist
        recommended_specialist = recommend_specialist(cleaned_input)
        st.info(f"Recommended Specialist: **{recommended_specialist}**")
    else:
        st.warning("Please enter symptoms or a question!")

# Display chat messages
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.write(f"🧑‍💻 **You:** {msg['content']}")
    else:
        st.markdown(f"👨‍⚕️ **Virtual Doctor:** {msg['content']}")

# Doctor Interaction Section
st.header("Doctor Interaction")

# Take a Photo for Diagnosis
photo = st.camera_input("📸 Take a photo for further diagnosis:")

if photo:
    # Display the uploaded photo
    st.image(photo, caption="Uploaded photo for diagnosis.", use_container_width=True)
    st.success("Photo uploaded successfully. The doctor can access it.")
    # Optionally save the photo
    with open("uploaded_photo.jpg", "wb") as file:
        file.write(photo.getbuffer())
    st.info("The doctor can download the uploaded photo.")

# # Real-time Video Conversation
# st.header("📹 Real-time Consultation with a Specialist")
# st.info("Start your live video consultation below.")
# webrtc_streamer(key="realtime-video", media_stream_constraints={"video": True, "audio": True})


# import streamlit as st
# import google.generativeai as genai
# from bs4 import BeautifulSoup
# import re

# # Set the page configuration
# st.set_page_config(page_title="Health Assistant", page_icon="🩺")

# # Configure the Gemini API (Google Generative AI)
# genai.configure(api_key="AIzaSyDeg4BHbJaM7tGocs4t6RJ4u7pI_2NpPOU")  # Replace with your actual Gemini API key
# model_name = "gemini-1.5-flash"

# # Define a function to clean user input
# def clean_text(text):
#     """Clean input text by removing special characters, numbers, and HTML tags."""
#     text = BeautifulSoup(text, "html.parser").get_text()  # Remove HTML tags
#     text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
#     text = re.sub(r'\d+', '', text)  # Remove numbers
#     return text.lower().strip()

# # Define a function to generate a response using Gemini API
# def get_gemini_response(user_input):
#     """Generate a response using the Gemini API."""
#     try:
#         model = genai.GenerativeModel(model_name)
#         response = model.generate_content(user_input)
#         return response.text
#     except Exception as e:
#         return f"Error: {str(e)}"

# # Streamlit app layout
# st.title("🩺 Health Assistant")
# st.markdown("""
# This **Health Assistant** uses advanced AI to answer your medical questions.  
# Enter your question below to receive a response from the Virtual Doctor.
# """)

# # Input area for user questions
# user_question = st.text_area("📝 Ask your medical question:", height=150)

# # Button to get a response
# if st.button("Get Response"):
#     if user_question:
#         with st.spinner("Thinking..."):
#             # Clean the user input
#             cleaned_question = clean_text(user_question)

#             # Get the AI response
#             response = get_gemini_response(cleaned_question)

#         # Display the AI response
#         st.subheader("Virtual Doctor's Response:")
#         st.write(response)
#     else:
#         st.warning("Please enter a question!")

# # Sidebar Information
# st.sidebar.title("About")
# st.sidebar.info("""
# This application leverages the Gemini API to answer medical questions.  
# Use it responsibly for informational purposes only.
# """)
