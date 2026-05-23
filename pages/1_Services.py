# pages/1_Services.py - SIMPLIFIED VERSION
import streamlit as st
import sys
from pathlib import Path
import json
import hashlib

sys.path.append(str(Path(__file__).parent.parent))

try:
    from modules.jsearch_client import JSearchClient
except ImportError:
    JSearchClient = None

st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="wide")

st.markdown("""
<style>
    .job-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    .job-title { font-size: 24px; font-weight: bold; }
    .match-badge { 
        display: inline-block; 
        padding: 5px 15px; 
        border-radius: 20px; 
        font-weight: bold;
        background-color: #f59e0b;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧭 Career Compass")

if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""

# Sidebar
with st.sidebar:
    st.header("💼 Saved Jobs")
    if st.session_state.saved_jobs:
        for i, job in enumerate(st.session_state.saved_jobs):
            st.write(f"{i+1}. {job.get('job_title', 'Job')}")
        if st.button("🗑️ Clear All"):
            st.session_state.saved_jobs = []
            st.rerun()
    else:
        st.info("No saved jobs")

tab1, tab2, tab3 = st.tabs(["📄 CV Upload", "🔍 Analysis", "💼 Jobs"])

with tab1:
    st.header("Upload CV")
    uploaded = st.file_uploader("Choose file", type=["txt", "pdf"], key="up1")
    if uploaded:
        if uploaded.type == "text/plain":
            st.session_state.cv_text = uploaded.read().decode("utf-8")
        st.success("✅ Uploaded!")

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
                messages=[{"role": "user", "content": f"Analyze: {st.session_state.cv_text[:2000]}"}]
            )
            st.write(resp.choices[0].message.content)
        except Exception as e:
            st.error(str(e))

with tab3:
    st.header("Job Matching")
    
    if JSearchClient is None:
        st.error("Module not loaded")
    elif st.button("🔍 Search Jobs", key="btn_search"):
        try:
            client = JSearchClient(api_key=st.secrets.get("JSEARCH_API_KEY", ""))
            results = client.search_jobs(
                query="software developer",
                num_pages=1,
                user_skills=["Python", "JavaScript"]
            )
            st.session_state.search_results = results.get("data", [])
            st.success(f"Found {len(st.session_state.search_results)} jobs!")
        except Exception as e:
            st.error(f"Error: {e}")
    
    if st.session_state.search_results:
        for idx, job in enumerate(st.session_state.search_results):
            if not isinstance(job, dict):
                continue
            
            title = str(job.get("job_title", "Job"))
            company = str(job.get("employer_name", "Company"))
            city = str(job.get("job_city", ""))
            desc = str(job.get("job_description", ""))[:300]
            skills = job.get("job_required_skills", []) or []
            salary = job.get("normalized_salary", {}) or {}
            apply_url = job.get("job_apply_link", "#")
            score = float(job.get("career_compass_match_score", 0))
            
            # Determine match level
            if score >= 0.7: badge = "🟢 Excellent"
            elif score >= 0.4: badge = "🟡 Good"
            else: badge = "⚪ Match"
            
            # Check if saved
            is_saved = any(
                str(s.get("job_title")) == title and str(s.get("employer_name")) == company
                for s in st.session_state.saved_jobs
            )
            
            # Job Card
            st.markdown(f"""
            <div class="job-card">
                <div class="job-title">{title}</div>
                <div>🏢 {company} | 📍 {city}</div>
                <div style="margin-top:10px;"><span class="match-badge">{badge}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Save button
            btn_key = f"save_{idx}_{hashlib.md5(f'{title}{company}'.encode()).hexdigest()}"
            col1, col2 = st.columns([4, 1])
            with col1:
                st.success("Saved") if is_saved else st.info("Click to save")
            with col2:
                if st.button("💾 Save", key=btn_key, type="primary" if not is_saved else "secondary"):
                    if is_saved:
                        st.session_state.saved_jobs = [
                            j for j in st.session_state.saved_jobs
                            if not (str(j.get("job_title")) == title and str(j.get("employer_name")) == company)
                        ]
                    else:
                        st.session_state.saved_jobs.append(job)
                    st.rerun()
            
            # Simple job details - NO columns, NO complex layout
            st.markdown("**Description:**")
            st.write(desc + "..." if len(desc) > 300 else desc)
            
            if skills:
                st.markdown("**Skills:** " + ", ".join(str(s) for s in skills[:5]))
            
            if salary and salary.get("min_annual_usd"):
                st.markdown(f"**Salary:** ${salary['min_annual_usd']:,} - ${salary['max_annual_usd']:,}")
            
            if apply_url and apply_url != "#":
                st.markdown(f"[🚀 Apply Here]({apply_url})")
            
            st.markdown("---")

st.markdown("---")
st.caption("Made with ❤️ using AI")