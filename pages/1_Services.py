# pages/1_Services.py
import streamlit as st
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent.parent))

try:
    from modules.jsearch_client import JSearchClient
except ImportError as e:
    st.error(f"️ Import Error: {e}")
    JSearchClient = None

st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="wide")

# Custom CSS
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
    .match-badge { display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; margin: 10px 0; }
    .excellent { background-color: #10b981; }
    .good { background-color: #f59e0b; }
    .potential { background-color: #6b7280; }
    .skill-tag { background-color: rgba(255,255,255,0.3); padding: 3px 8px; border-radius: 12px; font-size: 12px; margin: 2px; display: inline-block; }
    .location-tag { opacity: 0.8; font-size: 14px; }
    .saved-job-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 15px; border-radius: 8px; margin-bottom: 15px; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("🧭 Career Compass")
st.markdown("### AI-powered tools to accelerate your career journey")

# Initialize session state
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""
if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []
if "search_results" not in st.session_state:
    st.session_state.search_results = None

# Sidebar - Saved Jobs
with st.sidebar:
    st.header("💼 Saved Jobs")
    if len(st.session_state.saved_jobs) == 0:
        st.info("No saved jobs yet. Click the bookmark icon on jobs you're interested in!")
    else:
        st.success(f"✅ {len(st.session_state.saved_jobs)} job(s) saved")
        
        for i, job in enumerate(st.session_state.saved_jobs):
            with st.expander(f"💾 {job.get('job_title', 'Job')[:30]}..."):
                st.write(f"**🏢 {job.get('employer_name', 'Unknown')}**")
                st.write(f" {job.get('job_city', '')} {job.get('job_state', '')}")
                
                match_score = job.get("career_compass_match_score", 0)
                if match_score >= 0.7: st.write("🟢 Excellent Match")
                elif match_score >= 0.4: st.write("🟡 Good Match")
                else: st.write("⚪ Potential Fit")
                
                if st.button("🗑️ Remove", key=f"remove_{i}"):
                    st.session_state.saved_jobs.pop(i)
                    st.rerun()
        
        if len(st.session_state.saved_jobs) > 0:
            jobs_json = json.dumps(st.session_state.saved_jobs, indent=2)
            st.download_button(
                label="📥 Download Saved Jobs",
                data=jobs_json,
                file_name="saved_jobs.json",
                mime="application/json",
                use_container_width=True
            )
        
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.saved_jobs = []
            st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 CV Upload", "🔍 AI Profile Analysis", "💼 Job Matching", "✍️ CV Rewriting", "📧 Cover Letter"
])

# ==================== TAB 1: CV UPLOAD ====================
with tab1:
    st.header("📄 Upload Your CV")
    st.markdown("Upload your CV to get started with AI-powered career tools")
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])
    
    if uploaded_file is not None:
        st.success(f"✅ Uploaded: **{uploaded_file.name}**")
        try:
            if uploaded_file.type == "application/pdf":
                import PyPDF2
                from io import BytesIO
                pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
                cv_text = ""
                for page in pdf_reader.pages:
                    cv_text += page.extract_text()
            else:
                cv_text = uploaded_file.read().decode("utf-8")
            
            st.session_state.cv_text = cv_text
            st.session_state.user_profile["cv_uploaded"] = True
            
            with st.expander("📋 View CV Preview"):
                st.text_area("CV Content", cv_text, height=300)
        except Exception as e:
            st.error(f"Error: {e}")

# ==================== TAB 2: AI PROFILE ANALYSIS ====================
with tab2:
    st.header("🔍 AI Profile Analysis")
    st.markdown("Get AI-powered insights about your CV")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV in the first tab.")
    else:
        if st.button("🎯 Analyze My Profile", type="primary", use_container_width=True):
            with st.spinner("🤖 Analyzing your CV..."):
                try:
                    from groq import Groq
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    prompt = f"""
                    You are an expert career coach. Analyze the following CV and provide a professional assessment.
                    CV Content: {st.session_state.cv_text[:3000]}
                    Please provide the analysis in a clean, readable Markdown format with sections: Target Roles, Key Skills, Top Strengths, Areas for Improvement.
                    """
                    
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], max_tokens=600
                    )
                    
                    analysis = response.choices[0].message.content
                    st.session_state.user_profile["analysis"] = analysis
                    st.success("✅ Analysis Complete!")
                    st.markdown(analysis)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

