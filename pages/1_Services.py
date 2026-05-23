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

# Initialize with JSON-safe defaults
if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""

with st.sidebar:
    st.header("💼 Saved Jobs")
    if st.session_state.saved_jobs:
        st.write(f"✅ {len(st.session_state.saved_jobs)} saved")
        for i, job in enumerate(st.session_state.saved_jobs):
            title = str(job.get('job_title', 'Job'))[:35]
            with st.expander(f"**{i+1}.** {title}..."):
                st.write(f"🏢 {job.get('employer_name', 'N/A')}")
                if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                    st.session_state.saved_jobs.pop(i)
                    st.rerun()
        
        st.divider()
        # Export
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
        st.download_button("📥 Download CSV", data=csv, file_name="jobs.csv", mime="text/csv", use_container_width=True)
        
        if st.button("🗑️ Clear All", key="clear_all", use_container_width=True):
            st.session_state.saved_jobs = []
            st.rerun()
    else:
        st.write("No saved jobs")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 CV Upload", "🔍 Analysis", "💼 Jobs", "✍️ CV Rewrite", "📧 Cover Letter"])

with tab1:
    st.header("Upload CV")
    uploaded = st.file_uploader("Choose file", type=["txt", "pdf"], key="cv_up")
    if uploaded:
        try:
            if uploaded.type == "application/pdf":
                import PyPDF2
                from io import BytesIO
                reader = PyPDF2.PdfReader(BytesIO(uploaded.read()))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                st.session_state.cv_text = text
                st.write("✅ PDF uploaded")
            else:
                st.session_state.cv_text = uploaded.read().decode("utf-8")
                st.write("✅ Text uploaded")
        except Exception as e:
            st.write(f"Error: {e}")

with tab2:
    st.header("AI Analysis")
    if not st.session_state.cv_text:
        st.write("Upload CV first")
    elif st.button("🎯 Analyze", key="btn_analyze", type="primary", use_container_width=True):
        try:
            from groq import Groq
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": f"Analyze: {st.session_state.cv_text[:2000]}"}]
            )
            st.write(resp.choices[0].message.content)
        except Exception as e:
            st.write(f"Error: {e}")

