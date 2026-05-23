import streamlit as st
import sys
from pathlib import Path
import json
import hashlib

# Add project root to path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from modules.jsearch_client import JSearchClient
except ImportError:
    JSearchClient = None

st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="wide")

# Simple CSS for styling
st.markdown("""
<style>
    .job-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .badge { 
        display: inline-block; 
        padding: 5px 15px; 
        border-radius: 20px; 
        font-weight: bold;
        background-color: #f59e0b;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧭 Career Compass")

# Initialize Session State
if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""

# Sidebar for Saved Jobs
with st.sidebar:
    st.header("💼 Saved Jobs")
    if st.session_state.saved_jobs:
        st.success(f"✅ {len(st.session_state.saved_jobs)} saved")
        for i, job in enumerate(st.session_state.saved_jobs):
            st.write(f"**{i+1}.** {job.get('job_title', 'Job')}")
        if st.button("🗑️ Clear All"):
            st.session_state.saved_jobs = []
            st.rerun()
    else:
        st.info("No saved jobs")

# Main Tabs
tab1, tab2, tab3 = st.tabs(["📄 CV Upload", "🔍 Analysis", "💼 Jobs"])

# ==================== TAB 1: CV UPLOAD ====================
with tab1:
    st.header("Upload CV")
    uploaded = st.file_uploader("Choose a text file", type=["txt", "pdf"], key="cv_uploader")
    if uploaded:
        try:
            if uploaded.type == "text/plain":
                st.session_state.cv_text = uploaded.read().decode("utf-8")
                st.success("✅ CV Uploaded!")
            else:
                st.warning("Please upload a .txt file for this demo.")
        except Exception as e:
            st.error(f"Error: {e}")

# ==================== TAB 2: ANALYSIS ====================
with tab2:
    st.header("AI Analysis")
    if not st.session_state.cv_text:
        st.warning("Upload CV first")
    elif st.button("Analyze", key="btn_analyze"):
        try:
            from groq import Groq
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": f"Analyze this CV: {st.session_state.cv_text[:2000]}"}]
            )
            st.write(resp.choices[0].message.content)
        except Exception as e:
            st.write(f"Error: {e}")

# ==================== TAB 3: JOBS ====================
with tab3:
    st.header("Job Matching")
    
    if JSearchClient is None:
        st.error("Job matching module not loaded")
    else:
        # Search Button
        if st.button("🔍 Search Jobs", key="btn_search"):
            try:
                client = JSearchClient(api_key=st.secrets.get("JSEARCH_API_KEY", "demo-key"))
                results = client.search_jobs(
                    query="software developer", 
                    num_pages=1,
                    user_skills=["Python", "JavaScript", "AWS"]
                )
                
                # Store results in session state
                st.session_state.search_results = results.get("data", [])
                st.success(f"Found {len(st.session_state.search_results)} jobs!")
            except Exception as e:
                st.error(f"Error: {e}")
        
        # Display Results
        if st.session_state.search_results:
            st.markdown("---")
            for idx, job in enumerate(st.session_state.search_results):
                # Extract data safely
                title = str(job.get("job_title", "Job"))
                company = str(job.get("employer_name", "Company"))
                city = str(job.get("job_city", ""))
                desc = str(job.get("job_description", ""))[:200]
                skills = job.get("job_required_skills", [])
                apply_url = str(job.get("job_apply_link", "#"))
                score = float(job.get("career_compass_match_score", 0))
                
                # Determine badge
                if score >= 0.7: badge = "🟢 Excellent"
                elif score >= 0.4: badge = "🟡 Good"
                else: badge = "⚪ Match"
                
                # Check if saved
                is_saved = any(
                    str(s.get("job_title")) == title and str(s.get("employer_name")) == company
                    for s in st.session_state.saved_jobs
                )
                
                # Render Job Card
                st.markdown(f"""
                <div class="job-card">
                    <div style="font-size:24px; font-weight:bold;">{title}</div>
                    <div>🏢 {company} | 📍 {city}</div>
                    <div style="margin-top:10px;"><span class="badge">{badge}</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Save Button
                col1, col2 = st.columns([4, 1])
                with col1:
                    if is_saved:
                        st.success("💾 Saved")
                    else:
                        st.info("Click Save to bookmark")
                
                with col2:
                    key = f"save_{idx}_{hashlib.md5(f'{title}{company}'.encode()).hexdigest()}"
                    if st.button("💾 Save", key=key):
                        if is_saved:
                            # Remove
                            st.session_state.saved_jobs = [
                                j for j in st.session_state.saved_jobs
                                if not (str(j.get("job_title")) == title and str(j.get("employer_name")) == company)
                            ]
                        else:
                            # Add
                            st.session_state.saved_jobs.append({
                                "job_title": title,
                                "employer_name": company,
                                "job_city": city,
                                "job_description": desc,
                                "job_required_skills": skills,
                                "job_apply_link": apply_url,
                                "career_compass_match_score": score
                            })
                        st.rerun()
                
                # Job Details
                st.write(f"**Description:** {desc}...")
                if skills:
                    st.write(f"**Skills:** {', '.join(str(s) for s in skills[:5])}")
                if apply_url != "#":
                    st.markdown(f"[🚀 Apply]({apply_url})")
                
                st.markdown("---")

st.caption("Made with ❤️")