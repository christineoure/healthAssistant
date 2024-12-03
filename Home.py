import streamlit as st
from PIL import Image
import base64
import re
import google.generativeai as genai
from datetime import datetime
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from the .env file
load_dotenv()

# Fetch the API key
api_key = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API
genai.configure(api_key=api_key)
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

def get_gemini_response(user_input):
    """Send the input to Google Generative AI and get a response."""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to set the background color
def set_background_color(color_hex):
    """Set a background color for the app."""
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {color_hex};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Set the page configuration
st.set_page_config(page_title="My Health Buddy", page_icon="🩺")

# Set the background color
background_color = "#BFE0DB"  # Hexadecimal for the provided light teal color
set_background_color(background_color)

# App title and logo
# logo_image = "images/Health__106_-removebg-preview.png"

# App title and logo
logo_image_path = "images/icon.png"

# Display logo and app title with circular styling and proper alignment
logo_html = f"""
<div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
    <img src="data:image/png;base64,{base64.b64encode(open(logo_image_path, 'rb').read()).decode('utf-8')}" 
         alt="Logo" 
         style="height: 80px; width: 80px; border-radius: 50%; border: 3px solid #2E7D6F; margin-right: 15px;"/>
    <h1 style="margin: 0; font-size: 2.5rem; color: #2E7D6F; line-height: 80px;">My Health Buddy</h1>
</div>
"""

# Render the logo and title
st.markdown(logo_html, unsafe_allow_html=True)

# Landing image with about section
landing_image = "images/bg.jpg"
st.image(landing_image)
st.markdown("""
**Welcome to My Health Buddy, your personal health assistant!**  
We're here to help you manage your health effortlessly with tools, insights, and recommendations tailored just for you.

Explore features like symptom diagnosis, specialist recommendations, and real-time doctor consultations.
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

if st.button("Get Diagnosis"):
    if user_input:
        # Display user message
        st.session_state["messages"].append({"role": "user", "content": user_input})

        # Clean the user input
        cleaned_input = re.sub(r"[^A-Za-z\s]", "", user_input.lower().strip())

        # Get AI response
        with st.spinner("Processing your diagnosis..."):
            ai_response = get_gemini_response(cleaned_input)  

        # Display AI message
        st.session_state["messages"].append({"role": "ai", "content": ai_response})

        # Recommend a specialist
        recommended_specialist = next(
            (specialist for keyword, specialist in SPECIALIST_MAPPING.items() if keyword in cleaned_input),
            "General Physician",
        )
        st.info(f"Recommended Specialist: **{recommended_specialist}**")
    else:
        st.warning("Please enter symptoms or a question!")

# Display chat messages
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.write(f"🧑‍💻 **You:** {msg['content']}")
    else:
        st.markdown(f"👨‍⚕️ **Virtual Doctor:** {msg['content']}")