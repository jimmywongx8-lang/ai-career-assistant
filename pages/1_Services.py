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

# DEFINE ALL TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 CV Upload", "🔍 Analysis", "💼 Jobs", "✍️ CV Rewrite", "📧 Cover Letter"])

# TAB 1: CV UPLOAD
with tab1:
    st.header("Upload Your CV")
    st.markdown("Upload your CV to get started with AI-powered career tools")
    
    uploaded = st.file_uploader("Choose a file", type=["txt", "pdf"], key="cv_uploader_main")
    if uploaded:
        try:
            if uploaded.type == "application/pdf":
                import PyPDF2
                from io import BytesIO
                pdf_file = BytesIO(uploaded.read())
                reader = PyPDF2.PdfReader(pdf_file)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
                st.session_state.cv_text = text_content
                st.success(f"✅ PDF Uploaded ({len(uploaded.getvalue()) / 1024:.1f} KB)")
                with st.expander("📋 Preview"):
                    st.text_area("CV Content", text_content[:1000], height=200)
            elif uploaded.type == "text/plain":
                st.session_state.cv_text = uploaded.read().decode("utf-8")
                st.success("✅ Text File Uploaded!")
                with st.expander("📋 Preview"):
                    st.text_area("CV Content", st.session_state.cv_text[:1000], height=200)
            else:
                st.warning("Please use .txt or .pdf")
        except Exception as e:
            st.error(f"Error: {e}")