with tab3:
    st.header("Job Matching")
    
    if JSearchClient is None:
        st.write("Module not loaded")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            target_role = st.text_input("Target Role", placeholder="e.g., Strategy Consultant", key="target_role")
        with col2:
            location = st.text_input("Location", placeholder="Remote", key="location")
        
        # Detect skills
        detected = []
        if st.session_state.cv_text:
            cv_lower = st.session_state.cv_text.lower()
            for kw in ["strategy", "consulting", "analysis", "management", "finance"]:
                if kw in cv_lower:
                    detected.append(kw.title())
            if detected:
                st.write(f"💡 Detected: {', '.join(detected)}")
        
        if st.button("🔍 Search", key="btn_search", type="primary"):
            query = target_role.strip() if target_role else "consultant"
            try:
                client = JSearchClient(api_key=st.secrets.get("JSEARCH_API_KEY", ""))
                results = client.search_jobs(query=query, location=location if location else None, user_skills=detected)
                
                # CRITICAL: JSON serialize/deserialize to strip ALL Streamlit objects
                jobs_data = results.get("data", [])
                jobs_json = json.dumps(jobs_data, default=str)
                clean_results = json.loads(jobs_json)
                
                st.session_state.search_results = clean_results
                st.write(f"✅ Found {len(clean_results)} jobs!")
            except Exception as e:
                st.write(f"Error: {e}")
        
        if st.session_state.search_results:
            st.write("---")
            for idx, job in enumerate(st.session_state.search_results):
                # Ensure all values are plain strings
                title = str(job.get("job_title", "Job"))
                company = str(job.get("employer_name", "Company"))
                city = str(job.get("job_city", ""))
                desc = str(job.get("job_description", ""))[:200]
                skills = job.get("job_required_skills", [])
                if isinstance(skills, list):
                    skills = [str(s) for s in skills]
                else:
                    skills = []
                apply_url = str(job.get("job_apply_link", "#"))
                score = float(job.get("career_compass_match_score", 0))
                
                badge = "🟢 Excellent" if score >= 0.7 else "🟡 Good" if score >= 0.4 else "⚪ Match"
                
                is_saved = any(str(s.get("job_title")) == title and str(s.get("employer_name")) == company 
                              for s in st.session_state.saved_jobs)
                
                st.markdown(f"""
                <div class="job-card">
                    <div style="font-size:24px; font-weight:bold;">{title}</div>
                    <div>🏢 {company} | 📍 {city}</div>
                    <div style="margin-top:10px;"><span class="badge">{badge}</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([4, 1])
                with c1:
                    if is_saved:
                        st.write("💾 Saved")
                    else:
                        st.write("Click Save")
                with c2:
                    key = f"save_{idx}_{hashlib.md5(f'{title}{company}'.encode()).hexdigest()}"
                    if st.button("💾 Save", key=key):
                        if is_saved:
                            st.session_state.saved_jobs = [j for j in st.session_state.saved_jobs 
                                                           if not (str(j.get("job_title")) == title and str(j.get("employer_name")) == company)]
                        else:
                            # Create plain dict
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
                
                # FIXED: View Details with Apply Button
                with st.expander("📋 View Full Job Details"):
                    # Full description
                    st.markdown("**📝 Job Description**")
                    full_desc = str(job.get("job_description", "No description available"))
                    st.write(full_desc)
                    
                    # Skills
                    if skills and len(skills) > 0:
                        st.markdown("**💡 Required Skills**")
                        skills_text = ", ".join(skills)
                        st.write(skills_text)
                    
                    # Salary
                    salary_info = job.get("normalized_salary", {})
                    if salary_info and isinstance(salary_info, dict):
                        min_sal = salary_info.get("min_annual_usd", 0)
                        max_sal = salary_info.get("max_annual_usd", 0)
                        if min_sal and max_sal:
                            st.markdown("**💰 Salary Range**")
                            st.write(f"${min_sal:,} - ${max_sal:,} per year")
                    
                    # Apply button
                    if apply_url and apply_url != "#" and apply_url != "None":
                        st.markdown("---")
                        st.markdown(f"""
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="{apply_url}" target="_blank" 
                               style="background-color: #10b981; color: white; 
                                      padding: 12px 30px; border-radius: 5px; 
                                      text-decoration: none; font-weight: bold;
                                      display: inline-block;">
                                🚀 Apply Now
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.write("---")

with tab4:
    st.header("CV Rewrite")
    if not st.session_state.cv_text:
        st.write("Upload CV first")
    else:
        opt = st.radio("Option:", ["Select saved job", "Paste manually"], key="rewrite_opt")
        job_desc = ""
        if opt == "Select saved job" and st.session_state.saved_jobs:
            opts = [f"{j.get('job_title')} at {j.get('employer_name')}" for j in st.session_state.saved_jobs]
            sel = st.selectbox("Select:", opts, key="rewrite_sel")
            idx = opts.index(sel)
            job_desc = st.session_state.saved_jobs[idx].get("job_description", "")
            st.write(f"Using: {sel}")
        else:
            job_desc = st.text_area("Paste description:", height=150, key="rewrite_desc")
        
        if st.button("✨ Rewrite", key="btn_rewrite", type="primary", use_container_width=True):
            if job_desc:
                try:
                    from groq import Groq
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    prompt = f"Optimize CV: {st.session_state.cv_text[:2000]}\nFor: {job_desc[:1000]}"
                    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], max_tokens=1000)
                    st.write("✅ Done!")
                    st.text_area("Optimized CV", resp.choices[0].message.content, height=400)
                    st.download_button("📥 Download", resp.choices[0].message.content, "cv.txt")
                except Exception as e:
                    st.write(f"Error: {e}")

with tab5:
    st.header("Cover Letter")
    if not st.session_state.cv_text:
        st.write("Upload CV first")
    else:
        opt = st.radio("Option:", ["Select saved job", "Enter manually"], key="cl_opt")
        company = ""
        title = ""
        job_desc = ""
        
        if opt == "Select saved job" and st.session_state.saved_jobs:
            opts = [f"{j.get('job_title')} at {j.get('employer_name')}" for j in st.session_state.saved_jobs]
            sel = st.selectbox("Select:", opts, key="cl_sel")
            idx = opts.index(sel)
            job = st.session_state.saved_jobs[idx]
            company = str(job.get("employer_name", ""))
            title = str(job.get("job_title", ""))
            job_desc = job.get("job_description", "")
            st.write(f"Using: {company} - {title}")
        else:
            c1, c2 = st.columns(2)
            with c1: company = st.text_input("Company", key="cl_comp")
            with c2: title = st.text_input("Title", key="cl_title")
            job_desc = st.text_area("Description", height=150, key="cl_desc")
        
        if st.button("✍️ Generate", key="btn_cl", type="primary", use_container_width=True):
            if company and title:
                try:
                    from groq import Groq
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    prompt = f"Cover letter for {company} - {title}.\nCV: {st.session_state.cv_text[:1500]}\nJob: {job_desc[:500]}"
                    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], max_tokens=600)
                    st.write("✅ Done!")
                    st.text_area("Cover Letter", resp.choices[0].message.content, height=400)
                    st.download_button("📥 Download", resp.choices[0].message.content, "cl.txt")
                except Exception as e:
                    st.write(f"Error: {e}")

st.write("Made with ❤️")