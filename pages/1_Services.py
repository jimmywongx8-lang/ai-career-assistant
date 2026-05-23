import streamlit as st
import sys
from pathlib import Path
import json
import hashlib
import pandas as pd

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

# Sidebar for Saved Jobs & Export
with st.sidebar:
    st.header("💼 Saved Jobs")
    
    if st.session_state.saved_jobs:
        st.success(f"✅ {len(st.session_state.saved_jobs)} jobs saved")
        
        # List saved jobs
        for i, job in enumerate(st.session_state.saved_jobs):
            title = job.get('job_title', 'Unknown')[:35]
            with st.expander(f"**{i+1}.** {title}..."):
                st.write(f"🏢 {job.get('employer_name', 'N/A')}")
                st.write(f"📍 {job.get('job_city', '')} {job.get('job_state', '')}")
                score = job.get('career_compass_match_score', 0)
                if score >= 0.7: st.write("🟢 Excellent Match")
                elif score >= 0.4: st.write("🟡 Good Match")
                else: st.write("⚪ Potential Fit")
                
                # Remove individual job
                if st.button(f"🗑️ Remove", key=f"remove_job_{i}"):
                    st.session_state.saved_jobs.pop(i)
                    st.rerun()
        
        st.divider()
        
        # EXPORT SECTION
        st.subheader("📤 Export Jobs")
        st.markdown("Download your saved jobs to Excel")
        
        # Prepare data for export
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
        
        # Create CSV
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download as Excel/CSV",
            data=csv,
            file_name="my_saved_jobs.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Clear All
        if st.button("🗑️ Clear All Saved", use_container_width=True, key="clear_all_btn", type="secondary"):
            st.session_state.saved_jobs = []
            st.rerun()
            
    else:
        st.info("No saved jobs yet. Click 'Save' on jobs you like!")

# Main Tabs - ALL 5 TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 CV Upload", "🔍 Analysis", "💼 Jobs", "✍️ CV Rewrite", "📧 Cover Letter"])

# ==================== TAB 1: CV UPLOAD ====================
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

# ==================== TAB 2: AI ANALYSIS ====================
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

# ==================== TAB 3: JOB MATCHING ====================
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
                
                st.write(f"**Description:** {desc}...")
                if skills:
                    st.write(f"**Skills:** {', '.join(str(s) for s in skills[:5])}")
                if apply_url != "#":
                    st.markdown(f"[🚀 Apply]({apply_url})")
                
                st.markdown("---")

# ==================== TAB 4: CV REWRITING ====================
with tab4:
    st.header("✍️ AI CV Rewriting")
    st.markdown("Optimize your CV for specific job descriptions")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        job_desc = st.text_area(
            "Paste the Job Description",
            height=150,
            placeholder="Paste the job description you want to optimize your CV for...",
            key="cv_rewrite_job_desc"
        )
        
        if st.button("✨ Rewrite My CV", key="btn_rewrite_cv", type="primary", use_container_width=True):
            if not job_desc:
                st.warning("Please enter a job description")
            else:
                with st.spinner("🤖 Optimizing your CV..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        prompt = f"""
                        Optimize this CV for the following job description.
                        Highlight relevant skills and experience.
                        Keep it professional and concise.
                        
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

# ==================== TAB 5: COVER LETTER ====================
with tab5:
    st.header("📧 AI Cover Letter Generator")
    st.markdown("Generate personalized cover letters in seconds")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input(
                "🏢 Company Name",
                placeholder="e.g., Google, Microsoft",
                key="cover_letter_company"
            )
        with col2:
            job_title = st.text_input(
                "💼 Job Title",
                placeholder="e.g., Software Engineer",
                key="cover_letter_title"
            )
        
        job_desc = st.text_area(
            "📝 Job Description (Optional)",
            height=150,
            placeholder="Paste the job description for a more targeted cover letter...",
            key="cover_letter_desc"
        )
        
        if st.button("✍️ Generate Cover Letter", key="btn_generate_cover_letter", type="primary", use_container_width=True):
            if not company_name or not job_title:
                st.warning("Please fill in company name and job title")
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
                        Use a friendly but professional tone.
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