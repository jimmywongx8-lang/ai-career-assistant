import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

try:
    from modules.jsearch_client import JSearchClient
except ImportError:
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

with tab1:
    st.header("📄 Upload Your CV")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])
    
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

with tab2:
    st.header("🔍 AI Profile Analysis")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV in the first tab.")
    else:
        if st.button("Analyze My Profile", type="primary"):
            with st.spinner("🤖 AI is analyzing your CV..."):
                try:
                    from groq import Groq
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    analysis_prompt = f"""
                    Analyze this CV:
                    {st.session_state.cv_text[:3000]}
                    
                    Provide:
                    1. Top 5 skills
                    2. Years of experience
                    3. Target job titles
                    4. Key strengths
                    5. Areas for improvement
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
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

with tab3:
    st.header("💼 AI-Powered Job Matching")
    
    if JSearchClient is None:
        st.error("⚠️ JSearchClient not available")
    elif "JSEARCH_API_KEY" not in st.secrets:
        st.error("⚠️ JSearch API key not configured")
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
        
        if st.button("🔍 Find Matching Jobs", type="primary", use_container_width=True):
            with st.spinner("🔎 Searching..."):
                try:
                    client = JSearchClient(api_key=st.secrets["JSEARCH_API_KEY"])
                    
                    user_skills = []
                    if st.session_state.cv_text:
                        skills_keywords = ["Python", "JavaScript", "React", "Node.js", "Docker", "AWS", "Git"]
                        for skill in skills_keywords:
                            if skill.lower() in st.session_state.cv_text.lower():
                                user_skills.append(skill)
                    
                    results = client.search_jobs(
                        query=job_query,
                        location=location if location else None,
                        employment_types=emp_type if emp_type else None,
                        date_posted=date_filter,
                        num_pages=1,
                        user_skills=user_skills
                    )
                    
                    if results.get("data") and len(results["data"]) > 0:
                        st.success(f"✅ Found {len(results['data'])} jobs!")
                        
                        for i, job in enumerate(results["data"]):
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
                        st.warning("No jobs found. Try different search terms.")
                        
                except Exception as e:
                    st.error(f"Search failed: {e}")

with tab4:
    st.header("✍️ AI CV Rewriting")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        job_description = st.text_area("Paste Job Description", height=150)
        
        if st.button("✨ Rewrite My CV"):
            if not job_description:
                st.warning("Please enter a job description")
            else:
                with st.spinner("🤖 Optimizing..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        prompt = f"""
                        Optimize this CV for the job:
                        
                        CV: {st.session_state.cv_text[:2000]}
                        
                        Job: {job_description[:1000]}
                        
                        Provide rewritten CV content.
                        """
                        
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.5,
                            max_tokens=1000
                        )
                        
                        rewritten_cv = response.choices[0].message.content
                        st.success("✅ CV Rewritten!")
                        st.text_area("Optimized CV", rewritten_cv, height=400)
                        
                        st.download_button("📥 Download", data=rewritten_cv, file_name="optimized_cv.txt")
                    except Exception as e:
                        st.error(f"Rewriting failed: {e}")

with tab5:
    st.header("📧 AI Cover Letter Generator")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name")
        with col2:
            job_title = st.text_input("Job Title")
        
        job_desc = st.text_area("Job Description", height=150)
        
        if st.button("✍️ Generate Cover Letter", type="primary"):
            if not company_name or not job_title:
                st.warning("Please fill in company and job title")
            else:
                with st.spinner("🤖 Writing..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        prompt = f"""
                        Write a cover letter:
                        
                        CV: {st.session_state.cv_text[:1500]}
                        Company: {company_name}
                        Position: {job_title}
                        Details: {job_desc[:500]}
                        """
                        
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.5,
                            max_tokens=600
                        )
                        
                        cover_letter = response.choices[0].message.content
                        st.success("✅ Cover Letter Generated!")
                        st.text_area("Your Cover Letter", cover_letter, height=400)
                        
                        st.download_button("📥 Download", data=cover_letter, file_name="cover_letter.txt")
                    except Exception as e:
                        st.error(f"Generation failed: {e}")