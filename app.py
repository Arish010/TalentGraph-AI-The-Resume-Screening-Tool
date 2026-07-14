import os
import time
import io
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

from s3_service import S3Service
from app_graph import create_resume_screening_graph

st.set_page_config(
    page_title="TalentGraph AI",
    page_icon="⚙️",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { color: #f0f2f6; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4CAF50, #8BC34A); }
    .metric-card {
        background-color: #1e222b;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #3e4451;
        margin-bottom: 10px;
    }
    /* Style custom mode selection buttons */
    div.stButton > button:first-child {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

BUCKET_NAME = "resume-screening-system-arish"

@st.cache_resource
def init_backend():
    """Caches the heavy graph compilation and S3 clients so the UI remains fast."""
    s3 = S3Service(BUCKET_NAME)
    graph = create_resume_screening_graph()
    return s3, graph

try:
    s3, agent_graph = init_backend()
except Exception as e:
    st.error(f"Failed to initialize cloud backends. Ensure your .env has correct keys. Error: {e}")
    st.stop()

if "s3_candidates" not in st.session_state:
    st.session_state.s3_candidates = []

def update_s3_candidate_list():
    """Queries S3 directly and updates the application session state."""
    all_files = s3.list_resume_keys("")
    st.session_state.s3_candidates = [
        key for key in all_files 
        if key.endswith(".txt") and key != "job_description.txt"
    ]

if not st.session_state.s3_candidates:
    update_s3_candidate_list()

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Helper to extract clean selectable text from PDF bytes."""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"PDF parsing error: {e}")
        return ""

st.sidebar.title("🛠️ System Settings")
st.sidebar.markdown("### Select System Mode")

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "👤 Candidate Mode"

col_cand, col_hr = st.sidebar.columns(2)

if col_cand.button("👤 Candidate Mode", use_container_width=True, 
                 type="primary" if st.session_state.app_mode == "👤 Candidate Mode" else "secondary"):
    st.session_state.app_mode = "👤 Candidate Mode"
    st.rerun()

if col_hr.button("💼 HR Mode", use_container_width=True, 
              type="primary" if st.session_state.app_mode == "💼 HR / Recruiter Mode" else "secondary"):
    st.session_state.app_mode = "💼 HR / Recruiter Mode"
    st.rerun()

app_mode = st.session_state.app_mode
st.sidebar.markdown("---")

if app_mode != "👤 Candidate Mode":
    st.sidebar.info(f"Connected to AWS S3: `{BUCKET_NAME}`")
    st.sidebar.markdown("### 📤 S3 Batch Upload")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload file directly to S3:",
        type=["pdf", "txt"]
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        raw_file_name = uploaded_file.name
        
        if st.sidebar.button("Upload to AWS S3", use_container_width=True):
            with st.sidebar.spinner("Processing & uploading..."):
                if raw_file_name.lower().endswith(".pdf"):
                    extracted_text = extract_text_from_pdf(file_bytes)
                    upload_payload = extracted_text.encode("utf-8")
                    s3_file_key = raw_file_name.rsplit(".", 1)[0] + ".txt"
                else:
                    upload_payload = file_bytes
                    s3_file_key = raw_file_name
                    
                success = s3.upload_file_bytes(upload_payload, s3_file_key)
                if success:
                    st.sidebar.success("Uploaded successfully!")
                    st.cache_resource.clear()
                    update_s3_candidate_list()
                    time.sleep(1)
                    st.rerun()

    if st.sidebar.button("🔄 Sync S3 Bucket List", use_container_width=True):
        st.cache_resource.clear()
        update_s3_candidate_list()
        st.success("S3 Bucket List Synced!")
        time.sleep(1)
        st.rerun()

st.sidebar.markdown("<br><br>" * 3, unsafe_allow_html=True) 
st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style="text-align: center; color: #8bc34a; font-size: 0.85rem;">
        <p style="margin-bottom: 5px;">🤖 Designed & Engineered by</p>
        <p style="font-weight: bold; font-size: 1rem; color: #f0f2f6; margin-top: 0;">Arish Abdulgani Shaikh</p>
        <p style="color: #57606f; font-size: 0.75rem;">© 2026 TalentGraph AI. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)

if app_mode == "👤 Candidate Mode":
    st.title("🤖 TalentGraph AI: Candidate Feedback Center")
    st.write("Upload your resume and target job description to receive instant matching scores and detailed improvements.")
    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📋 Target Job Description")
        candidate_jd = st.text_area(
            "Paste target requirements here:",
            height=250,
            placeholder="e.g., Looking for a Data Scientist proficient in Python, SQL, and Machine Learning pipelines..."
        )

    with col2:
        st.header("📤 Your Resume")
        uploaded_resume = st.file_uploader(
            "Upload your resume (PDF or TXT):",
            type=["pdf", "txt"],
            help="Your file is processed instantly and securely in-memory. It will not be stored anywhere."
        )

    if st.button("🔍 Analyze Match & Get Feedback", type="primary", use_container_width=True):
        if not candidate_jd:
            st.error("Please paste a Job Description first.")
        elif not uploaded_resume:
            st.error("Please upload your resume file.")
        else:
            with st.spinner("Agents are analyzing your profile against the target role..."):
                file_bytes = uploaded_resume.read()
                if uploaded_resume.name.lower().endswith(".pdf"):
                    resume_text = extract_text_from_pdf(file_bytes)
                else:
                    resume_text = file_bytes.decode("utf-8")

                if not resume_text:
                    st.error("Could not read any text from your resume. Ensure it is not a scanned image PDF.")
                else:
                    initial_state = {
                        "resume_raw": resume_text,
                        "resume_data": {},
                        "jd_text": candidate_jd,
                        "similarity_score": 0.0,
                        "insight": "",
                        "matched_skills": []
                    }
                    
                    final_state = agent_graph.invoke(initial_state)

                    st.markdown("---")
                    st.header("📊 Evaluation Breakdown")
                    
                    score_col, skill_col = st.columns([1, 2])
                    
                    with score_col:
                        st.markdown(f"""
                        <div class="metric-card" style="text-align: center;">
                            <h3 style="margin: 0; color: #8BC34A;">Match Accuracy</h3>
                            <h1 style="font-size: 4rem; margin: 10px 0; color: #4CAF50;">{final_state['similarity_score']}%</h1>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with skill_col:
                        matched = final_state['matched_skills']
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3 style="margin: 0; color: #f0f2f6;">Identified Match Keywords</h3>
                            <p style="font-size: 1.2rem; margin-top: 15px;">
                                {', '.join([f"✅ <b>{s}</b>" for s in matched]) if matched else '⚠️ No standard technical keyword matches detected.'}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("### 💬 AI Agent Recommendation & Improvement Coach")
                    st.markdown(final_state['insight'].strip())

else:
    st.title("💼 TalentGraph AI: HR Batch Screener")
    st.write("Compare multiple candidates currently stored inside your AWS S3 data bucket against a target requirement sheet.")
    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("📋 Target Requirements")
        try:
            with st.spinner("Fetching JD..."):
                default_jd = s3.download_file_to_string("job_description.txt")
        except Exception:
            default_jd = "Enter requirements..."
            
        jd_input = st.text_area("Job Description Context:", value=default_jd, height=350)

    with col2:
        st.header("👥 AWS S3 Queue")
        
        candidate_keys = st.session_state.s3_candidates
        
        if not candidate_keys:
            st.warning("No candidate profiles found in S3. Please upload some text or PDF resumes.")
        else:
            st.write(f"S3 Bucket contains **{len(candidate_keys)}** resumes:")
            grid_cols = st.columns(3)
            for i, key in enumerate(candidate_keys):
                col_idx = i % 3
                display_name = key.replace(".txt", "").title().replace("Candidate_", "").replace("_", " ")
                grid_cols[col_idx].markdown(f"- 📄 **{display_name}**")

    st.markdown("---")
    if st.button("🚀 Run Cloud Multi-Agent Screening", type="primary", use_container_width=True):
        if not candidate_keys:
            st.error("S3 bucket is empty. Upload candidate profiles first.")
        else:
            status_box = st.empty()
            progress_bar = st.progress(0)
            final_leaderboard_data = []
            total_candidates = len(candidate_keys)

            for index, file_key in enumerate(candidate_keys):
                display_name = file_key.replace(".txt", "").title().replace("Candidate_", "").replace("_", " ")
                status_box.markdown(f"🟢 **[ORCHESTRATOR]** Fetching and evaluating **{display_name}**...")
                
                raw_resume_text = s3.download_file_to_string(file_key)
                
                initial_state = {
                    "resume_raw": raw_resume_text,
                    "resume_data": {},
                    "jd_text": jd_input,
                    "similarity_score": 0.0,
                    "insight": "",
                    "matched_skills": []
                }
                
                final_state = agent_graph.invoke(initial_state)
                final_leaderboard_data.append({
                    "candidate": display_name,
                    "score": final_state["similarity_score"],
                    "skills": final_state["matched_skills"],
                    "insight": final_state["insight"].strip()
                })
                progress_bar.progress((index + 1) / total_candidates)

            status_box.empty()
            progress_bar.empty()

            ranked_leaderboard = sorted(final_leaderboard_data, key=lambda x: x["score"], reverse=True)
            st.header("🏆 Live AI Leaderboard")
            for rank, candidate in enumerate(ranked_leaderboard, 1):
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; color: #4CAF50;">Rank {rank}: {candidate['candidate']}</h3>
                        <span style="font-size: 1.5rem; font-weight: bold; color: #8BC34A;">{candidate['score']}% Match</span>
                    </div>
                    <p style="margin-top: 10px;"><b>Identified Skills:</b> {', '.join(candidate['skills'])}</p>
                    <blockquote style="border-left: 5px solid #8BC34A; padding-left: 10px; margin-top: 10px; color: #b2bec3; font-style: italic;">
                        "{candidate['insight']}"
                    </blockquote>
                </div>
                """, unsafe_allow_html=True)
