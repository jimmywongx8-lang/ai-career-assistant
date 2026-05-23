# pages/1_Services.py
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

try:
    from modules.jsearch_client import JSearchClient
except ImportError as e:
    st.error(f"⚠️ Import Error: {e}")
    JSearchClient = None

st.set_page_config(page_title="Services - Career Compass", page_icon="🛠️", layout="wide")

st.title("🛠️ Career Services")
st.markdown("AI-powered tools to accelerate your career journey")

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""
if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 CV Upload", 
    "🔍 AI Profile Analysis", 
    "💼 Job Matching",
    "✍️ CV Rewriting",
    "📧 Cover Letter"
])

# ==================== TAB 1: CV UPLOAD ====================
with tab1:
    st.header("📄 Upload Your CV")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])
    
    if uploaded_file is not None:
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        
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
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        if st.button("Analyze My Profile", type="primary"):
            with st.spinner("🤖 Analyzing your CV..."):
                try:
                    from groq import Groq
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    prompt = f"""
                    You are an expert career coach. Analyze the following CV and provide a professional assessment.
                    
                    CV Content:
                    {st.session_state.cv_text[:3000]}
                    
                    Please provide the analysis in a clean, readable Markdown format with the following sections:
                    
                    1. **🎯 Target Roles**: (Suggest 3-4 suitable job titles)
                    2. **💡 Key Skills**: (List top technical and soft skills found)
                    3. **✅ Top Strengths**: (Bullet points of what they do well)
                    4. **🚀 Areas for Improvement**: (Constructive feedback on what to add or fix)
                    
                    Do NOT output JSON or code blocks. Just use bold headers and bullet points.
                    """
                    
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=600
                    )
                    
                    analysis = response.choices[0].message.content
                    st.session_state.user_profile["analysis"] = analysis
                    st.session_state.user_profile["analyzed"] = True
                    
                    st.success("✅ Analysis Complete!")
                    st.markdown(analysis)
                    
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

# ==================== TAB 3: JOB MATCHING (WITH DEBUG) ====================
with tab3:
    st.header("💼 AI-Powered Job Matching")
    
    if JSearchClient is None:
        st.error("⚠️ Job matching module not loaded.")
    elif "JSEARCH_API_KEY" not in st.secrets:
        st.error("⚠️ JSearch API key not configured.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            job_query = st.text_input("Target Role", value="software developer")
        with col2:
            location = st.text_input("Location", placeholder="Remote, New York, etc.")
        
        with st.expander("🔍 Advanced Filters"):
            emp_type = st.multiselect("Employment Type", ["FULLTIME", "CONTRACTOR", "PARTTIME"], default=[])
            date_filter = st.selectbox("Posted Within", ["all", "week", "month"], index=0)
            num_results = st.slider("Number of Results", 5, 20, 10)
        
        # Debug checkbox
        show_debug = st.checkbox("🔍 Show Debug Information", value=False)
        
        if st.button("🔍 Find Matching Jobs", type="primary", use_container_width=True):
            with st.spinner("🔎 Searching..."):
                try:
                    # Extract skills from CV
                    user_skills = []
                    if st.session_state.cv_text:
                        skills_keywords = ["Python", "JavaScript", "React", "Node.js", "Docker", "AWS", "Git", "Agile", "Kubernetes", "Jenkins"]
                        for skill in skills_keywords:
                            if skill.lower() in st.session_state.cv_text.lower():
                                user_skills.append(skill)
                    
                    if show_debug:
                        st.info(f"🔍 **Debug Info:**")
                        st.write(f"- Query: {job_query}")
                        st.write(f"- Location: {location}")
                        st.write(f"- Employment Types: {emp_type}")
                        st.write(f"- Date Filter: {date_filter}")
                        st.write(f"- Extracted Skills: {user_skills}")
                    
                    # Initialize client and search
                    client = JSearchClient(api_key=st.secrets["JSEARCH_API_KEY"])
                    results = client.search_jobs(
                        query=job_query,
                        location=location if location else None,
                        employment_types=emp_type if emp_type else None,
                        date_posted=date_filter,
                        num_pages=1,
                        user_skills=user_skills
                    )
                    
                    if show_debug:
                        st.write("📊 **API Response:**")
                        st.json(results)
                    
                    # Display Results
                    if results.get("data") and len(results["data"]) > 0:
                        st.success(f"✅ Found {len(results['data'])} jobs!")
                        
                        for i, job in enumerate(results["data"]):
                            # Debug: Check what type job is
                            if show_debug:
                                st.write(f"🔍 **Job {i} type:** {type(job)}")
                                if isinstance(job, dict):
                                    st.write(f"- Job Title: {job.get('job_title', 'N/A')}")
                                    st.write(f"- Employer: {job.get('employer_name', 'N/A')}")
                                    st.write(f"- Match Score: {job.get('career_compass_match_score', 'N/A')}")
                                else:
                                    st.error(f"⚠️ Job {i} is not a dictionary! It's a {type(job)}")
                            
                            # Skip if not a dict
                            if not isinstance(job, dict):
                                st.warning(f"⚠️ Skipping job {i} - invalid format")
                                continue

                            match_score = job.get("career_compass_match_score", 0)
                            
                            if match_score >= 0.7:
                                badge = "🟢 Excellent Match"
                            elif match_score >= 0.4:
                                badge = "🟡 Good Match"
                            else:
                                badge = "⚪ Potential Fit"
                            
                            st.markdown(f"**{job.get('job_title', 'N/A')}** - {job.get('employer_name', 'Unknown')} {badge}")
                            st.caption(f"{job.get('job_city', '')} {job.get('job_state', '')}")
                            
                            with st.expander("View Details"):
                                if job.get("job_required_skills"):
                                    st.write("**Skills:**", ", ".join(job["job_required_skills"][:5]))
                                if job.get("job_apply_link"):
                                    st.link_button("🚀 Apply Now", job["job_apply_link"])
                    else:
                        st.warning("⚠️ No jobs found. Try different search terms.")
                        if show_debug:
                            st.info("💡 The API returned successfully but no jobs were found in the 'data' field.")
                        
                except Exception as e:
                    st.error(f"❌ Search failed: {e}")
                    import traceback
                    st.code(traceback.format_exc())
                    st.error("💡 This error might be due to API issues. Check your JSEARCH_API_KEY in Streamlit secrets.")

# ==================== TAB 4 & 5: PLACEHOLDERS ====================
with tab4:
    st.header("✍️ CV Rewriting")
    st.info("Coming soon!")

with tab5:
    st.header("📧 Cover Letter")
    st.info("Coming soon!")