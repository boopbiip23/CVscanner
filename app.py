import json
import urllib.request
import urllib.error
import streamlit as st

# --- App Configuration & Simpsons Theme ---
st.set_page_config(
    page_title="Simpsons CV Leaderboard 🍩", 
    page_icon="🍩", 
    layout="centered"
)

# Custom Simpsons Styling (Clouds, Yellow & Blue theme)
st.markdown("""
    <style>
    /* Simpsons Sky Background with animated clouds */
    .stApp {
        background: linear-gradient(135deg, #70d6ff 0%, #ff70a6 100%);
        background-attachment: fixed;
    }
    
    /* Main container styling */
    div.block-container {
        background-color: rgba(255, 255, 255, 0.92);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        border: 4px solid #ffd166;
    }

    /* Titles and Headers */
    h1 {
        color: #0b090a;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        text-shadow: 2px 2px #ffd166;
        text-align: center;
    }
    
    p, label {
        color: #1d3557;
        font-weight: bold;
    }

    /* Simpsons Yellow Buttons */
    .stButton > button {
        background-color: #ffd166 !important;
        color: #0b090a !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        border: 3px solid #0b090a !important;
        box-shadow: 0 4px 0 #0b090a !important;
        width: 100%;
        transition: all 0.1s ease;
    }
    
    .stButton > button:hover {
        background-color: #ff9f1c !important;
        transform: translateY(-2px);
    }

    /* Text areas and file uploaders */
    .stTextArea textarea, .stFileUploader {
        border-radius: 10px;
        border: 2px solid #1d3557;
    }
    </style>
""", unsafe_allow_html=True)

# Simpsons Header
st.markdown("<h1>🍩 Simpsons CV Leaderboard 🏆</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>*Even Homer Simpson could find the best candidate with this!* 🍺</p>", unsafe_allow_html=True)
st.markdown("---")

# --- API Key Setup ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input(
        "🔑 Enter your Gemini API Key", type="password"
    )

if not api_key:
    st.warning("⚠️ Please enter your Gemini API key in the sidebar to fire up the Springfield AI!")
    st.stop()


# --- Funkcija za automatsko nalaženje aktivnog modela ---
def get_working_model(api_key):
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
        req = urllib.request.Request(list_url, method="GET")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            for model in data.get("models", []):
                name = model.get("name", "")
                methods = model.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    return name.replace("models/", "")
    except Exception:
        pass
    return "gemini-1.5-flash"


# --- PDF Text Extractor ---
def extract_text_from_pdf(pdf_file) -> str:
    try:
        content = pdf_file.read()
        text = ""
        for line in content.split(b"\n"):
            if b"(" in line and b")" in line:
                try:
                    decoded = line.decode("latin1", errors="ignore")
                    text += decoded + " "
                except:
                    pass
        return text if len(text) > 50 else "Sadržaj CV-a iz PDF-a"
    except Exception as e:
        return f"Error reading PDF: {e}"


# --- User Inputs ---
job_description = st.text_area(
    "📝 1. What kind of job do you need filled?",
    placeholder="e.g., Nuclear Safety Inspector who eats donuts all day...",
    height=100,
)

uploaded_files = st.file_uploader(
    "📂 2. Upload Candidate CVs (PDFs)", type=["pdf"], accept_multiple_files=True
)

# --- Processing & Leaderboard ---
if st.button("D’oh! Let's Generate Leaderboard 🚀"):
    if not job_description:
        st.error("D'oh! You forgot to write the job requirements!")
    elif not uploaded_files:
        st.error("D'oh! You didn't upload any CVs!")
    else:
        with st.spinner("🍩 Mmm... analyzing candidate brains in Springfield... Please wait!"):
            cv_data = []

            for file in uploaded_files:
                text = extract_text_from_pdf(file)
                cv_data.append({"filename": file.name, "text": text})

            prompt = f"""
            You are an expert HR recruiter with a fun Simpsons-like attitude. 
            I am looking to fill the following job role:
            ---
            {job_description}
            ---

            Below are the contents of {len(cv_data)} candidate CVs. 
            Analyze all of them, evaluate how well they match the job requirements, and select ONLY the TOP 3 to 4 best candidates.

            Return the results as a strict leaderboard (Number 1 being the absolute best).

            For each of the top 3-4 candidates, provide:
            1. Rank (#1, #2, #3, #4)
            2. Candidate Name/Filename
            3. Match Score (out of 100)
            4. A short justification of why they are a great fit (strengths).
            5. One potential weakness or missing skill based on the job description.

            Here are the CVs:
            """

            for i, cv in enumerate(cv_data):
                prompt += f"\n\n--- CANDIDATE {i+1} (Filename: {cv['filename']}) ---\n{cv['text'][:10000]}"

            model_name = get_working_model(api_key)
            
            url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}"
            payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
            
            req = urllib.request.Request(
                url, 
                data=payload, 
                headers={"Content-Type": "application/json"}, 
                method="POST"
            )

            try:
                with urllib.request.urlopen(req) as response:
                    result_json = json.loads(response.read().decode("utf-8"))
                    
                    if "candidates" in result_json:
                        output_text = result_json["candidates"][0]["content"]["parts"][0]["text"]
                        st.markdown("---")
                        st.subheader("🏆 Springfield's Top Candidates Leaderboard")
                        st.markdown(output_text)
                    else:
                        st.error(f"API Error: {result_json}")

            except urllib.error.HTTPError as e:
                error_message = e.read().decode("utf-8")
                st.error(f"HTTP Error {e.code}: {error_message}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
