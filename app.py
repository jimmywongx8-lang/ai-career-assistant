# app.py
import streamlit as st
import os
import sys
import time
from urllib.parse import quote

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from cv_parser import extract_text_from_file
    from cv_analyzer import analyze_cv
    from job_matcher import find_matching_jobs
    from cv_rewriter import rewrite_cv
    from cover_letter import generate_cover_letter
except Exception as e:
    st.error(f"⚠️ Error loading modules: {e}")

# Page Config
st.set_page_config(
    page_title="Career Compass | AI Outplacement",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS & THEME ---
st.markdown("""
<style>
    /* General Styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    body, p, h1, h2, h3, h4, h5, h6, span, label, div, a {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    
    /* Header Gradient */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    .header-container h1 { margin: 0; font-size: 2.5rem; font-weight: 700; }
    .header-container p { margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9; }

    /* Section Cards */
    .step-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 2rem;
        transition: transform 0.2s ease;
    }
    .step-card:hover { border-color: #667eea; }

    .step-title {
        color: #1e293b;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .step-badge {
        background: #eff6ff;
        color: #3b82f6;
        font-size: 0.8rem;
        padding: 4px 8px;
        border-radius: 20px;
        font-weight: 600;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Job Cards */
    .job-card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .score-high { color: #10b981; font-weight: bold; }
    .score-med { color: #f59e0b; font-weight: bold; }
    .score-low { color: #ef4444; font-weight: bold; }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: MISSION & NAV ---
with st.sidebar:
    st.markdown("###  Our Mission")
    st.info("Career Compass is a community-driven project designed to provide **high-quality AI career support** to everyone, for free.")
    
    st.markdown("---")
    st.markdown("**✨ Features**")
    st.caption("• AI Resume Analysis")
    st.caption("• Smart Job Matching")
    st.caption("• Tailored Documents")
    st.caption("• 100% Privacy First")
    
    st.markdown("---")
    st.markdown("**🔒 Privacy Promise**")
    st.success("Your CV and data are processed locally or via secure API calls. We do not store your data.")

# --- MAIN CONTENT ---

# 1. HEADER
st.markdown("""
<div class="header-container">
    <h1>🚀 Career Compass</h1>
    <p>Your AI-powered partner for career transitions. Analyze, match, and apply with confidence.</p>
</div>
""", unsafe_allow_html=True)

# Session State Initialization
for key in ['cv_text', 'analysis', 'matches', 'selected_job', 'rewritten_cv', 'cover_letter']:
    if key not in st.session_state: st.session_state[key] = None

def reset_app():
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()

# Reset Button
if st.session_state.cv_text:
    if st.button("🔄 Start New Analysis"):
        reset_app()

# --- STEP 1: UPLOAD ---
st.markdown("""
<div class="step-card">
    <div class="step-title">📄 Step 1: Upload Your CV</div>
    <p style="color: #64748b; margin-bottom: 1rem;">Upload your current resume (PDF or DOCX) so our AI can understand your background.</p>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=['pdf', 'docx'], label_visibility="collapsed")

if uploaded_file and st.session_state.cv_text is None:
    with st.spinner(" Reading CV..."):
        save_path = os.path.join("data", f"temp_cv.{uploaded_file.name.split('.')[-1]}")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
        st.session_state.cv_text = extract_text_from_file(save_path)
        st.success("✅ CV loaded successfully!")
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- STEP 2: ANALYZE ---
st.markdown("""
<div class="step-card">
    <div class="step-title">🔍 Step 2: AI Analysis</div>
""", unsafe_allow_html=True)

if st.session_state.cv_text:
    if st.button("✨ Analyze My Profile", use_container_width=True):
        with st.spinner("🤖 Analyzing experience and skills..."):
            st.session_state.analysis = analyze_cv(st.session_state.cv_text)
            st.success("✅ Analysis Complete!")
    
    if st.session_state.analysis:
        c1, c2, c3 = st.columns(3)
        c1.metric("🏢 Current Sector", st.session_state.analysis.get('current_sector', 'N/A'))
        c2.metric("📈 Seniority Level", st.session_state.analysis.get('seniority_level', 'N/A'))
        c3.metric("️ Top Skills", ', '.join(st.session_state.analysis.get('top_5_skills', [])[:3]))
else:
    st.info("👆 Please upload your CV in Step 1 first.")

st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# --- STEP 3: JOBS ---
st.markdown("""
<div class="step-card">
    <div class="step-title">🎯 Step 3: Find Matching Jobs</div>
""", unsafe_allow_html=True)

if st.session_state.cv_text:
    with st.expander("🔧 Customize Search Filters", expanded=False):
        col_a, col_b = st.columns(2)
        keywords = col_a.text_input("Target Job Title", value="Strategy Consultant")
        location = col_b.text_input("Target Location", value="Singapore")
    
    if st.button("🔍 Search Jobs (AI-Powered)", use_container_width=True):
        with st.spinner("🔎 Scanning opportunities & scoring matches..."):
            st.session_state.matches = find_matching_jobs(st.session_state.cv_text, keywords, location, num_matches=3)
            if st.session_state.matches:
                st.success(f"✅ Found {len(st.session_state.matches)} top matches!")
            else:
                st.warning("No matches found. Try broadening your keywords.")

    if st.session_state.matches:
        st.markdown("### 💼 Top Matches (AI Scored)")
        job_options = [f"{m['title']} at {m['company']}" for m in st.session_state.matches]
        selected = st.selectbox("Select a job to target:", job_options)
        
        if selected:
            idx = job_options.index(selected)
            st.session_state.selected_job = st.session_state.matches[idx]
            job = st.session_state.selected_job
            
            score_color = "score-high" if job.get('score',0) > 80 else ("score-med" if job.get('score',0) > 60 else "score-low")
            
            apply_link = job.get('apply_link')
            if not apply_link or apply_link.strip() == '':
                search_query = f"apply {job.get('title', '')} {job.get('company', '')} {job.get('location', '')}"
                apply_link = f"https://www.google.com/search?q={quote(search_query)}"
                st.info(f"ℹ️ No direct link found. This will search Google for the role.")
            
            st.markdown(f"""
            <div class="job-card">
                <h3 style="margin:0 0 0.5rem 0;"> {job['title']}</h3>
                <p style="margin:0; color:#64748b;"><strong>{job['company']}</strong> • {job['location']}</p>
                <p style="margin:0.5rem 0;"><strong>Match Score:</strong> <span class="{score_color}">{job.get('score', 'N/A')}%</span></p>
                
                <p><strong>✅ Why it matches:</strong></p>
                <ul style="margin-top:-1rem; color:#475569;">
                    {''.join(f'<li>{r}</li>' for r in job.get('reasons', []))}
                </ul>
                <p><strong>⚠️ Potential Gaps:</strong></p>
                <ul style="margin-top:-1rem; color:#475569;">
                    {''.join(f'<li>{g}</li>' for g in job.get('gaps', []))}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.link_button("🔗 Apply Now", apply_link)
else:
    st.info(" Analyze your CV first.")

st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# --- STEP 4: CV ---
st.markdown("""
<div class="step-card">
    <div class="step-title">📝 Step 4: Tailor Your CV</div>
""", unsafe_allow_html=True)

if st.session_state.cv_text and st.session_state.selected_job:
    if st.button("✏️ Generate Tailored CV", use_container_width=True):
        with st.spinner("✍️ Optimizing your CV for this role..."):
            st.session_state.rewritten_cv = rewrite_cv(st.session_state.cv_text, st.session_state.selected_job['title'], st.session_state.selected_job.get('description', ''))
            st.success("✅ Done!")
    
    if st.session_state.rewritten_cv:
        st.markdown(st.session_state.rewritten_cv)
        st.download_button("📥 Download as TXT", st.session_state.rewritten_cv, 
                          file_name=f"tailored_cv_{st.session_state.selected_job['company'].replace(' ','_')}.txt", 
                          mime="text/plain",
                          use_container_width=True)
else:
    st.info("👆 Select a job in Step 3 first.")

st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# --- STEP 5: COVER LETTER ---
st.markdown("""
<div class="step-card">
    <div class="step-title">✉️ Step 5: Generate Cover Letter</div>
""", unsafe_allow_html=True)

if st.session_state.cv_text and st.session_state.selected_job:
    if st.button(" Write Cover Letter", use_container_width=True):
        with st.spinner("✍️ Drafting your letter..."):
            st.session_state.cover_letter = generate_cover_letter(st.session_state.cv_text, st.session_state.selected_job['title'], st.session_state.selected_job.get('description', ''))
            st.success("✅ Done!")
    
    if st.session_state.cover_letter:
        st.markdown(st.session_state.cover_letter)
        st.download_button("📥 Download as TXT", st.session_state.cover_letter,
                          file_name=f"cover_letter_{st.session_state.selected_job['company'].replace(' ','_')}.txt", 
                          mime="text/plain",
                          use_container_width=True)
else:
    st.info("👆 Select a job in Step 3 first.")

st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.9rem; margin-top: 2rem;">
    <p>Built with ❤️ for the community • Privacy-First AI • Powered by Streamlit & Groq</p>
</div>
""")