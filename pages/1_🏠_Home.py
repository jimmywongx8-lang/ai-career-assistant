import streamlit as st
import os
import sys
from urllib.parse import quote

# --- NAVIGATION BAR ---
st.markdown("""<style>.nav-bar{background:white;padding:15px 20px;box-shadow:0 2px 10px rgba(0,0,0,0.1);display:flex;justify-content:center;gap:2rem;margin-bottom:2rem;border-radius:8px;}</style>""", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1: st.page_link("app.py", label="🏠 Home")
with col2: st.page_link("pages/1_🏠_Home.py", label="📋 Services")
with col3: st.page_link("pages/3_ℹ️_About.py", label="ℹ️ About")
with col4: st.page_link("pages/4_📞_Contact.py", label="📞 Contact")

# --- APP LOGIC ---
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))
try:
    from cv_parser import extract_text_from_file
    from cv_analyzer import analyze_cv
    from job_matcher import find_matching_jobs
    from cv_rewriter import rewrite_cv
    from cover_letter import generate_cover_letter
except Exception: pass

for key in ['cv_text', 'analysis', 'matches', 'selected_job', 'rewritten_cv', 'cover_letter']:
    if key not in st.session_state: st.session_state[key] = None

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
    <h1 style="margin:0">🛠️ Our Services</h1>
    <p style="margin:0.5rem 0 0 0">Upload your CV to get started</p>
</div>
""", unsafe_allow_html=True)

# Step 1
st.header("1️⃣ Upload CV")
uploaded_file = st.file_uploader("Choose PDF or DOCX", type=['pdf', 'docx'], label_visibility="collapsed")
if uploaded_file and st.session_state.cv_text is None:
    with st.spinner(" Reading..."):
        save_path = os.path.join("data", f"temp_cv.{uploaded_file.name.split('.')[-1]}")
        os.makedirs("data", exist_ok=True)
        with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
        st.session_state.cv_text = extract_text_from_file(save_path)
        st.success("✅ CV loaded!")
        st.rerun()

st.divider()

# Step 2
st.header("2️⃣ Analyze Profile")
if st.session_state.cv_text:
    if st.button("✨ Analyze CV", use_container_width=True):
        with st.spinner("🤖 Analyzing..."):
            st.session_state.analysis = analyze_cv(st.session_state.cv_text)
            st.success("✅ Done!")
    if st.session_state.analysis:
        c1, c2, c3 = st.columns(3)
        c1.metric("Sector", st.session_state.analysis.get('current_sector', 'N/A'))
        c2.metric("Level", st.session_state.analysis.get('seniority_level', 'N/A'))
        c3.metric("Skills", ', '.join(st.session_state.analysis.get('top_5_skills', [])[:3]))
else: st.info("👆 Upload CV first")

st.divider()

# Step 3
st.header("3️⃣ Find Jobs")
if st.session_state.cv_text:
    keywords = st.text_input("Target Job", value="Strategy Consultant")
    location = st.text_input("Location", value="Singapore")
    
    if st.button("🔍 Search Jobs", use_container_width=True):
        with st.spinner("🔎 Searching..."):
            st.session_state.matches = find_matching_jobs(st.session_state.cv_text, keywords, location, num_matches=3)
            if st.session_state.matches: st.success(f"✅ Found {len(st.session_state.matches)} matches!")
    
    if st.session_state.matches:
        job_options = [f"{m['title']} at {m['company']}" for m in st.session_state.matches]
        selected = st.selectbox("Select a job:", job_options)
        if selected:
            idx = job_options.index(selected)
            st.session_state.selected_job = st.session_state.matches[idx]
            job = st.session_state.selected_job
            
            apply_link = job.get('apply_link')
            if not apply_link or apply_link == '#':
                apply_link = f"https://www.google.com/search?q=apply {quote(job['title'])} {quote(job['company'])}"
            
            st.markdown(f"### 🎯 {job['title']}")
            st.info(f"**{job['company']}** • {job['location']} • Score: {job.get('score')}%")
            st.link_button("🔗 Apply Now", apply_link)
else: st.info("👆 Upload CV first")

st.divider()

# Step 4 & 5
c1, c2 = st.columns(2)
with c1:
    st.header("4️⃣ Tailor CV")
    if st.session_state.cv_text and st.session_state.selected_job:
        if st.button("✏️ Rewrite", use_container_width=True):
            with st.spinner("✍️..."):
                st.session_state.rewritten_cv = rewrite_cv(st.session_state.cv_text, st.session_state.selected_job['title'], st.session_state.selected_job.get('description', ''))
        if st.session_state.rewritten_cv:
            st.download_button("📥 Download", st.session_state.rewritten_cv, "cv.txt")
    else: st.info("Select a job first")

with c2:
    st.header("5️⃣ Cover Letter")
    if st.session_state.cv_text and st.session_state.selected_job:
        if st.button("✉️ Generate", use_container_width=True):
            with st.spinner("✍️..."):
                st.session_state.cover_letter = generate_cover_letter(st.session_state.cv_text, st.session_state.selected_job['title'], st.session_state.selected_job.get('description', ''))
        if st.session_state.cover_letter:
            st.download_button("📥 Download", st.session_state.cover_letter, "letter.txt")
    else: st.info("Select a job first")