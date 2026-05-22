# pages/1_Services.py
"""
Career Compass - Services Page
Features: CV Upload, AI Profile Analysis, Job Matching, CV Rewriting, Cover Letter
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import our modules
try:
    from modules.jsearch_client import JSearchClient
except ImportError as e:
    st.error(f"⚠️ Could not import JSearchClient: {e}")
    st.error("Make sure modules/jsearch_client.py exists and has no syntax errors")

# Page config
st.set_page_config(
    page_title="Services - Career Compass",
    page_icon="🛠️",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .job-card {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .match-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🛠️ Career Services")
st.markdown("AI-powered tools to accelerate your career journey")

# Initialize session state
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""
if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []

# Create tabs for different services
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
    st.markdown("Upload your CV in PDF or TXT format to get started")
    
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=["pdf", "txt"],
        help="We support PDF and TXT formats"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        st.info(f"Size: {uploaded_file.size / 1024:.1f} KB")
        
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
            st.error(f"Error reading file: {e}")

# ==================== TAB 2: AI PROFILE ANALYSIS ====================
with tab2:
    st.header("🔍 AI Profile Analysis")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV in the first tab to analyze it.")
    else:
        st.markdown("Get AI-powered insights about your CV")
        
        if st.button("Analyze My Profile", type="primary"):
            with st.spinner("🤖 AI is analyzing your CV..."):
                try:
                    from groq import Groq
                    
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    analysis_prompt = f"""
                    Analyze this CV and provide:
                    1. Top 5 skills/expertise areas
                    2. Years of experience estimate
                    3. Target job titles
                    4. Key strengths
                    5. Areas for improvement
                    
                    CV:
                    {st.session_state.cv_text[:3000]}
                    
                    Format as JSON with keys: skills, experience_years, target_roles, strengths, improvements
                    """
                    
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": analysis_prompt}],
                        temperature=0.3,
                        max_tokens=500
                    )
                    
                    analysis = response.choices[0].message.content
                    
                    st.session_state.user_profile["analysis"] = analysis
                    st.session_state.user_profile["analyzed"] = True
                    
                    st.success("✅ Analysis Complete!")
                    st.markdown(analysis)
                    st.info("💡 Your profile has been analyzed. You can now use Job Matching tab!")
                    
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

# ==================== TAB 3: JOB MATCHING ====================
with tab3:
    st.header("💼 AI-Powered Job Matching")
    st.markdown("Find jobs that match your skills and experience")
    
    if "JSEARCH_API_KEY" not in st.secrets:
        st.error("⚠️ JSearch API key not configured. Please add it to Streamlit secrets.")
    else:
        default_query = "software developer"
        default_location = ""
        
        if st.session_state.user_profile.get("analyzed"):
            st.info("✨ Using your profile analysis for smarter matching")
        
        col1, col2 = st.columns(2)
        with col1:
            job_query = st.text_input(
                "Target Role", 
                value=default_query,
                help="e.g., Python Developer, Data Analyst, Project Manager"
            )
        with col2:
            location = st.text_input(
                "Location", 
                value=default_location,
                placeholder="Remote, New York, London, etc."
            )
        
        with st.expander("🔍 Advanced Filters"):
            col_a, col_b = st.columns(2)
            with col_a:
                emp_type = st.multiselect(
                    "Employment Type",
                    ["FULLTIME", "CONTRACTOR", "PARTTIME", "INTERN"],
                    default=[]
                )
            with col_b:
                date_filter = st.selectbox(
                    "Posted Within",
                    ["all", "today", "3days", "week", "month"],
                    index=3
                )
            
            num_results = st.slider("Number of Results", 5, 20, 10)
        
        if st.button("🔍 Find Matching Jobs", type="primary", use_container_width=True):
            with st.spinner("🔎 Searching for the best opportunities..."):
                try:
                    # Debug: Show what we're searching for
                    st.info(f"🔍 **Debug** - Query: '{job_query}', Location: '{location}'")
                    
                    client = JSearchClient(api_key=st.secrets["JSEARCH_API_KEY"])
                    
                    user_skills = []
                    if st.session_state.user_profile.get("analyzed"):
                        # Extract skills from analysis if available
                        analysis_text = st.session_state.user_profile.get("analysis", "")
                        if "Team Leadership" in analysis_text:
                            user_skills = ["Team Leadership", "Strategic Planning", "Product Management"]
                    
                    st.info(f"🔍 **Debug** - User Skills: {user_skills}")
                    
                    results = client.search_jobs(
                        query=job_query,
                        location=location if location else None,
                        employment_types=emp_type if emp_type else None,
                        date_posted=date_filter,
                        num_pages=1,
                        user_skills=user_skills
                    )
                    
                    # Debug: Show raw response
                    st.write("📊 **API Response Status:**", results.get("status"))
                    st.write("📊 **Number of jobs:**", len(results.get("data", [])))
                    
                    if results.get("data") and len(results["data"]) > 0:
                        st.success(f"✅ Found {len(results['data'])} matching jobs!")
                        display_jobs(results["data"], job_query)
                    else:
                        st.warning("⚠️ No jobs found. Try broadening your search terms.")
                        st.info(f"📋 **Debug Info** - Full response: {results}")
                        
                except Exception as e:
                    st.error(f"❌ Search failed: {e}")
                    import traceback
                    st.code(traceback.format_exc())

# ==================== TAB 4: CV REWRITING ====================
with tab4:
    st.header("✍️ AI CV Rewriting")
    st.markdown("Optimize your CV for specific job descriptions")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        job_description = st.text_area(
            "Paste Job Description",
            height=150,
            placeholder="Paste the job description you're targeting..."
        )
        
        if st.button("✨ Rewrite My CV"):
            if not job_description:
                st.warning("Please enter a job description")
            else:
                with st.spinner("🤖 Optimizing your CV..."):
                    try:
                        from groq import Groq
                        
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        rewrite_prompt = f"""
                        Rewrite and optimize this CV to better match the job description.
                        
                        Original CV:
                        {st.session_state.cv_text[:2000]}
                        
                        Job Description:
                        {job_description[:1000]}
                        
                        Provide the rewritten CV content.
                        """
                        
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": rewrite_prompt}],
                            temperature=0.5,
                            max_tokens=1000
                        )
                        
                        rewritten_cv = response.choices[0].message.content
                        
                        st.success("✅ CV Rewritten!")
                        st.text_area("Optimized CV", rewritten_cv, height=400)
                        
                        st.download_button(
                            label="📥 Download Rewritten CV",
                            data=rewritten_cv,
                            file_name="optimized_cv.txt",
                            mime="text/plain"
                        )
                        
                    except Exception as e:
                        st.error(f"Rewriting failed: {e}")

# ==================== TAB 5: COVER LETTER ====================
with tab5:
    st.header("📧 AI Cover Letter Generator")
    st.markdown("Create personalized cover letters in seconds")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name")
        with col2:
            job_title = st.text_input("Job Title")
        
        job_desc = st.text_area(
            "Job Description",
            height=150,
            placeholder="Paste key requirements..."
        )
        
        if st.button("✍️ Generate Cover Letter", type="primary"):
            if not company_name or not job_title:
                st.warning("Please fill in company name and job title")
            else:
                with st.spinner("🤖 Writing your cover letter..."):
                    try:
                        from groq import Groq
                        
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        cover_letter_prompt = f"""
                        Write a professional cover letter for this position.
                        
                        Candidate CV:
                        {st.session_state.cv_text[:1500]}
                        
                        Company: {company_name}
                        Position: {job_title}
                        Job Details: {job_desc[:500]}
                        
                        Write a compelling 3-4 paragraph cover letter.
                        """
                        
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": cover_letter_prompt}],
                            temperature=0.5,
                            max_tokens=600
                        )
                        
                        cover_letter = response.choices[0].message.content
                        
                        st.success("✅ Cover Letter Generated!")
                        st.text_area("Your Cover Letter", cover_letter, height=400)
                        
                        st.download_button(
                            label="📥 Download Cover Letter",
                            data=cover_letter,
                            file_name="cover_letter.txt",
                            mime="text/plain"
                        )
                        
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

# Helper function to display jobs
def display_jobs(jobs, query):
    """Display job listings with match scores"""
    
    for i, job in enumerate(jobs):
        match_score = job.get("career_compass_match_score", 0)
        
        if match_score >= 0.7:
            badge_html = '<span style="background:#10b981;color:white;padding:4px 12px;border-radius:20px;font-size:0.8rem;">🟢 Excellent Match</span>'
        elif match_score >= 0.4:
            badge_html = '<span style="background:#f59e0b;color:white;padding:4px 12px;border-radius:20px;font-size:0.8rem;">🟡 Good Match</span>'
        else:
            badge_html = '<span style="background:#6b7280;color:white;padding:4px 12px;border-radius:20px;font-size:0.8rem;">⚪ Potential Fit</span>'
        
        st.markdown(f"""
        <div class="job-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h4 style="margin: 0 0 4px 0; color: #1f2937;">{job.get('job_title', 'N/A')}</h4>
                    <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 0.9rem;">
                        <strong>{job.get('employer_name', 'Unknown Company')}</strong> • 
                        {job.get('job_city', '')}{', ' if job.get('job_city') and job.get('job_state') else ''}{job.get('job_state', '')}
                    </p>
                </div>
                {badge_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("View Details & Apply"):
            if job.get("normalized_salary"):
                salary = job["normalized_salary"]
                if salary.get("min_annual_usd"):
                    st.caption(f"💰 Estimated Salary: ${salary['min_annual_usd']:,} - ${salary['max_annual_usd']:,} USD/year")
            
            if job.get("job_required_skills"):
                st.markdown("**Required Skills:**")
                st.write(", ".join(job["job_required_skills"][:5]))
            
            apply_link = job.get("job_apply_link", "#")
            st.link_button("🚀 Apply Now", apply_link, type="primary")
            
            if st.button("💾 Save for Later", key=f"save_{i}"):
                st.session_state.saved_jobs.append(job)
                st.success("Job saved! ✨")
            
            st.divider()