# ==================== TAB 3: JOB MATCHING ====================
with tab3:
    st.header("💼 AI-Powered Job Matching")
    st.markdown("Find jobs that match your skills and experience")
    
    if JSearchClient is None:
        st.error("️ Job matching module not loaded.")
    elif "JSEARCH_API_KEY" not in st.secrets:
        st.error("⚠️ JSearch API key not configured.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            job_query = st.text_input("🎯 Target Role", value="software developer")
        with col2:
            location = st.text_input("📍 Location", placeholder="Remote, New York, etc.")
        
        with st.expander(" Advanced Filters"):
            col1, col2 = st.columns(2)
            with col1:
                emp_type = st.multiselect("Employment Type", ["FULLTIME", "CONTRACTOR", "PARTTIME"], default=["FULLTIME"])
            with col2:
                date_filter = st.selectbox("Posted Within", ["all", "week", "month"], index=0)
        
        if st.button(" Find Matching Jobs", type="primary", use_container_width=True):
            with st.spinner("🔎 Searching for jobs..."):
                try:
                    user_skills = []
                    if st.session_state.cv_text:
                        skills_keywords = ["Python", "JavaScript", "React", "Node.js", "Docker", "AWS", "Git", "Agile", "Kubernetes", "Jenkins"]
                        for skill in skills_keywords:
                            if skill.lower() in st.session_state.cv_text.lower():
                                user_skills.append(skill)
                    
                    client = JSearchClient(api_key=st.secrets["JSEARCH_API_KEY"])
                    results = client.search_jobs(
                        query=job_query, location=location if location else None,
                        employment_types=emp_type if emp_type else None, date_posted=date_filter,
                        num_pages=1, user_skills=user_skills
                    )
                    
                    # Save results to session state so they persist!
                    st.session_state.search_results = results.get("data", [])
                    st.session_state.search_query = job_query
                    
                except Exception as e:
                    st.error(f" Search failed: {e}")
        
        # Display results if they exist in session state
        if st.session_state.search_results:
            st.success(f"✅ Found **{len(st.session_state.search_results)}** matching jobs!")
            st.markdown("---")
            
            for i, job in enumerate(st.session_state.search_results):
                if not isinstance(job, dict): continue

                match_score = job.get("career_compass_match_score", 0)
                job_id = job.get("job_title", "") + job.get("employer_name", "")
                
                # Check if saved
                is_saved = any(
                    s.get("job_title") == job.get("job_title") and s.get("employer_name") == job.get("employer_name")
                    for s in st.session_state.saved_jobs
                )
                
                if match_score >= 0.7: badge_class, badge_text = "excellent", "🟢 Excellent Match"
                elif match_score >= 0.4: badge_class, badge_text = "good", "🟡 Good Match"
                else: badge_class, badge_text = "potential", "⚪ Potential Fit"
                
                st.markdown(f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div class="job-title">{job.get('job_title', 'N/A')}</div>
                            <div class="employer">🏢 {job.get('employer_name', 'Unknown')}</div>
                            <div class="location-tag">📍 {job.get('job_city', '')} {job.get('job_state', '')}</div>
                        </div>
                        <div class="match-badge {badge_class}">{badge_text}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Save Button Logic
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.success("💾 Saved to your jobs list") if is_saved else st.info("Click bookmark to save this job")
                
                with col2:
                    save_label = "💾 Saved" if is_saved else "🔖 Save Job"
                    save_type = "secondary" if is_saved else "primary"
                    
                    if st.button(save_label, key=f"save_{i}_{job_id}", type=save_type, use_container_width=True):
                        if is_saved:
                            st.session_state.saved_jobs = [j for j in st.session_state.saved_jobs if not (j.get("job_title") == job.get("job_title") and j.get("employer_name") == job.get("employer_name"))]
                        else:
                            st.session_state.saved_jobs.append(job)
                        st.rerun()
                
                # Job Details
                with st.expander("📋 View Job Details"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**📝 Description**")
                        st.write(job.get("job_description", "No description available"))
                    with col2:
                        if job.get("job_required_skills"):
                            st.markdown("**💡 Required Skills**")
                            skills_html = "".join([f'<span class="skill-tag">{s}</span>' for s in job["job_required_skills"][:8]])
                            st.markdown(skills_html, unsafe_allow_html=True)
                        if job.get("normalized_salary"):
                            st.markdown("**💰 Salary Range**")
                            salary = job["normalized_salary"]
                            if salary.get("min_annual_usd"):
                                st.info(f"${salary['min_annual_usd']:,} - ${salary['max_annual_usd']:,} / year")
                    
                    if job.get("job_apply_link"):
                        st.markdown(f"""
                        <div style="text-align: center; margin-top: 20px;">
                            <a href="{job['job_apply_link']}" target="_blank" style="background-color: #667eea; color: white; padding: 12px 30px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block;"> Apply Now</a>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown("---")

# ==================== TAB 4 & 5 (Simplified for brevity, same as before) ====================
with tab4:
    st.header("✍️ AI CV Rewriting")
    if not st.session_state.cv_text: st.warning("⚠️ Please upload your CV first.")
    else:
        job_desc = st.text_area("Paste Job Description", height=150)
        if st.button("✨ Rewrite My CV", type="primary", use_container_width=True):
            if job_desc:
                with st.spinner(" Optimizing..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        prompt = f"Optimize this CV for: {job_desc[:1000]}\nCV: {st.session_state.cv_text[:2000]}"
                        response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], max_tokens=1000)
                        st.success("✅ CV Optimized!")
                        st.text_area("Optimized CV", response.choices[0].message.content, height=400)
                    except Exception as e: st.error(f"Error: {e}")

with tab5:
    st.header("📧 AI Cover Letter Generator")
    if not st.session_state.cv_text: st.warning("⚠️ Please upload your CV first.")
    else:
        col1, col2 = st.columns(2)
        with col1: company_name = st.text_input(" Company Name")
        with col2: job_title = st.text_input("💼 Job Title")
        job_desc = st.text_area("📝 Job Description", height=150)
        
        if st.button("✍️ Generate Cover Letter", type="primary", use_container_width=True):
            if company_name and job_title:
                with st.spinner("🤖 Writing..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        prompt = f"Write cover letter for {company_name} - {job_title}.\nCV: {st.session_state.cv_text[:1500]}\nJob: {job_desc[:500]}"
                        response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], max_tokens=600)
                        st.success("✅ Cover Letter Generated!")
                        st.text_area("Your Cover Letter", response.choices[0].message.content, height=400)
                    except Exception as e: st.error(f"Error: {e}")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Made with ❤️ using AI</div>", unsafe_allow_html=True)