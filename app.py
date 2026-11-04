import streamlit as st
import google.genai as genai
from pypdf import PdfReader

# --- App Configuration ---
st.set_page_config(
    page_title="CV Leaderboard AI", page_icon="🏆", layout="centered"
)

st.title("🏆 AI CV Leaderboard")
st.write(
    "Upload unlimited CVs, enter the job description, and get the top 3-4 best candidates!"
)

# --- API Key Setup ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input(
        "Enter your Gemini API Key", type="password"
    )

if not api_key:
    st.warning(
        "Please enter your Gemini API key in the sidebar to continue (or set it in app secrets)."
    )
    st.stop()

# Initialize the Gemini client using the updated import method
client = genai.Client(api_key=api_key)

# (Keep the rest of your app.py code below this unchanged...)
