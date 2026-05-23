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

st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="wide")

# Custom CSS for better styling
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
    .job-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .employer {
        font-size: 18px;
        opacity: 0.9;
    }
    .match-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        margin: 10px 0;
    }
    .excellent { background-color: #10b981; }
    .good { background-color: #f59e0b; }
    .potential { background-color: #6b7280; }
    .salary-tag {
        background-color: rgba(255,255,255,0.2);
        padding: 5px 10px;
        border-radius: 5px;
        margin: 5px;
        display: inline-block;
    }
    .skill-tag {
        background-color: rgba(255,255,255,0.3);
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px;
        display: inline-block;
    }
    .apply-button {
        background-color: #ffffff;
        color: #667eea;
        padding: 10px 20px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    .location-tag {
        opacity: 0.8;
        font-size: 14px;
    }
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

# ==================== TAB 3: JOB MATCHING ====================
with tab3:
    st.header("💼 AI-Powered Job Matching")
    st.markdown("Find jobs that match your skills and experience")
    
    if JSearchClient is None:
        st.error("⚠️ Job matching module not loaded.")
    elif "JSEARCH_API_KEY" not in st.secrets:
        st.error("⚠️ JSearch API key not configured.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            job_query = st.text_input("🎯 Target Role", value="software developer", 
                                     help="Enter the job title you're looking for")
        with col2:
            location = st.text_input("📍 Location", placeholder="Remote, New York, etc.",
                                    help="Enter location or leave blank for remote")
        
        with st.expander("🔧 Advanced Filters"):
            col1, col2 = st.columns(2)
            with col1:
                emp_type = st.multiselect("Employment Type", 
                                         ["FULLTIME", "CONTRACTOR", "PARTTIME"], 
                                         default=["FULLTIME"])
            with col2:
                date_filter = st.selectbox("Posted Within", 
                                          ["all", "week", "month"], 
                                          index=0)
        
        if st.button("🔍 Find Matching Jobs", type="primary", use_container_width=True):
            with st.spinner("🔎 Searching for jobs..."):
                try:
                    # Extract skills from CV
                    user_skills = []
                    if st.session_state.cv_text:
                        skills_keywords = ["Python", "JavaScript", "React", "Node.js", 
                                         "Docker", "AWS", "Git", "Agile", "Kubernetes", "Jenkins"]
                        for skill in skills_keywords:
                            if skill.lower() in st.session_state.cv_text.lower():
                                user_skills.append(skill)
                    
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
                    
                    if results.get("data") and len(results["data"]) > 0:
                        st.success(f"✅ Found **{len(results['data'])}** matching jobs!")
                        st.markdown("---")
                        
                        for i, job in enumerate(results["data"]):
                            if not isinstance(job, dict):
                                continue

                            match_score = job.get("career_compass_match_score", 0)
                            
                            # Determine badge class
                            if match_score >= 0.7:
                                badge_class = "excellent"
                                badge_text = "🟢 Excellent Match"
                            elif match_score >= 0.4:
                                badge_class = "good"
                                badge_text = "🟡 Good Match"
                            else:
                                badge_class = "potential"
                                badge_text = "⚪ Potential Fit"
                            
                            # Job card
                            st.markdown(f"""
                            <div class="job-card">
                                <div class="job-title">{job.get('job_title', 'N/A')}</div>
                                <div class="employer">🏢 {job.get('employer_name', 'Unknown')}</div>
                                <div class="location-tag">📍 {job.get('job_city', '')} {job.get('job_state', '')}</div>
                                <div class="match-badge {badge_class}">{badge_text} ({match_score*100:.0f}%)</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Job details in expander
                            with st.expander("📋 View Job Details"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("**📝 Description**")
                                    st.write(job.get("job_description", "No description available"))
                                
                                with col2:
                                    if job.get("job_required_skills"):
                                        st.markdown("**💡 Required Skills**")
                                        skills_html = "".join([f'<span class="skill-tag">{s}</span>' 
                                                              for s in job["job_required_skills"][:8]])
                                        st.markdown(skills_html, unsafe_allow_html=True)
                                    
                                    if job.get("normalized_salary"):
                                        st.markdown("**💰 Salary Range**")
                                        salary = job["normalized_salary"]
                                        if salary.get("min_annual_usd") and salary.get("max_annual_usd"):
                                            st.markdown(f"""
                                            <div style="background-color: #f0f9ff; padding: 10px; border-radius: 5px; margin: 10px 0;">
                                                <strong>${salary['min_annual_usd']:,} - ${salary['max_annual_usd']:,}</strong> / year
                                            </div>
                                            """, unsafe_allow_html=True)
                                
                                if job.get("job_apply_link"):
                                    st.markdown(f"""
                                    <div style="text-align: center; margin-top: 20px;">
                                        <a href="{job['job_apply_link']}" target="_blank" 
                                           style="background-color: #667eea; color: white; 
                                                  padding: 12px 30px; border-radius: 5px; 
                                                  text-decoration: none; font-weight: bold;
                                                  display: inline-block;">
                                            🚀 Apply Now
                                        </a>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            st.markdown("---")
                    else:
                        st.warning("⚠️ No jobs found. Try different search terms.")
                        
                except Exception as e:
                    st.error(f"❌ Search failed: {e}")

# ==================== TAB 4: CV REWRITING ====================
with tab4:
    st.header("✍️ AI CV Rewriting")
    st.markdown("Optimize your CV for specific job descriptions")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        job_description = st.text_area("Paste Job Description", height=150,
                                      placeholder="Paste the job description you want to optimize your CV for...")
        
        if st.button("✨ Rewrite My CV", type="primary", use_container_width=True):
            if not job_description:
                st.warning("Please enter a job description")
            else:
                with st.spinner("🤖 Optimizing your CV..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        prompt = f"""
                        Optimize this CV for the following job description:
                        
                        CV: {st.session_state.cv_text[:2000]}
                        
                        Job Description: {job_description[:1000]}
                        
                        Provide an optimized version of the CV that highlights relevant skills and experience.
                        Keep it professional and concise.
                        """
                        
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=1000
                        )
                        
                        rewritten_cv = response.choices[0].message.content
                        st.success("✅ CV Optimized!")
                        st.text_area("Optimized CV", rewritten_cv, height=400)
                        
                        st.download_button("📥 Download Optimized CV", 
                                         data=rewritten_cv, 
                                         file_name="optimized_cv.txt",
                                         mime="text/plain")
                    except Exception as e:
                        st.error(f"Rewriting failed: {e}")

# ==================== TAB 5: COVER LETTER ====================
with tab5:
    st.header("📧 AI Cover Letter Generator")
    st.markdown("Generate personalized cover letters in seconds")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("🏢 Company Name", 
                                        placeholder="e.g., Google, Microsoft")
        with col2:
            job_title = st.text_input("💼 Job Title", 
                                     placeholder="e.g., Software Engineer")
        
        job_desc = st.text_area("📝 Job Description", height=150,
                               placeholder="Paste the job description...")
        
        if st.button("✍️ Generate Cover Letter", type="primary", use_container_width=True):
            if not company_name or not job_title:
                st.warning("Please fill in company and job title")
            else:
                with st.spinner("🤖 Writing your cover letter..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        prompt = f"""
                        Write a professional cover letter for the following:
                        
                        My CV: {st.session_state.cv_text[:1500]}
                        Company: {company_name}
                        Position: {job_title}
                        Job Details: {job_desc[:500] if job_desc else "Not provided"}
                        
                        Make it professional, concise (300-400 words), and highlight relevant skills.
                        """
                        
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=600
                        )
                        
                        cover_letter = response.choices[0].message.content
                        st.success("✅ Cover Letter Generated!")
                        st.text_area("Your Cover Letter", cover_letter, height=400)
                        
                        st.download_button("📥 Download Cover Letter", 
                                         data=cover_letter, 
                                         file_name="cover_letter.txt",
                                         mime="text/plain")
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Made with ❤️ using AI</div>", 
           unsafe_allow_html=True)