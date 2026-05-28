import streamlit as st
import sys
from pathlib import Path
import json
import hashlib
import pandas as pd
import time

sys.path.append(str(Path(__file__).parent.parent))

try:
    from modules.jsearch_client import JSearchClient
except ImportError:
    JSearchClient = None

st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="wide")

# ==========================================
# CLEAN, PROFESSIONAL THEME
# ==========================================
st.markdown("""
<style>
    /* Import Professional Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Clean Color Palette */
    :root {
        --primary: #2563EB;
        --primary-hover: #1D4ED8;
        --secondary: #7C3AED;
        --success: #059669;
        --warning: #D97706;
        --error: #DC2626;
        --text-primary: #111827;
        --text-secondary: #6B7280;
        --bg-primary: #FFFFFF;
        --bg-secondary: #F9FAFB;
        --bg-tertiary: #F3F4F6;
        --border: #E5E7EB;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Global Styles - Clean White Background */
    body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #F9FAFB;
        color: var(--text-primary);
        font-size: 15px;
        line-height: 1.6;
    }
    
    /* Main Container */
    .main .block-container {
        padding: 2.5rem 3rem 3rem 3rem;
        max-width: 1200px;
        background-color: white;
        border-radius: 0;
    }
    
    /* Typography - Clean & Readable */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        line-height: 1.3;
        letter-spacing: -0.01em;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    
    h1 { font-size: 2.5rem; }
    h2 { font-size: 2rem; }
    h3 { font-size: 1.5rem; }
    
    /* Hero Section - Clean & Professional */
    .hero-section {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
        padding: 3rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2.5rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
    }
    
    .hero-title {
        font-size: 2.75rem;
        font-weight: 700;
        margin: 0 0 0.75rem 0;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.125rem;
        font-weight: 400;
        color: var(--text-secondary);
        max-width: 650px;
        line-height: 1.6;
    }
    
    .hero-badges {
        display: flex;
        gap: 0.75rem;
        margin-top: 1.5rem;
        flex-wrap: wrap;
    }
    
    .hero-badge {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        padding: 0.625rem 1.25rem;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.875rem;
        color: var(--text-primary);
    }
    
    /* Cards - Clean White */
    .job-card, .info-box, .steps-box {
        background: white;
        border-radius: 12px;
        padding: 1.75rem;
        margin-bottom: 1.25rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .job-card:hover {
        box-shadow: var(--shadow-md);
        border-color: #D1D5DB;
    }
    
    .job-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        border-radius: 12px 12px 0 0;
    }
    
    /* Buttons - Professional Blue */
    .stButton button {
        background: var(--primary);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.625rem 1.5rem;
        font-weight: 500;
        font-size: 0.9375rem;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .stButton button:hover {
        background: var(--primary-hover);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    /* Tabs - Clean */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: transparent;
        border-bottom: 2px solid var(--border);
        padding-bottom: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        padding: 0 20px !important;
        background: transparent;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        font-size: 0.9375rem;
        color: var(--text-secondary);
        transition: all 0.2s ease;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-secondary);
        color: var(--text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: var(--primary) !important;
        font-weight: 600;
        border-bottom: 2px solid white;
        margin-bottom: -2px;
    }
    
    /* Sidebar - Clean White */
    .css-1d391kg {
        background: white;
        border-right: 1px solid var(--border);
    }
    
    /* Metrics - Subtle */
    .metric-card {
        background: var(--bg-secondary);
        border-radius: 8px;
        padding: 1.25rem;
        border: 1px solid var(--border);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    /* Input Fields - Clean */
    .stTextInput > div > div,
    .stTextArea > div > div,
    .stSelectbox > div > div {
        border: 1px solid var(--border);
        border-radius: 8px;
        background: white;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div:focus-within,
    .stTextArea > div > div:focus-within,
    .stSelectbox > div > div:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* Badges - Professional */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.375rem 0.875rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .badge-excellent {
        background: #D1FAE5;
        color: #065F46;
    }
    
    .badge-good {
        background: #FEF3C7;
        color: #92400E;
    }
    
    .badge-match {
        background: var(--bg-tertiary);
        color: var(--text-secondary);
    }
    
    /* Info Boxes - Subtle Colors */
    .info-box {
        background: #EFF6FF;
        border-left: 4px solid var(--primary);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .info-box-title {
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 0.75rem;
        font-size: 1rem;
    }
    
    .info-box-text {
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    .steps-box {
        background: #F0FDF4;
        border-left: 4px solid var(--success);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .steps-box-title {
        font-weight: 600;
        color: var(--success);
        margin-bottom: 0.75rem;
        font-size: 1rem;
    }
    
    /* Footer - Clean */
    .footer {
        background: white;
        padding: 3rem 0 2rem 0;
        margin-top: 4rem;
        border-top: 1px solid var(--border);
    }
    
    .footer-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 3rem;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .footer-col h4 {
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    
    .footer-col ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .footer-col li {
        margin-bottom: 0.625rem;
        color: var(--text-secondary);
        font-size: 0.875rem;
    }
    
    .footer-bottom {
        text-align: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border);
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
        color: var(--text-secondary);
        font-size: 0.875rem;
    }
    
    /* Mobile */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem; }
        .hero-section { padding: 2rem 1.5rem; }
        .main .block-container { padding: 1.5rem 1rem; }
        .footer-grid { grid-template-columns: 1fr; gap: 2rem; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "search_count" not in st.session_state:
    st.session_state.search_count = 0

# ==========================================
# CLEAN HERO SECTION
# ==========================================
st.markdown("""
<div class="hero-section">
    <div>
        <h1 class="hero-title">🧭 Career Compass</h1>
        <p class="hero-subtitle">AI-powered career tools to help you find jobs, optimize your CV, and generate professional cover letters. 100% free, no signup required.</p>
        <div class="hero-badges">
            <div class="hero-badge">✨ AI-Powered</div>
            <div class="hero-badge">🔒 Privacy-First</div>
            <div class="hero-badge">⚡ Instant Results</div>
            <div class="hero-badge">💯 Free Forever</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    # Session Metrics
    st.markdown("### 📊 Your Session")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.saved_jobs)}</div>
            <div class="metric-label">Jobs Saved</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.search_count}</div>
            <div class="metric-label">Searches</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 💼 Saved Jobs")
    if st.session_state.saved_jobs:
        st.success(f"✅ {len(st.session_state.saved_jobs)} jobs saved")
        
        for i, job in enumerate(st.session_state.saved_jobs):
            title = str(job.get('job_title', 'Job'))[:35]
            with st.expander(f"**{i+1}.** {title}...", expanded=False):
                st.markdown(f'🏢 **{job.get("employer_name", "N/A")}**')
                if st.button(f"🗑️ Remove", key=f"remove_{i}", use_container_width=True):
                    st.session_state.saved_jobs.pop(i)
                    st.rerun()
        
        st.divider()
        st.markdown("### 📤 Export Jobs")
        st.markdown("Download your saved jobs to track applications")
        
        export_data = []
        for job in st.session_state.saved_jobs:
            export_data.append({
                "Title": job.get("job_title", ""),
                "Company": job.get("employer_name", ""),
                "Location": f"{job.get('job_city', '')} {job.get('job_state', '')}".strip(),
                "Match Score": f"{job.get('career_compass_match_score', 0) * 100:.0f}%",
                "Apply Link": job.get("job_apply_link", "#")
            })
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        
        st.download_button(
            "📥 Download CSV",
            data=csv,
            file_name="saved_jobs.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
        
        st.info("💡 Tip: Download and email to yourself")
        
        st.divider()
        if st.button("🗑️ Clear All", key="clear_all", use_container_width=True):
            st.session_state.saved_jobs = []
            st.rerun()
    else:
        st.info("💼 No saved jobs yet. Click Save on jobs you like!")

# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 CV Upload", "🔍 Analysis", "💼 Jobs", "✍️ CV Rewrite", "📧 Cover Letter"])

# TAB 1: CV UPLOAD
with tab1:
    st.header("Upload Your CV")
    st.markdown("Upload your CV to unlock AI-powered career tools")
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">📋 What This Does</div>
        <div class="info-box-text">
            Upload your CV to:
            <ul style="margin: 0.5rem 0 0 1.25rem; padding: 0;">
                <li>Get instant AI feedback</li>
                <li>Find matching job opportunities</li>
                <li>Optimize for specific roles</li>
                <li>Generate tailored cover letters</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded = st.file_uploader("Choose file (PDF or TXT)", type=["txt", "pdf"], key="cv_up")
    if uploaded:
        try:
            if uploaded.type == "application/pdf":
                import PyPDF2
                from io import BytesIO
                with st.spinner("Parsing PDF..."):
                    reader = PyPDF2.PdfReader(BytesIO(uploaded.read()))
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    st.session_state.cv_text = text
                    st.success("✅ PDF uploaded successfully")
            else:
                st.session_state.cv_text = uploaded.read().decode("utf-8")
                st.success("✅ File uploaded successfully")
        except Exception as e:
            st.error(f"Error: {e}")

# TAB 2: AI ANALYSIS
with tab2:
    st.header("AI Profile Analysis")
    st.markdown("Get instant AI-powered career insights")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV in the first tab")
    else:
        if st.button("🎯 Analyze My Profile", key="btn_analyze", type="primary", use_container_width=True):
            st.session_state.is_processing = True
            with st.spinner("Analyzing your CV..."):
                try:
                    from groq import Groq
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    prompt = f"Analyze this CV and provide:\n1. Target Roles (3-4 job titles)\n2. Key Skills\n3. Top Strengths\n4. Areas for Improvement\n\nCV:\n{st.session_state.cv_text[:2000]}"
                    resp = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    st.success("✅ Analysis Complete!")
                    st.markdown(resp.choices[0].message.content)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
            st.session_state.is_processing = False

# TAB 3: JOB MATCHING
with tab3:
    st.header("AI-Powered Job Matching")
    st.markdown("Find jobs that match your skills")
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">💼 Features</div>
        <div class="info-box-text">
            <ul style="margin: 0.5rem 0 0 1.25rem; padding: 0;">
                <li><strong>Smart Matching:</strong> AI calculates match scores</li>
                <li><strong>Real Jobs:</strong> Live listings from major boards</li>
                <li><strong>Save & Export:</strong> Bookmark and download jobs</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if JSearchClient is None:
        st.error("Job matching module not loaded")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            target_role = st.text_input("Target Role", placeholder="e.g., Python Developer")
        with col2:
            location = st.text_input("Location", placeholder="Remote, New York")
        
        if st.button("🔍 Search Jobs", key="btn_search", type="primary", use_container_width=True):
            st.session_state.search_count += 1
            st.session_state.is_processing = True
            
            with st.spinner("Searching for jobs..."):
                try:
                    client = JSearchClient(api_key=st.secrets.get("JSEARCH_API_KEY", ""))
                    results = client.search_jobs(
                        query=target_role.strip() if target_role else "consultant",
                        location=location if location else None
                    )
                    
                    jobs_data = results.get("data", [])
                    jobs_json = json.dumps(jobs_data, default=str)
                    st.session_state.search_results = json.loads(jobs_json)
                    
                    st.success(f"✅ Found {len(st.session_state.search_results)} jobs!")
                except Exception as e:
                    st.error(f"Search failed: {e}")
            st.session_state.is_processing = False
        
        if st.session_state.search_results:
            st.divider()
            for idx, job in enumerate(st.session_state.search_results):
                title = str(job.get("job_title", "Job"))
                company = str(job.get("employer_name", "Company"))
                city = str(job.get("job_city", ""))
                score = float(job.get("career_compass_match_score", 0))
                
                if score >= 0.7:
                    badge_class, badge_text = "excellent", "🟢 Excellent Match"
                elif score >= 0.4:
                    badge_class, badge_text = "good", "🟡 Good Match"
                else:
                    badge_class, badge_text = "match", "⚪ Potential Fit"
                
                is_saved = any(str(s.get("job_title")) == title and str(s.get("employer_name")) == company 
                              for s in st.session_state.saved_jobs)
                
                st.markdown(f"""
                <div class="job-card" style="position: relative;">
                    <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">{title}</div>
                    <div style="color: var(--text-secondary); margin-bottom: 0.75rem;">
                        🏢 {company} • 📍 {city}
                    </div>
                    <div class="badge badge-{badge_class}">{badge_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.success("💾 Saved") if is_saved else st.markdown("Click save to bookmark")
                with c2:
                    key = f"save_{idx}_{hashlib.md5(f'{title}{company}'.encode()).hexdigest()}"
                    if st.button("💾 Save", key=key, use_container_width=True):
                        if not is_saved:
                            st.session_state.saved_jobs.append({
                                "job_title": title,
                                "employer_name": company,
                                "job_city": city,
                                "job_description": str(job.get("job_description", ""))[:200],
                                "job_required_skills": job.get("job_required_skills", []),
                                "job_apply_link": str(job.get("job_apply_link", "#")),
                                "career_compass_match_score": score
                            })
                            st.rerun()
                
                with st.expander("📋 View Details"):
                    st.write(job.get("job_description", "No description"))
                st.divider()

# TAB 4: CV REWRITE
with tab4:
    st.header("AI CV Rewriting")
    st.markdown("Optimize your CV for specific jobs")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Upload your CV first")
    else:
        job_desc = st.text_area("Paste job description", height=150, key="rewrite_desc")
        
        if st.button("✨ Rewrite CV", key="btn_rewrite", type="primary", use_container_width=True):
            if job_desc:
                with st.spinner("Optimizing CV..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        prompt = f"Optimize this CV for the job:\nCV: {st.session_state.cv_text[:2000]}\nJob: {job_desc[:1000]}"
                        resp = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=1000
                        )
                        
                        st.success("✅ CV Optimized!")
                        st.text_area("Optimized CV", resp.choices[0].message.content, height=400)
                        st.download_button("📥 Download", resp.choices[0].message.content, "optimized_cv.txt")
                    except Exception as e:
                        st.error(f"Failed: {e}")

# TAB 5: COVER LETTER
with tab5:
    st.header("AI Cover Letter Generator")
    st.markdown("Generate professional cover letters")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Upload your CV first")
    else:
        col1, col2 = st.columns(2)
        with col1:
            company = st.text_input("Company Name")
        with col2:
            title = st.text_input("Job Title")
        
        job_desc = st.text_area("Job Description (optional)", height=120)
        
        if st.button("✍️ Generate", key="btn_cl", type="primary", use_container_width=True):
            if company and title:
                with st.spinner("Writing cover letter..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        prompt = f"Write a cover letter for {company} - {title}.\nCV: {st.session_state.cv_text[:1500]}\nJob: {job_desc[:500]}"
                        resp = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=600
                        )
                        
                        st.success("✅ Cover Letter Generated!")
                        st.text_area("Your Cover Letter", resp.choices[0].message.content, height=400)
                        st.download_button("📥 Download", resp.choices[0].message.content, "cover_letter.txt")
                    except Exception as e:
                        st.error(f"Failed: {e}")

# ==========================================
# CLEAN FOOTER
# ==========================================
st.markdown("""
<div class="footer">
    <div class="footer-grid">
        <div class="footer-col">
            <h4>🧭 Career Compass</h4>
            <p style="color: var(--text-secondary); line-height: 1.6;">
                Free AI-powered career tools to help you land your dream job.
            </p>
        </div>
        <div class="footer-col">
            <h4>Services</h4>
            <ul>
                <li>CV Analysis</li>
                <li>Job Matching</li>
                <li>CV Rewriting</li>
                <li>Cover Letters</li>
            </ul>
        </div>
        <div class="footer-col">
            <h4>Legal</h4>
            <ul>
                <li>Privacy Policy</li>
                <li>Terms of Service</li>
            </ul>
        </div>
        <div class="footer-col">
            <h4>About</h4>
            <ul>
                <li>Contact Us</li>
                <li>Feedback</li>
            </ul>
        </div>
    </div>
    <div class="footer-bottom">
        <p>© 2026 Career Compass. A Community Project. All rights reserved.</p>
    </div>
</div>
""", unsafe_allow_html=True)