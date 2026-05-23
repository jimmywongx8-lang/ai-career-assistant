import streamlit as st
import sys
from pathlib import Path
import json
import hashlib
import pandas as pd

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

if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""

with st.sidebar:
    st.header("💼 Saved Jobs")
    
    if st.session_state.saved_jobs:
        st.success(f"✅ {len(st.session_state.saved_jobs)} jobs saved")
        
        for i, job in enumerate(st.session_state.saved_jobs):
            title = job.get('job_title', 'Unknown')[:35]
            with st.expander(f"**{i+1}.** {title}..."):
                st.write(f"🏢 {job.get('employer_name', 'N/A')}")
                st.write(f"📍 {job.get('job_city', '')} {job.get('job_state', '')}")
                score = job.get('career_compass_match_score', 0)
                if score >= 0.7: st.write("🟢 Excellent Match")
                elif score >= 0.4: st.write("🟡 Good Match")
                else: st.write("⚪ Potential Fit")
                
                if st.button(f"🗑️ Remove", key=f"remove_job_{i}"):
                    st.session_state.saved_jobs.pop(i)
                    st.rerun()
        
        st.divider()
        
        st.subheader("📤 Export Jobs")
        st.markdown("Download your saved jobs to Excel")
        
        export_data = []
        for job in st.session_state.saved_jobs:
            export_data.append({
                "Title": job.get("job_title", ""),
                "Company": job.get("employer_name", ""),
                "Location": f"{job.get('job_city', '')} {job.get('job_state', '')}".strip(),
                "Match Score": f"{job.get('career_compass_match_score', 0) * 100:.0f}%",
                "Skills": ", ".join(job.get("job_required_skills", [])[:5]),
                "Apply Link": job.get("job_apply_link", "#")
            })
        
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download as Excel/CSV",
            data=csv,
            file_name="my_saved_jobs.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        if st.button("🗑️ Clear All Saved", key="clear_all_btn", type="secondary", use_container_width=True):
            st.session_state.saved_jobs = []
            st.rerun()
            
    else:
        st.info("No saved jobs yet. Click 'Save' on jobs you like!")

# ALL 5 TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 CV Upload", "🔍 Analysis", "💼 Jobs", "✍️ CV Rewrite", "📧 Cover Letter"])

# TAB 1: CV UPLOAD
with tab1:
    st.header("Upload Your CV")
    st.markdown("Upload your CV to get started with AI-powered career tools")
    
    uploaded = st.file_uploader("Choose a file", type=["txt", "pdf"], key="cv_uploader_main")
    if uploaded:
        try:
            if uploaded.type == "text/plain":
                st.session_state.cv_text = uploaded.read().decode("utf-8")
                st.success("✅ CV Uploaded!")
                with st.expander("📋 Preview"):
                    st.text_area("CV Content", st.session_state.cv_text, height=200)
            else:
                st.warning("Please upload a .txt file for this demo.")
        except Exception as e:
            st.error(f"Error: {e}")

# TAB 2: ANALYSIS
with tab2:
    st.header("AI Profile Analysis")
    st.markdown("Get AI-powered insights about your CV")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV in the first tab.")
    elif st.button("🎯 Analyze My Profile", key="btn_analyze_main", type="primary", use_container_width=True):
        with st.spinner("🤖 Analyzing your CV..."):
            try:
                from groq import Groq
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prompt = f"""
                You are an expert career coach. Analyze this CV and provide:
                1. Target Roles (3-4 suitable job titles)
                2. Key Skills (technical and soft skills)
                3. Top Strengths
                4. Areas for Improvement
                
                CV: {st.session_state.cv_text[:2000]}
                """
                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.success("✅ Analysis Complete!")
                st.markdown(resp.choices[0].message.content)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

