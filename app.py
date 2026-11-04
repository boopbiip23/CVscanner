import json
import urllib.request
import urllib.error
import streamlit as st

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
    st.warning("Please enter your Gemini API key in the sidebar to continue.")
    st.stop()


# --- Simple Pure-Python PDF Text Extractor ---
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
    "1. What kind of job do you need filled?",
    placeholder="e.g., Senior Python Developer with 5+ years experience...",
    height=100,
)

uploaded_files = st.file_uploader(
    "2. Upload CVs (PDFs)", type=["pdf"], accept_multiple_files=True
)

# --- Processing & Leaderboard ---
if st.button("Generate Leaderboard 🚀", type="primary"):
    if not job_description:
        st.error("Please enter the job requirements.")
    elif not uploaded_files:
        st.error("Please upload at least one CV.")
    else:
        with st.spinner("Analyzing and ranking CVs... Please wait."):
            cv_data = []

            for file in uploaded_files:
                text = extract_text_from_pdf(file)
                cv_data.append({"filename": file.name, "text": text})

            prompt = f"""
            You are an expert HR recruiter. 
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

            # Koristimo novi, aktivni gemini-2.0-flash model
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={api_key}"
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
                        st.subheader("🎯 Top Candidates Leaderboard")
                        st.markdown(output_text)
                    else:
                        st.error(f"API Error: {result_json}")

            except urllib.error.HTTPError as e:
                error_message = e.read().decode("utf-8")
                st.error(f"HTTP Error {e.code}: {error_message}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
