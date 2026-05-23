# pages/1_Services.py
import streamlit as st
import sys
from pathlib import Path
import json
import hashlib

sys.path.append(str(Path(__file__).parent.parent))

try:
    from modules.jsearch_client import JSearchClient
except ImportError as e:
    st.error(f"⚠️ Import Error: {e}")
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .job-title { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
    .employer { font-size: 18px; opacity: 0.9; }
    .match-badge { display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; }
    .excellent { background-color: #10b981; }
    .good { background-color: #f59e0b; }
    .potential { background-color: #6b7280; }
    .skill-tag { background-color: rgba(255,255,255,0.3); padding: 3px 8px; border-radius: 12px; font-size: 12px; margin: 2px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

st.title("🧭 Career Compass")
st.markdown("### AI-powered tools to accelerate your career journey")

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""
if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []
if "search_results" not in st.session_state:
    st.session_state.search_results = None

# Sidebar
with st.sidebar:
    st.header("💼 Saved Jobs")
    if len(st.session_state.saved_jobs) == 0:
        st.info("No saved jobs yet.")
    else:
        st.success(f"✅ {len(st.session_state.saved_jobs)} job(s) saved")
        for i, job in enumerate(st.session_state.saved_jobs):
            job_title = str(job.get('job_title', 'Job'))[:30]
            with st.expander(f"💾 {job_title}..."):
                st.write(f"🏢 {job.get('employer_name', 'Unknown')}")
                if st.button("🗑️ Remove", key=f"remove_job_{i}_{hash(str(job))}"):
                    st.session_state.saved_jobs.pop(i)
                    st.rerun()
        
        if len(st.session_state.saved_jobs) > 0:
            jobs_json = json.dumps(st.session_state.saved_jobs, indent=2)
            st.download_button(
                label="📥 Download",
                data=jobs_json,
                file_name="saved_jobs.json",
                mime="application/json",
                use_container_width=True
            )

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 CV Upload", "🔍 AI Profile Analysis", "💼 Job Matching", "✍️ CV Rewriting", "📧 Cover Letter"
])

# TAB 1
with tab1:
    st.header("📄 Upload Your CV")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"], key="cv_uploader")
    
    if uploaded_file is not None:
        st.success(f"✅ Uploaded: **{uploaded_file.name}**")
        try:
            if uploaded_file.type == "application/pdf":
                import PyPDF2
                from io import BytesIO
                pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
                cv_text = "".join(page.extract_text() for page in pdf_reader.pages)
            else:
                cv_text = uploaded_file.read().decode("utf-8")
            
            st.session_state.cv_text = cv_text
            st.session_state.user_profile["cv_uploaded"] = True
        except Exception as e:
            st.error(f"Error: {e}")

# TAB 2
with tab2:
    st.header("🔍 AI Profile Analysis")
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        if st.button("🎯 Analyze My Profile", type="primary", use_container_width=True, key="analyze_btn"):
            with st.spinner("🤖 Analyzing..."):
                try:
                    from groq import Groq
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    prompt = f"Analyze this CV: {st.session_state.cv_text[:3000]}"
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant", 
                        messages=[{"role": "user", "content": prompt}], 
                        max_tokens=600
                    )
                    st.success("✅ Analysis Complete!")
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

# TAB 3
with tab3:
    st.header("💼 AI-Powered Job Matching")
    
    if JSearchClient is None:
        st.error("⚠️ Job matching module not loaded.")
    elif "JSEARCH_API_KEY" not in st.secrets:
        st.error("⚠️ JSearch API key not configured.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            job_query = st.text_input("🎯 Target Role", value="software developer", key="job_query_input")
        with col2:
            location = st.text_input("📍 Location", placeholder="Remote, New York, etc.", key="location_input")
        
        with st.expander("🔧 Advanced Filters"):
            emp_type = st.multiselect("Employment Type", ["FULLTIME", "CONTRACTOR", "PARTTIME"], default=["FULLTIME"], key="emp_type_sel")
            date_filter = st.selectbox("Posted Within", ["all", "week", "month"], index=0, key="date_filter_sel")
        
        if st.button("🔍 Find Matching Jobs", type="primary", use_container_width=True, key="find_jobs_btn"):
            with st.spinner("🔎 Searching..."):
                try:
                    user_skills = []
                    if st.session_state.cv_text:
                        for skill in ["Python", "JavaScript", "React", "Node.js", "Docker", "AWS", "Git", "Agile"]:
                            if skill.lower() in st.session_state.cv_text.lower():
                                user_skills.append(skill)
                    
                    client = JSearchClient(api_key=st.secrets["JSEARCH_API_KEY"])
                    results = client.search_jobs(
                        query=job_query, location=location if location else None,
                        employment_types=emp_type if emp_type else None, 
                        date_posted=date_filter, num_pages=1, user_skills=user_skills
                    )
                    
                    st.session_state.search_results = results.get("data", [])
                    st.success(f"✅ Found {len(st.session_state.search_results)} jobs!")
                    
                except Exception as e:
                    st.error(f"❌ Search failed: {e}")
        
        if st.session_state.search_results:
            st.markdown("---")
            
            for i, job in enumerate(st.session_state.search_results):
                if not isinstance(job, dict):
                    continue
                
                # Safe extraction with defaults
                job_title = str(job.get("job_title") or "Unknown Position")
                employer = str(job.get("employer_name") or "Unknown Company")
                city = str(job.get("job_city") or "")
                state = str(job.get("job_state") or "")
                description = str(job.get("job_description") or "No description available")
                skills = job.get("job_required_skills") or []
                salary = job.get("normalized_salary") or {}
                apply_link = job.get("job_apply_link") or "#"
                match_score = float(job.get("career_compass_match_score") or 0)
                
                if match_score >= 0.7:
                    badge_class, badge_text = "excellent", "🟢 Excellent Match"
                elif match_score >= 0.4:
                    badge_class, badge_text = "good", "🟡 Good Match"
                else:
                    badge_class, badge_text = "potential", "⚪ Potential Fit"
                
                is_saved = any(
                    str(s.get("job_title")) == job_title and str(s.get("employer_name")) == employer
                    for s in st.session_state.saved_jobs
                )
                
                st.markdown(f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div class="job-title">{job_title}</div>
                            <div class="employer">🏢 {employer}</div>
                            <div>📍 {city} {state}</div>
                        </div>
                        <div class="match-badge {badge_class}">{badge_text}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.success("💾 Saved") if is_saved else st.info("Click to save")
                
                with col2:
                    btn_label = "💾 Saved" if is_saved else "🔖 Save"
                    btn_type = "secondary" if is_saved else "primary"
                    unique_key = f"save_btn_{i}_{hashlib.md5(f'{job_title}{employer}'.encode()).hexdigest()}"
                    if st.button(btn_label, key=unique_key, type=btn_type, use_container_width=True):
                        if is_saved:
                            st.session_state.saved_jobs = [
                                j for j in st.session_state.saved_jobs 
                                if not (str(j.get("job_title")) == job_title and str(j.get("employer_name")) == employer)
                            ]
                        else:
                            st.session_state.saved_jobs.append(job)
                        st.rerun()
                
                # Job Details - ONLY show if we have valid data
                with st.expander("📋 View Details"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**📝 Description**")
                        desc_text = description[:500] + "..." if len(str(description)) > 500 else description
                        st.write(desc_text)
                    
                    with c2:
                        if skills and len(skills) > 0:
                            st.markdown("**💡 Skills**")
                            skills_html = "".join([f'<span class="skill-tag">{str(s)}</span>' for s in skills[:6]])
                            st.markdown(skills_html, unsafe_allow_html=True)
                        
                        if salary and salary.get("min_annual_usd"):
                            st.markdown("**💰 Salary**")
                            min_sal = salary.get("min_annual_usd", 0)
                            max_sal = salary.get("max_annual_usd", 0)
                            st.info(f"${min_sal:,} - ${max_sal:,}")
                    
                    if apply_link and apply_link != "#":
                        st.markdown(f"""
                        <div style="text-align: center; margin-top: 15px;">
                            <a href="{apply_link}" target="_blank" 
                               style="background-color: #667eea; color: white; 
                                      padding: 10px 25px; border-radius: 5px; 
                                      text-decoration: none; font-weight: bold;">
                                🚀 Apply Now
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")

# TAB 4
with tab4:
    st.header("✍️ CV Rewriting")
    if not st.session_state.cv_text:
        st.warning("⚠️ Upload CV first")
    else:
        job_desc = st.text_area("Job Description", height=150, key="cv_rewrite_desc")
        if st.button("✨ Rewrite CV", type="primary", use_container_width=True, key="cv_rewrite_btn"):
            if job_desc:
                with st.spinner("Optimizing..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        prompt = f"Optimize CV for: {job_desc[:1000]}\nCV: {st.session_state.cv_text[:2000]}"
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant", 
                            messages=[{"role": "user", "content": prompt}], 
                            max_tokens=1000
                        )
                        st.success("✅ Done!")
                        st.text_area("Optimized CV", response.choices[0].message.content, height=400, key="cv_rewrite_output")
                    except Exception as e:
                        st.error(f"Error: {e}")

# TAB 5
with tab5:
    st.header("📧 Cover Letter")
    if not st.session_state.cv_text:
        st.warning("⚠️ Upload CV first")
    else:
        col1, col2 = st.columns(2)
        with col1: 
            company = st.text_input("Company", key="cl_company")
        with col2: 
            title = st.text_input("Job Title", key="cl_title")
        job_desc = st.text_area("Job Description", height=150, key="cl_desc")
        
        if st.button("✍️ Generate", type="primary", use_container_width=True, key="cl_generate_btn"):
            if company and title:
                with st.spinner("Writing..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        prompt = f"Cover letter for {company} - {title}.\nCV: {st.session_state.cv_text[:1500]}"
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant", 
                            messages=[{"role": "user", "content": prompt}], 
                            max_tokens=600
                        )
                        st.success("✅ Done!")
                        st.text_area("Cover Letter", response.choices[0].message.content, height=400, key="cl_output")
                    except Exception as e:
                        st.error(f"Error: {e}")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Made with ❤️ using AI</div>", unsafe_allow_html=True)