# TAB 2: ANALYSIS
with tab2:
    st.header("AI Profile Analysis")
    if not st.session_state.cv_text:
        st.warning("⚠️ Upload CV first")
    elif st.button("🎯 Analyze", key="btn_analyze", type="primary", use_container_width=True):
        with st.spinner("🤖 Analyzing..."):
            try:
                from groq import Groq
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                prompt = f"Analyze CV: {st.session_state.cv_text[:2000]}"
                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.success("✅ Analysis Complete!")
                st.markdown(resp.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")

# TAB 3: JOBS - SMART SEARCH
with tab3:
    st.header("AI-Powered Job Matching")
    st.markdown("Find jobs matching your background")
    
    if JSearchClient is None:
        st.error("Module not loaded")
    else:
        # Input fields for job search
        st.markdown("**🎯 Target Role**")
        col1, col2 = st.columns([3, 1])
        with col1:
            target_role = st.text_input(
                "Job Title",
                placeholder="e.g., Strategy Consultant, Business Analyst",
                help="Enter your target role",
                key="target_role_input"
            )
        with col2:
            search_location = st.text_input("Location", placeholder="Remote", key="search_location_input")
        
        # Smart skill detection from CV
        detected_skills = []
        if st.session_state.cv_text:
            cv_lower = st.session_state.cv_text.lower()
            strategy_keywords = ["strategy", "consulting", "analysis", "management", "finance", "operations", "marketing"]
            for kw in strategy_keywords:
                if kw in cv_lower:
                    detected_skills.append(kw.title())
            
            tech_skills = ["Python", "SQL", "Excel", "Tableau", "PowerBI"]
            for skill in tech_skills:
                if skill.lower() in cv_lower:
                    detected_skills.append(skill)
            
            if detected_skills:
                st.info(f"💡 Detected: {', '.join(detected_skills[:6])}")
        
        if st.button("🔍 Search Jobs", key="btn_search_main", type="primary"):
            search_query = target_role.strip() if target_role else "consultant"
            search_skills = detected_skills if detected_skills else ["Strategy", "Analysis"]
            
            try:
                client = JSearchClient(api_key=st.secrets.get("JSEARCH_API_KEY", "demo-key"))
                results = client.search_jobs(
                    query=search_query,
                    location=search_location if search_location else None,
                    num_pages=1,
                    user_skills=search_skills
                )
                
                st.session_state.search_results = results.get("data", [])
                st.success(f"Found {len(st.session_state.search_results)} jobs for **{search_query}**!")
            except Exception as e:
                st.error(f"Error: {e}")
        
        # Display jobs
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
                    st.success("💾 Saved") if is_saved else st.info("Click Save")
                with col2:
                    key = f"save_{idx}_{hashlib.md5(f'{title}{company}'.encode()).hexdigest()}"
                    if st.button("💾 Save", key=key):
                        if is_saved:
                            st.session_state.saved_jobs = [j for j in st.session_state.saved_jobs 
                                                           if not (str(j.get("job_title")) == title and str(j.get("employer_name")) == company)]
                        else:
                            st.session_state.saved_jobs.append(job.copy())
                        st.rerun()
                
                with st.expander("📋 View Details"):
                    st.write(f"**Description:** {desc}")
                    if skills:
                        st.write(f"**Skills:** {', '.join(str(s) for s in skills[:5])}")
                    if apply_url != "#":
                        st.markdown(f"[🚀 Apply]({apply_url})")
                st.markdown("---")

# TAB 4: CV REWRITE
with tab4:
    st.header("✍️ AI CV Rewriting")
    if not st.session_state.cv_text:
        st.warning("⚠️ Upload CV first")
    else:
        option = st.radio("Choose option:", ["📋 Select saved job", "✍️ Paste manually"], key="rewrite_option")
        job_desc = ""
        
        if option == "📋 Select saved job" and st.session_state.saved_jobs:
            job_options = [f"{j.get('job_title')} at {j.get('employer_name')}" for j in st.session_state.saved_jobs]
            selected = st.selectbox("Select job:", job_options, key="job_selector_rewrite")
            idx = job_options.index(selected)
            job_desc = st.session_state.saved_jobs[idx].get("job_description", "")
            st.info(f"Using: {selected}")
        else:
            job_desc = st.text_area("Paste job description:", height=150, key="job_desc_manual")
        
        if st.button("✨ Rewrite CV", key="btn_rewrite", type="primary", use_container_width=True):
            if job_desc:
                with st.spinner("🤖 Optimizing..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        prompt = f"Optimize CV for: {job_desc[:1000]}\nCV: {st.session_state.cv_text[:2000]}"
                        resp = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=1000
                        )
                        st.success("✅ Done!")
                        st.text_area("Optimized CV", resp.choices[0].message.content, height=400)
                        st.download_button("📥 Download", resp.choices[0].message.content, "optimized_cv.txt")
                    except Exception as e:
                        st.error(f"Error: {e}")

# TAB 5: COVER LETTER
with tab5:
    st.header("📧 Cover Letter Generator")
    if not st.session_state.cv_text:
        st.warning("⚠️ Upload CV first")
    else:
        option = st.radio("Choose option:", ["📋 Select saved job", "✍️ Enter manually"], key="cl_option")
        company = ""
        title = ""
        job_desc = ""
        
        if option == "📋 Select saved job" and st.session_state.saved_jobs:
            job_options = [f"{j.get('job_title')} at {j.get('employer_name')}" for j in st.session_state.saved_jobs]
            selected = st.selectbox("Select job:", job_options, key="job_selector_cl")
            idx = job_options.index(selected)
            job = st.session_state.saved_jobs[idx]
            company = job.get("employer_name", "")
            title = job.get("job_title", "")
            job_desc = job.get("job_description", "")
            st.info(f"Using: {company} - {title}")
        else:
            c1, c2 = st.columns(2)
            with c1: company = st.text_input("Company", key="cl_company")
            with c2: title = st.text_input("Job Title", key="cl_title")
            job_desc = st.text_area("Job Description", height=150, key="cl_desc")
        
        if st.button("✍️ Generate", key="btn_cl", type="primary", use_container_width=True):
            if company and title:
                with st.spinner("🤖 Writing..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        prompt = f"Cover letter for {company} - {title}.\nCV: {st.session_state.cv_text[:1500]}\nJob: {job_desc[:500]}"
                        resp = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=600
                        )
                        st.success("✅ Done!")
                        st.text_area("Cover Letter", resp.choices[0].message.content, height=400)
                        st.download_button("📥 Download", resp.choices[0].message.content, "cover_letter.txt")
                    except Exception as e:
                        st.error(f"Error: {e}")

st.caption("Made with ❤️ using AI")