# TAB 3: JOBS
with tab3:
    st.header("AI-Powered Job Matching")
    st.markdown("Find jobs that match your skills and experience")
    
    if JSearchClient is None:
        st.error("Job matching module not loaded")
    else:
        if st.button("🔍 Search Jobs", key="btn_search_main", type="primary"):
            try:
                client = JSearchClient(api_key=st.secrets.get("JSEARCH_API_KEY", "demo-key"))
                results = client.search_jobs(
                    query="software developer", 
                    num_pages=1,
                    user_skills=["Python", "JavaScript", "AWS"]
                )
                
                st.session_state.search_results = results.get("data", [])
                st.success(f"Found {len(st.session_state.search_results)} jobs!")
            except Exception as e:
                st.error(f"Error: {e}")
        
        if st.session_state.search_results:
            st.markdown("---")
            for idx, job in enumerate(st.session_state.search_results):
                title = str(job.get("job_title", "Job"))
                company = str(job.get("employer_name", "Company"))
                city = str(job.get("job_city", ""))
                desc = str(job.get("job_description", ""))[:200]
                skills = job.get("job_required_skills", [])
                apply_url = str(job.get("job_apply_link", "#"))
                score = float(job.get("career_compass_match_score", 0))
                salary = job.get("normalized_salary", {})
                
                if score >= 0.7: badge = "🟢 Excellent"
                elif score >= 0.4: badge = "🟡 Good"
                else: badge = "⚪ Match"
                
                is_saved = any(
                    str(s.get("job_title")) == title and str(s.get("employer_name")) == company
                    for s in st.session_state.saved_jobs
                )
                
                st.markdown(f"""
                <div class="job-card">
                    <div style="font-size:24px; font-weight:bold;">{title}</div>
                    <div>🏢 {company} | 📍 {city}</div>
                    <div style="margin-top:10px;"><span class="badge">{badge}</span></div>
                </div>
                """, unsafe_allow_html=True)
                
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
                            st.session_state.saved_jobs = [
                                j for j in st.session_state.saved_jobs
                                if not (str(j.get("job_title")) == title and str(j.get("employer_name")) == company)
                            ]
                        else:
                            st.session_state.saved_jobs.append(job.copy())
                        st.rerun()
                
                with st.expander("📋 View Full Job Details"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**📝 Full Description**")
                        st.write(desc if desc else "No description available")
                    
                    with col_b:
                        if skills:
                            st.markdown("**💡 Required Skills**")
                            skills_str = ", ".join(str(s) for s in skills)
                            st.write(skills_str)
                        
                        if salary and salary.get("min_annual_usd"):
                            st.markdown("**💰 Salary Range**")
                            min_sal = salary.get("min_annual_usd", 0)
                            max_sal = salary.get("max_annual_usd", 0)
                            st.info(f"${min_sal:,} - ${max_sal:,} / year")
                    
                    if apply_url and apply_url != "#":
                        st.markdown(f"""
                        <div style="text-align: center; margin-top: 20px;">
                            <a href="{apply_url}" target="_blank" 
                               style="background-color: #667eea; color: white; 
                                      padding: 12px 30px; border-radius: 5px; 
                                      text-decoration: none; font-weight: bold;
                                      display: inline-block;">
                                🚀 Apply Now
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")

# TAB 4: CV REWRITE
with tab4:
    st.header("✍️ AI CV Rewriting")
    st.markdown("Optimize your CV for specific job descriptions")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        rewrite_option = st.radio(
            "Choose how to provide job description:",
            ["📋 Select from my saved jobs", "✍️ Paste job description manually"],
            key="rewrite_option_select"
        )
        
        job_desc = ""
        
        if rewrite_option == "📋 Select from my saved jobs":
            if st.session_state.saved_jobs:
                job_options = [f"{job.get('job_title', 'Job')} at {job.get('employer_name', 'Company')}" 
                              for job in st.session_state.saved_jobs]
                selected_job = st.selectbox(
                    "Select a job to optimize your CV for:",
                    job_options,
                    key="saved_job_selector"
                )
                
                selected_idx = job_options.index(selected_job)
                selected_job_data = st.session_state.saved_jobs[selected_idx]
                job_desc = selected_job_data.get("job_description", "")
                
                if job_desc:
                    st.info(f"📄 Using job description from **{selected_job}**")
                    with st.expander("👀 Preview job description"):
                        st.write(job_desc[:500] + "..." if len(job_desc) > 500 else job_desc)
            else:
                st.warning("You haven't saved any jobs yet.")
                job_desc = st.text_area("Or paste the job description here:", height=150, key="cv_rewrite_manual")
        else:
            job_desc = st.text_area("Paste the Job Description", height=150, placeholder="Paste job description...", key="cv_rewrite_job_desc")
        
        if st.button("✨ Rewrite My CV", key="btn_rewrite_cv", type="primary", use_container_width=True):
            if not job_desc:
                st.warning("Please enter or select a job description")
            else:
                with st.spinner("🤖 Optimizing your CV..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        prompt = f"""
                        Optimize this CV for the following job description.
                        Highlight relevant skills and experience.
                        
                        CV: {st.session_state.cv_text[:2000]}
                        Job Description: {job_desc[:1000]}
                        """
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=1000
                        )
                        
                        st.success("✅ CV Optimized!")
                        st.text_area("Optimized CV", response.choices[0].message.content, height=400, key="cv_rewrite_output")
                        
                        st.download_button(
                            "📥 Download Optimized CV",
                            data=response.choices[0].message.content,
                            file_name="optimized_cv.txt",
                            mime="text/plain",
                            key="download_optimized_cv"
                        )
                    except Exception as e:
                        st.error(f"Rewriting failed: {e}")

# TAB 5: COVER LETTER
with tab5:
    st.header("📧 AI Cover Letter Generator")
    st.markdown("Generate personalized cover letters in seconds")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        cl_option = st.radio(
            "Choose how to provide job details:",
            ["📋 Select from my saved jobs", "✍️ Enter job details manually"],
            key="cover_letter_option_select"
        )
        
        company_name = ""
        job_title = ""
        job_desc = ""
        
        if cl_option == "📋 Select from my saved jobs":
            if st.session_state.saved_jobs:
                job_options = [f"{job.get('job_title', 'Job')} at {job.get('employer_name', 'Company')}" 
                              for job in st.session_state.saved_jobs]
                selected_job = st.selectbox(
                    "Select a job to generate cover letter for:",
                    job_options,
                    key="saved_job_selector_cover_letter"
                )
                
                selected_idx = job_options.index(selected_job)
                selected_job_data = st.session_state.saved_jobs[selected_idx]
                
                company_name = selected_job_data.get("employer_name", "")
                job_title = selected_job_data.get("job_title", "")
                job_desc = selected_job_data.get("job_description", "")
                
                st.info(f"📄 Using details from **{selected_job}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Company", value=company_name, disabled=True, key="cl_company_disabled")
                with col2:
                    st.text_input("Job Title", value=job_title, disabled=True, key="cl_title_disabled")
                
                if job_desc:
                    with st.expander("👀 Preview job description"):
                        st.write(job_desc[:500] + "..." if len(job_desc) > 500 else job_desc)
            else:
                st.warning("You haven't saved any jobs yet.")
                col1, col2 = st.columns(2)
                with col1:
                    company_name = st.text_input("🏢 Company Name", placeholder="Google", key="cl_company_manual")
                with col2:
                    job_title = st.text_input("💼 Job Title", placeholder="Software Engineer", key="cl_title_manual")
                job_desc = st.text_area("📝 Job Description", height=150, key="cl_desc_manual")
        else:
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("🏢 Company Name", placeholder="Google", key="cl_company_manual2")
            with col2:
                job_title = st.text_input("💼 Job Title", placeholder="Software Engineer", key="cl_title_manual2")
            job_desc = st.text_area("📝 Job Description", height=150, key="cl_desc_manual2")
        
        if st.button("✍️ Generate Cover Letter", key="btn_generate_cover_letter", type="primary", use_container_width=True):
            if not company_name or not job_title:
                st.warning("Please fill in company name and job title")
            else:
                with st.spinner("🤖 Writing your cover letter..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        prompt = f"""
                        Write a professional cover letter:
                        CV: {st.session_state.cv_text[:1500]}
                        Company: {company_name}
                        Position: {job_title}
                        Job Details: {job_desc[:500] if job_desc else "Not provided"}
                        
                        Make it professional, 300-400 words.
                        """
                        
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=600
                        )
                        
                        st.success("✅ Cover Letter Generated!")
                        st.text_area("Your Cover Letter", response.choices[0].message.content, height=400, key="cover_letter_output")
                        
                        st.download_button(
                            "📥 Download Cover Letter",
                            data=response.choices[0].message.content,
                            file_name="cover_letter.txt",
                            mime="text/plain",
                            key="download_cover_letter"
                        )
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

st.markdown("---")
st.caption("Made with ❤️ using AI")