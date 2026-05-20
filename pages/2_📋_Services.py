import streamlit as st
import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    from cv_parser import extract_text_from_file
    from cv_analyzer import analyze_cv
    from job_matcher import find_matching_jobs
    from cv_rewriter import rewrite_cv
    from cover_letter import generate_cover_letter
except Exception as e:
    st.error(f"⚠️ Error loading modules: {e}")

st.set_page_config(page_title="Services | Career Compass", page_icon="📋", layout="wide")

# CSS
st.markdown("""
<style>
    .service-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .step-container {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
        border-left: 5px solid #3b82f6;
    }
    
    .step-number {
        background: #3b82f6;
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="service-header">
    <h1 style="margin: 0; font-size: 2.5rem;">Our Services</h1>
    <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">Professional career transition tools powered by AI</p>
</div>
""", unsafe_allow_html=True)

# Session State
for key in ['cv_text', 'analysis', 'matches', 'selected_job', 'rewritten_cv', 'cover_letter']:
    if key not in st.session_state: st.session_state[key] = None

# Step 1
st.markdown("""
<div class="step-container">
    <h2><span class="step-number">1</span>Upload Your CV</h2>
    <p style="color: #64748b; margin-left: 56px;">Start by uploading your current resume</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose PDF or DOCX", type=['pdf', 'docx'], label_visibility="collapsed")

if uploaded_file and st.session_state.cv_text is None:
    with st.spinner("📖 Reading your CV..."):
        save_path = os.path.join("data", f"temp_cv.{uploaded_file.name.split('.')[-1]}")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.cv_text = extract_text_from_file(save_path)
        st.success("✅ CV uploaded successfully!")
        st.rerun()

st.divider()

# Step 2
st.markdown("""
<div class="step-container">
    <h2><span class="step-number">2</span>AI Analysis</h2>
    <p style="color: #64748b; margin-left: 56px;">Let our AI analyze your profile</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.cv_text:
    if st.button("✨ Analyze My Profile", use_container_width=True):
        with st.spinner("🤖 Analyzing..."):
            st.session_state.analysis = analyze_cv(st.session_state.cv_text)
            st.success("✅ Analysis complete!")
    
    if st.session_state.analysis:
        c1, c2, c3 = st.columns(3)
        c1.metric("🏢 Sector", st.session_state.analysis.get('current_sector', 'N/A'))
        c2.metric("📈 Level", st.session_state.analysis.get('seniority_level', 'N/A'))
        c3.metric("🛠️ Top Skills", ', '.join(st.session_state.analysis.get('top_5_skills', [])[:3]))
else:
    st.info("👆 Upload your CV first")

st.divider()

# Step 3
st.markdown("""
<div class="step-container">
    <h2><span class="step-number">3</span>Find Matching Jobs</h2>
    <p style="color: #64748b; margin-left: 56px;">AI-powered job matching</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.cv_text:
    keywords = st.text_input("Target Job Title", value="Strategy Consultant")
    location = st.text_input("Location", value="Singapore")
    
    if st.button("🔍 Search Jobs", use_container_width=True):
        with st.spinner("🔎 Finding matches..."):
            st.session_state.matches = find_matching_jobs(st.session_state.cv_text, keywords, location, num_matches=3)
            if st.session_state.matches:
                st.success(f"✅ Found {len(st.session_state.matches)} matches!")
    
    if st.session_state.matches:
        job_options = [f"{m['title']} at {m['company']}" for m in st.session_state.matches]
        selected = st.selectbox("Select a job:", job_options)
        
        if selected:
            idx = job_options.index(selected)
            st.session_state.selected_job = st.session_state.matches[idx]
            job = st.session_state.selected_job
            
            st.markdown(f"""
            <div style="background: #f0f9ff; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
                <h3>🎯 {job['title']}</h3>
                <p><strong>{job['company']}</strong> • {job['location']}</p>
                <p><strong>Match Score:</strong> {job.get('score', 'N/A')}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            apply_link = job.get('apply_link', '')
            if not apply_link:
                search_query = f"apply {job['title']} {job['company']}"
                apply_link = f"https://www.google.com/search?q={quote(search_query)}"
            
            st.link_button("🔗 Apply Now", apply_link)
else:
    st.info("👆 Upload CV first")

st.divider()

# Step 4 & 5
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
    <div class="step-container">
        <h2><span class="step-number">4</span>Tailor CV</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.cv_text and st.session_state.selected_job:
        if st.button("✏️ Rewrite CV", use_container_width=True):
            with st.spinner("✍️ Tailoring..."):
                st.session_state.rewritten_cv = rewrite_cv(st.session_state.cv_text, st.session_state.selected_job['title'], st.session_state.selected_job.get('description', ''))
                st.success("✅ Done!")
        
        if st.session_state.rewritten_cv:
            st.download_button("📥 Download", st.session_state.rewritten_cv, "tailored_cv.txt")
    else:
        st.info("Complete steps 1-3 first")

with col_b:
    st.markdown("""
    <div class="step-container">
        <h2><span class="step-number">5</span>Cover Letter</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.cv_text and st.session_state.selected_job:
        if st.button("✉️ Generate Letter", use_container_width=True):
            with st.spinner("✍️ Writing..."):
                st.session_state.cover_letter = generate_cover_letter(st.session_state.cv_text, st.session_state.selected_job['title'], st.session_state.selected_job.get('description', ''))
                st.success("✅ Done!")
        
        if st.session_state.cover_letter:
            st.download_button("📥 Download", st.session_state.cover_letter, "cover_letter.txt")
    else:
        st.info("Complete steps 1-3 first")