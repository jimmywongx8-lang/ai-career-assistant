# app.py
import streamlit as st
import os
import sys
import time
from urllib.parse import quote

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))
from cv_parser import extract_text_from_file
from cv_analyzer import analyze_cv
from job_matcher import find_matching_jobs
from cv_rewriter import rewrite_cv
from cover_letter import generate_cover_letter

st.set_page_config(page_title="AI Outplacement Assistant", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: 600;
    }
    .section-header {font-size: 1.5rem; font-weight: 700; color: #1e293b; margin-bottom: 1.5rem; border-bottom: 3px solid #667eea; padding-bottom: 0.5rem;}
    .metric-label {font-size: 0.875rem; color: #64748b; font-weight: 500;}
    .metric-value {font-size: 1.25rem; color: #1e293b; font-weight: 700;}
    .job-card {background: #f8fafc; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #667eea; margin: 1rem 0;}
    .score-high {color: #10b981; font-weight: bold;}
    .score-med {color: #f59e0b; font-weight: bold;}
    .score-low {color: #ef4444; font-weight: bold;}
    .apply-btn {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 10px 20px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 600;
        margin-top: 1rem;
    }
    .apply-btn:hover {background: #764ba2;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);'>
    <h1 style='color: white; margin: 0; font-size: 2.5rem;'>🚀 AI Outplacement Assistant</h1>
    <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;'>Free, privacy-first AI for career transitions</p>
</div>
""", unsafe_allow_html=True)

# Session State Init
for key in ['cv_text', 'analysis', 'matches', 'selected_job', 'rewritten_cv', 'cover_letter']:
    if key not in st.session_state: st.session_state[key] = None

def reset_app():
    for key in st.session_state.keys(): del st.session_state[key]
    st.rerun()

if st.session_state.cv_text:
    if st.button("🔄 Reset App", use_container_width=True): reset_app()

# Step 1
st.markdown('<div class="section-header">📄 Step 1: Upload Your CV</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose PDF or DOCX", type=['pdf', 'docx'], label_visibility="collapsed")

if uploaded_file and st.session_state.cv_text is None:
    with st.spinner("📖 Reading CV..."):
        save_path = os.path.join("data", f"temp_cv.{uploaded_file.name.split('.')[-1]}")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
        st.session_state.cv_text = extract_text_from_file(save_path)
        st.success("✅ CV loaded!")
        st.rerun()

st.divider()

# Step 2
st.markdown('<div class="section-header">🔍 Step 2: Analyze CV</div>', unsafe_allow_html=True)
if st.session_state.cv_text:
    if st.button("✨ Analyze CV"):
        with st.spinner("🤖 Analyzing..."):
            st.session_state.analysis = analyze_cv(st.session_state.cv_text)
            st.success("✅ Done!")
    
    if st.session_state.analysis:
        c1, c2, c3 = st.columns(3)
        c1.metric("Sector", st.session_state.analysis.get('current_sector', 'N/A'))
        c2.metric("Level", st.session_state.analysis.get('seniority_level', 'N/A'))
        c3.metric("Top Skills", ', '.join(st.session_state.analysis.get('top_5_skills', [])[:3]))
else:
    st.info("👆 Upload CV first")

st.divider()

# Step 3: ENHANCED JOB SEARCH
st.markdown('<div class="section-header">🎯 Step 3: Find Matching Jobs</div>', unsafe_allow_html=True)

if st.session_state.cv_text:
    with st.expander("🔧 Customize Job Search Filters", expanded=False):
        col_a, col_b = st.columns(2)
        keywords = col_a.text_input("Keywords / Job Title", value="Strategy Consultant")
        location = col_b.text_input("Location", value="Singapore")
    
    if st.button("🔍 Search Jobs (AI-Powered)"):
        with st.spinner("🔎 Fetching & scoring jobs..."):
            st.session_state.matches = find_matching_jobs(st.session_state.cv_text, keywords, location, num_matches=3)
            if st.session_state.matches:
                st.success(f"✅ Found {len(st.session_state.matches)} top matches!")
            else:
                st.warning("No matches found. Try different keywords.")

    if st.session_state.matches:
        st.markdown("### 💼 Top Matches (AI Scored)")
        job_options = [f"{m['title']} at {m['company']}" for m in st.session_state.matches]
        selected = st.selectbox("Select a job to target:", job_options)
        
        if selected:
            idx = job_options.index(selected)
            st.session_state.selected_job = st.session_state.matches[idx]
            job = st.session_state.selected_job
            
            score_color = "score-high" if job.get('score',0) > 80 else ("score-med" if job.get('score',0) > 60 else "score-low")
            
            st.write(f"🔗 **Apply Link Value:** `{job.get('apply_link', 'NOT FOUND')}`")
            
            # Get apply link - ALWAYS use Google search as fallback
            apply_link = job.get('apply_link')
            
            # If no apply link or it's empty/None/#, use Google search
            if not apply_link or apply_link == '#' or apply_link.strip() == '':
                # Create Google search URL
                search_query = f"apply {job.get('title', '')} {job.get('company', '')} {job.get('location', '')}"
                apply_link = f"https://www.google.com/search?q={quote(search_query)}"
                st.info(f"ℹ️ No direct application link found. Clicking will search Google for: **{job.get('title')} at {job.get('company')}**")
            
            st.markdown(f"""
            <div class="job-card">
                <h3 style="margin:0 0 0.5rem 0;">🎯 {job['title']}</h3>
                <p style="margin:0; color:#64748b;"><strong>Company:</strong> {job['company']} | <strong>Location:</strong> {job['location']}</p>
                <p style="margin:0.5rem 0;"><strong>Match Score:</strong> <span class="{score_color}">{job.get('score', 'N/A')}%</span></p>
                <p><strong>✅ Why it matches:</strong></p>
                <ul style="margin-top:-1rem;">
                    {''.join(f'<li>{r}</li>' for r in job.get('reasons', []))}
                </ul>
                <p><strong>⚠️ Potential Gaps:</strong></p>
                <ul style="margin-top:-1rem;">
                    {''.join(f'<li>{g}</li>' for g in job.get('gaps', []))}
                </ul>
                <a href="{apply_link}" target="_blank" rel="noopener noreferrer" class="apply-btn">🔗 Apply Now</a>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("👆 Upload CV first")

st.divider()

# Step 4
st.markdown('<div class="section-header">📝 Step 4: Tailor Your CV</div>', unsafe_allow_html=True)
if st.session_state.cv_text and st.session_state.selected_job:
    if st.button("✏️ Rewrite CV"):
        with st.spinner("✍️ Tailoring..."):
            st.session_state.rewritten_cv = rewrite_cv(st.session_state.cv_text, st.session_state.selected_job['title'], st.session_state.selected_job.get('description', ''))
            st.success("✅ Done!")
    
    if st.session_state.rewritten_cv:
        st.markdown(st.session_state.rewritten_cv)
        st.download_button("📥 Download as TXT", st.session_state.rewritten_cv, 
                          file_name=f"tailored_cv_{st.session_state.selected_job['company'].replace(' ','_')}.txt", mime="text/plain")
        st.info("💡 **Pro Tip:** Download TXT → Open in Word → Save As PDF for best formatting.")
else:
    st.info("👆 Complete Steps 1-3 first")

st.divider()

# Step 5
st.markdown('<div class="section-header">✉️ Step 5: Generate Cover Letter</div>', unsafe_allow_html=True)
if st.session_state.cv_text and st.session_state.selected_job:
    if st.button("📄 Generate Letter"):
        with st.spinner("✍️ Writing..."):
            st.session_state.cover_letter = generate_cover_letter(st.session_state.cv_text, st.session_state.selected_job['title'], st.session_state.selected_job.get('description', ''))
            st.success("✅ Done!")
    
    if st.session_state.cover_letter:
        st.markdown(st.session_state.cover_letter)
        st.download_button("📥 Download as TXT", st.session_state.cover_letter,
                          file_name=f"cover_letter_{st.session_state.selected_job['company'].replace(' ','_')}.txt", mime="text/plain")
        st.info("💡 **Pro Tip:** Download TXT → Open in Word → Save As PDF for best formatting.")
else:
    st.info("👆 Complete Steps 1-3 first")

st.divider()
st.caption("🔒 Privacy-first: All data stays on your device. Built with ❤️ using Streamlit & Groq")