import streamlit as st
import sys
from pathlib import Path
import json
import hashlib
import pandas as pd
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io

sys.path.append(str(Path(__file__).parent.parent))

try:
    from modules.jsearch_client import JSearchClient
except ImportError:
    JSearchClient = None

st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="wide")

# ==========================================
# THEME & STYLING
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    body, .stApp { font-family: 'Inter', sans-serif; background-color: #F8FAFC; color: #1E293B; }
    h1, h2, h3 { font-weight: 600; letter-spacing: -0.025em; }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background: transparent; }
    .stTabs [data-baseweb="tab"] { 
        height: 42px; white-space: pre-wrap; background-color: #FFFFFF; 
        border-radius: 10px 10px 0 0; font-weight: 500; color: #64748B; 
        border: none !important; padding: 0 16px !important;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #FFFFFF !important; color: #4F46E5 !important; 
        font-weight: 600; border-bottom: 3px solid #4F46E5 !important;
    }
    
    /* Job Cards */
    .job-card { 
        background: #FFFFFF; border-radius: 12px; padding: 20px 24px; 
        margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03); 
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); 
        border: 1px solid #E2E8F0; position: relative; overflow: hidden; 
    }
    .job-card:hover { 
        transform: translateY(-3px); 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04); 
        border-color: #CBD5E1; 
    }
    .job-card::before { 
        content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 3px; 
        background: linear-gradient(90deg, #4F46E5, #8B5CF6); 
    }
    .job-title { font-size: 1.2rem; font-weight: 600; color: #0F172A; margin: 0 0 6px 0; }
    .job-meta { font-size: 0.875rem; color: #64748B; display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
    .job-meta span { display: flex; align-items: center; gap: 5px; }
    
    /* Badges */
    .badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 600; margin-top: 10px; text-transform: uppercase; letter-spacing: 0.025em; }
    .badge-excellent { background-color: #D1FAE5; color: #065F46; }
    .badge-good { background-color: #FEF3C7; color: #92400E; }
    .badge-match { background-color: #E2E8F0; color: #475569; }
    
    /* Buttons & Inputs */
    .stButton button { border-radius: 8px !important; font-weight: 500 !important; transition: all 0.2s !important; border: none !important; }
    .stButton button:hover { transform: translateY(-1px); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important; }
    .stTextInput div, .stSelectbox div, .stTextArea div { border-radius: 8px !important; border: 1px solid #E2E8F0 !important; }
    .stTextInput div:focus-within, .stSelectbox div:focus-within, .stTextArea div:focus-within { border-color: #4F46E5 !important; box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1) !important; }
    
    /* Expander */
    .streamlit-expanderHeader { border-radius: 8px !important; background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; }
    .streamlit-expanderHeader:hover { background-color: #F1F5F9 !important; }
    .streamlit-expanderContent { border-radius: 0 0 8px 8px !important; border: 1px solid #E2E8F0 !important; border-top: none !important; }
    
    /* Sidebar */
    .css-1d391kg { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; }
    .stSidebar > div { padding-top: 2rem !important; }
    
    /* Info Boxes */
    .info-box { 
        background-color: #EFF6FF; border-left: 4px solid #3B82F6; 
        padding: 16px 20px; border-radius: 8px; margin: 16px 0; 
    }
    .info-box-title { font-weight: 600; color: #1E40AF; margin-bottom: 8px; }
    .info-box-text { color: #1E40AF; line-height: 1.6; }
    
    .steps-box { 
        background-color: #F0FDF4; border-left: 4px solid #10B981; 
        padding: 16px 20px; border-radius: 8px; margin: 16px 0; 
    }
    .steps-box-title { font-weight: 600; color: #065F46; margin-bottom: 8px; }
    .steps-box-text { color: #065F46; line-height: 1.6; }
    
    /* Loading Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .loading-text { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }

    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .hero-section { padding: 24px 20px !important; }
        .hero-title { font-size: 1.75rem !important; }
        .job-card { padding: 16px !important; }
        .job-meta { flex-direction: column; align-items: flex-start; gap: 4px; }
        .stTabs [data-baseweb="tab"] { padding: 0 10px !important; font-size: 0.85rem; }
        .row-widget.stHorizontal { flex-direction: column !important; }
        .row-widget.stHorizontal > div { width: 100% !important; }
        .stSidebar { width: 300px !important; }
        .footer-grid { grid-template-columns: 1fr; gap: 24px; }
    }

    /* Footer */
    .footer {
        background-color: #F8FAFC;
        padding: 40px 0;
        margin-top: 60px;
        border-top: 1px solid #E2E8F0;
        color: #64748B;
        font-size: 0.875rem;
    }
    .footer-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 40px;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }
    .footer-col h4 {
        color: #0F172A;
        font-weight: 600;
        margin-bottom: 16px;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .footer-col ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .footer-col li {
        margin-bottom: 10px;
    }
    .footer-bottom {
        text-align: center;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #E2E8F0;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# BROWSER LOCALSTORAGE PERSISTENCE
# ==========================================
import streamlit.components.v1 as components

# Inject JavaScript for localStorage sync
components.html("""
<script>
// Auto-save saved_jobs to localStorage
function saveJobs() {
    const savedJobsElement = document.querySelector('#saved-jobs-data');
    if (savedJobsElement) {
        const jobsData = savedJobsElement.getAttribute('data-jobs');
        if (jobsData) {
            localStorage.setItem('cc_saved_jobs', jobsData);
        }
    }
}

// Auto-load saved_jobs from localStorage on page load
window.addEventListener('load', function() {
    const stored = localStorage.getItem('cc_saved_jobs');
    if (stored) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.id = 'cc-load-jobs';
        input.value = stored;
        document.body.appendChild(input);
    }
});

// Save when session state changes
setInterval(saveJobs, 2000);
</script>
""", height=0)

# Initialize session state
if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = []
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# Check for localStorage data
load_jobs_element = st.empty()
if hasattr(st, 'session_state'):
    try:
        # This is a workaround - in practice, you'd use streamlit-js-eval package
        # For now, we'll just use session state
        pass
    except:
        pass

# HERO SECTION
st.markdown("""
<div style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); padding: 32px 28px; border-radius: 16px; margin-bottom: 24px; color: white; box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.25);">
    <div style="font-size: 2.25rem; font-weight: 700; margin: 0 0 8px 0; letter-spacing: -0.02em;">🧭 Career Compass</div>
    <div style="font-size: 1.05rem; font-weight: 400; opacity: 0.9; margin: 0;">AI-powered tools to accelerate your career journey</div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("### 💼 Saved Jobs")
    if st.session_state.saved_jobs:
        st.markdown(f'<div style="background:#D1FAE5; color:#065F46; padding:8px 12px; border-radius:8px; font-size:0.875rem; font-weight:500;">✅ {len(st.session_state.saved_jobs)} jobs saved</div>', unsafe_allow_html=True)
        
        for i, job in enumerate(st.session_state.saved_jobs):
            title = str(job.get('job_title', 'Job'))[:35]
            with st.expander(f"**{i+1}.** {title}...", expanded=False):
                st.markdown(f'🏢 **{job.get("employer_name", "N/A")}**')
                if st.button(f"🗑️ Remove", key=f"remove_{i}", use_container_width=True):
                    st.session_state.saved_jobs.pop(i)
                    st.rerun()
        
        st.divider()
        st.markdown("### 📤 Export & Email Jobs")
        
        # Prepare export data
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
        
        # CSV Download
        st.download_button(
            "📥 Download CSV", 
            data=csv, 
            file_name="saved_jobs.csv", 
            mime="text/csv", 
            use_container_width=True
        )
        
        # Email feature
        st.markdown('<p class="text-muted" style="font-size:0.8rem; margin:8px 0;">Or email jobs to your inbox</p>', unsafe_allow_html=True)
        user_email = st.text_input("", placeholder="you@example.com", key="email_jobs_input", label_visibility="collapsed")
        
        if st.button("📧 Email My Jobs", key="email_jobs_btn", use_container_width=True):
            if user_email and "@" in user_email:
                if len(st.session_state.saved_jobs) > 0:
                    try:
                        # Create email
                        msg = MIMEMultipart()
                        msg['From'] = "info@careeraisupport.org"
                        msg['To'] = user_email
                        msg['Subject'] = "🧭 Your Saved Jobs from Career Compass"
                        
                        body = f"""Hi there!

Here are the {len(st.session_state.saved_jobs)} jobs you saved on Career Compass. Good luck with your applications! 🚀

— The Career Compass Team
https://careeraisupport.streamlit.app"""
                        
                        msg.attach(MIMEText(body, 'plain'))
                        
                        # Attach CSV
                        csv_buffer = io.StringIO()
                        df.to_csv(csv_buffer, index=False)
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(csv_buffer.getvalue().encode())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment', filename="career_compass_jobs.csv")
                        msg.attach(part)
                        
                        # Send via Gmail SMTP
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(st.secrets["GMAIL_USER"], st.secrets["GMAIL_APP_PASSWORD"])
                        server.send_message(msg)
                        server.quit()
                        
                        st.success(f"✅ Jobs sent to {user_email}!")
                    except Exception as e:
                        st.error("Failed to send email. Please try downloading the CSV instead.")
                else:
                    st.warning("No jobs saved yet.")
            else:
                st.warning("Please enter a valid email address.")
        
        st.divider()
        
        if st.button("🗑️ Clear All", key="clear_all", use_container_width=True):
            st.session_state.saved_jobs = []
            st.rerun()
    else:
        st.markdown('<p class="text-muted">No saved jobs yet. Click 💾 on jobs you like!</p>', unsafe_allow_html=True)

# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 CV Upload", "🔍 Analysis", "💼 Jobs", "✍️ CV Rewrite", "📧 Cover Letter"])

# TAB 1: CV UPLOAD
with tab1:
    st.header("Upload Your CV")
    st.markdown('<p class="text-muted">Upload your CV to get started with AI-powered career tools</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">📋 What This Does</div>
        <div class="info-box-text">
            Upload your current CV/resume to unlock all AI-powered features. Your CV will be analyzed to:
            <ul style="margin: 8px 0 0 20px; padding: 0;">
                <li>Identify your key skills and experience</li>
                <li>Match you with relevant job opportunities</li>
                <li>Generate personalized career insights</li>
                <li>Optimize your CV for specific roles</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="steps-box">
        <div class="steps-box-title">✅ How to Use</div>
        <div class="steps-box-text">
            <strong>Step 1:</strong> Click "Choose file" above<br>
            <strong>Step 2:</strong> Select your CV file (PDF or TXT format)<br>
            <strong>Step 3:</strong> Wait for the upload to complete<br>
            <strong>Step 4:</strong> Navigate to other tabs to use AI features
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="text-muted">Supported formats: PDF, TXT (Max file size: 10MB)</p>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader("Choose file", type=["txt", "pdf"], key="cv_up")
    if uploaded:
        try:
            if uploaded.type == "application/pdf":
                import PyPDF2
                from io import BytesIO
                with st.spinner("📄 Parsing PDF... Please wait."):
                    progress_bar = st.progress(0)
                    reader = PyPDF2.PdfReader(BytesIO(uploaded.read()))
                    text = ""
                    total_pages = len(reader.pages)
                    
                    for i, page in enumerate(reader.pages):
                        text += page.extract_text() + "\n"
                        progress_bar.progress((i + 1) / total_pages)
                    
                    st.session_state.cv_text = text
                    progress_bar.empty()
                    st.success("✅ PDF uploaded & parsed successfully")
            else:
                with st.spinner("📄 Reading text file..."):
                    st.session_state.cv_text = uploaded.read().decode("utf-8")
                    st.success("✅ Text file uploaded successfully")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# TAB 2: AI ANALYSIS
with tab2:
    st.header("AI Profile Analysis")
    st.markdown('<p class="text-muted">Get AI-powered insights about your CV</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">🤖 What This Does</div>
        <div class="info-box-text">
            Our AI analyzes your CV to provide comprehensive career insights including:
            <ul style="margin: 8px 0 0 20px; padding: 0;">
                <li><strong>Target Roles:</strong> 3-4 job titles that match your background</li>
                <li><strong>Key Skills:</strong> Technical and soft skills identified in your CV</li>
                <li><strong>Top Strengths:</strong> Your competitive advantages</li>
                <li><strong>Areas for Improvement:</strong> Constructive feedback to enhance your CV</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="steps-box">
        <div class="steps-box-title">✅ How to Use</div>
        <div class="steps-box-text">
            <strong>Step 1:</strong> Ensure you've uploaded your CV in the "CV Upload" tab<br>
            <strong>Step 2:</strong> Click "Analyze My Profile" button below<br>
            <strong>Step 3:</strong> Wait for AI analysis (usually takes 5-10 seconds)<br>
            <strong>Step 4:</strong> Review the insights and use them to guide your job search
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV in the first tab before analyzing.")
    else:
        if st.button("🎯 Analyze My Profile", key="btn_analyze", type="primary", use_container_width=True, disabled=st.session_state.is_processing):
            st.session_state.is_processing = True
            
            progress_container = st.container()
            with progress_container:
                st.markdown('<div class="loading-text">⏳ Initializing AI analysis...</div>', unsafe_allow_html=True)
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    from groq import Groq
                    
                    time.sleep(0.3)
                    progress_bar.progress(20)
                    status_text.markdown('<div class="loading-text">📤 Sending CV to AI...</div>', unsafe_allow_html=True)
                    
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    time.sleep(0.3)
                    progress_bar.progress(40)
                    status_text.markdown('<div class="loading-text">🤖 AI is analyzing your profile...</div>', unsafe_allow_html=True)
                    
                    prompt = f"You are an expert career coach. Analyze this CV and provide:\n1. Target Roles (3-4 suitable job titles)\n2. Key Skills (technical and soft skills)\n3. Top Strengths\n4. Areas for Improvement\n\nCV:\n{st.session_state.cv_text[:2000]}"
                    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                    
                    time.sleep(0.3)
                    progress_bar.progress(80)
                    status_text.markdown('<div class="loading-text">✨ Generating insights...</div>', unsafe_allow_html=True)
                    
                    time.sleep(0.3)
                    progress_bar.progress(100)
                    status_text.markdown('<div class="loading-text">✅ Analysis complete!</div>', unsafe_allow_html=True)
                    
                    time.sleep(0.5)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success("✅ Analysis Complete!")
                    st.markdown(resp.choices[0].message.content)
                    st.session_state.is_processing = False
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"Analysis failed: {e}")
                    st.session_state.is_processing = False

# TAB 3: JOB MATCHING
with tab3:
    st.header("AI-Powered Job Matching")
    st.markdown('<p class="text-muted">Find jobs that match your skills and experience</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">💼 What This Does</div>
        <div class="info-box-text">
            Search and discover job opportunities that match your skills and experience:
            <ul style="margin: 8px 0 0 20px; padding: 0;">
                <li><strong>Smart Matching:</strong> AI calculates match scores based on your CV</li>
                <li><strong>Real Jobs:</strong> Live job listings from major job boards</li>
                <li><strong>Save Jobs:</strong> Bookmark interesting positions for later</li>
                <li><strong>Export:</strong> Download saved jobs to Excel for tracking</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="steps-box">
        <div class="steps-box-title">✅ How to Use</div>
        <div class="steps-box-text">
            <strong>Step 1:</strong> Enter your target job title (e.g., "Strategy Consultant", "Business Analyst")<br>
            <strong>Step 2:</strong> Specify location (e.g., "Remote", "New York", or leave blank for any)<br>
            <strong>Step 3:</strong> Click "Search Jobs" button<br>
            <strong>Step 4:</strong> Review results and click "Save" on jobs you're interested in<br>
            <strong>Step 5:</strong> View full details by expanding each job listing<br>
            <strong>Step 6:</strong> Use saved jobs for CV rewriting and cover letters
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.warning("⚠️ **Job listings are sourced from third-party APIs. We do not verify accuracy, availability, or legitimacy of postings. Always research employers before applying.**")
    
    if JSearchClient is None:
        st.error("Job matching module not loaded")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            target_role = st.text_input("Target Role", placeholder="e.g., Strategy Consultant, Business Analyst", key="target_role")
        with col2:
            location = st.text_input("Location", placeholder="Remote, New York", key="location")
        
        detected = []
        if st.session_state.cv_text:
            cv_lower = st.session_state.cv_text.lower()
            for kw in ["strategy", "consulting", "analysis", "management", "finance", "marketing", "operations"]:
                if kw in cv_lower:
                    detected.append(kw.title())
            if detected:
                st.info(f"💡 **Detected Skills:** {', '.join(detected)}")
        
        if st.button("🔍 Search Jobs", key="btn_search", type="primary", use_container_width=True, disabled=st.session_state.is_processing):
            query = target_role.strip() if target_role else "consultant"
            st.session_state.is_processing = True
            
            progress_container = st.container()
            with progress_container:
                st.markdown('<div class="loading-text">⏳ Preparing job search...</div>', unsafe_allow_html=True)
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    time.sleep(0.3)
                    progress_bar.progress(20)
                    status_text.markdown('<div class="loading-text">🔍 Searching job database...</div>', unsafe_allow_html=True)
                    
                    client = JSearchClient(api_key=st.secrets.get("JSEARCH_API_KEY", ""))
                    
                    time.sleep(0.5)
                    progress_bar.progress(50)
                    status_text.markdown('<div class="loading-text">📥 Fetching job listings...</div>', unsafe_allow_html=True)
                    
                    results = client.search_jobs(query=query, location=location if location else None, user_skills=detected)
                    
                    time.sleep(0.3)
                    progress_bar.progress(70)
                    status_text.markdown('<div class="loading-text">🎯 Calculating match scores...</div>', unsafe_allow_html=True)
                    
                    jobs_data = results.get("data", [])
                    jobs_json = json.dumps(jobs_data, default=str)
                    clean_results = json.loads(jobs_json)
                    
                    time.sleep(0.3)
                    progress_bar.progress(90)
                    status_text.markdown('<div class="loading-text">✨ Processing results...</div>', unsafe_allow_html=True)
                    
                    st.session_state.search_results = clean_results
                    
                    time.sleep(0.3)
                    progress_bar.progress(100)
                    status_text.markdown(f'<div class="loading-text">✅ Found {len(clean_results)} matching jobs!</div>', unsafe_allow_html=True)
                    
                    time.sleep(0.5)
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success(f"✅ Found {len(clean_results)} matching jobs!")
                    st.session_state.is_processing = False
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"Search failed: {e}")
                    st.session_state.is_processing = False
        
        if st.session_state.search_results:
            st.divider()
            for idx, job in enumerate(st.session_state.search_results):
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
                
                if score >= 0.7:
                    badge_class, badge_text = "excellent", "🟢 Excellent Match"
                elif score >= 0.4:
                    badge_class, badge_text = "good", "🟡 Good Match"
                else:
                    badge_class, badge_text = "match", "⚪ Potential Fit"
                
                is_saved = any(str(s.get("job_title")) == title and str(s.get("employer_name")) == company 
                              for s in st.session_state.saved_jobs)
                
                st.markdown(f"""
                <div class="job-card">
                    <div class="job-title">{title}</div>
                    <div class="job-meta">
                        <span>🏢 {company}</span>
                        <span>📍 {city}</span>
                    </div>
                    <div class="badge badge-{badge_class}">{badge_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([4, 1])
                with c1:
                    if is_saved:
                        st.success("💾 Saved to your list")
                    else:
                        st.markdown('<p class="text-muted">Click save to bookmark this job</p>', unsafe_allow_html=True)
                with c2:
                    key = f"save_{idx}_{hashlib.md5(f'{title}{company}'.encode()).hexdigest()}"
                    if st.button("💾 Save", key=key, use_container_width=True, disabled=st.session_state.is_processing):
                        if is_saved:
                            st.session_state.saved_jobs = [j for j in st.session_state.saved_jobs 
                                                           if not (str(j.get("job_title")) == title and str(j.get("employer_name")) == company)]
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
                
                with st.expander("📋 View Full Job Details"):
                    st.markdown("**📝 Job Description**")
                    st.write(str(job.get("job_description", "No description available")))
                    
                    if skills:
                        st.markdown("**💡 Required Skills**")
                        st.write(", ".join(skills))
                    
                    salary_info = job.get("normalized_salary", {})
                    if salary_info and isinstance(salary_info, dict):
                        min_sal = salary_info.get("min_annual_usd", 0)
                        max_sal = salary_info.get("max_annual_usd", 0)
                        if min_sal and max_sal:
                            st.markdown("**💰 Salary Range**")
                            st.write(f"${min_sal:,} - ${max_sal:,} per year")
                    
                    if apply_url and apply_url != "#" and apply_url != "None":
                        st.divider()
                        st.markdown(f"""
                        <div style="text-align: center; margin: 16px 0;">
                            <a href="{apply_url}" target="_blank" 
                               style="background-color: #10B981; color: white; padding: 10px 24px; border-radius: 8px; 
                                      text-decoration: none; font-weight: 600; display: inline-block; transition: all 0.2s;">
                                🚀 Apply Now
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.divider()

# TAB 4: CV REWRITE
with tab4:
    st.header("✍️ AI CV Rewriting")
    st.markdown('<p class="text-muted">Optimize your CV for specific job descriptions</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">✨ What This Does</div>
        <div class="info-box-text">
            Optimize your CV to match specific job descriptions:
            <ul style="margin: 8px 0 0 20px; padding: 0;">
                <li><strong>Keyword Optimization:</strong> Highlights relevant skills and experience</li>
                <li><strong>Tailored Content:</strong> Rewrites your CV for each specific role</li>
                <li><strong>ATS-Friendly:</strong> Improves chances of passing automated screening</li>
                <li><strong>Professional Tone:</strong> Ensures polished, industry-appropriate language</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="steps-box">
        <div class="steps-box-title">✅ How to Use</div>
        <div class="steps-box-text">
            <strong>Step 1:</strong> Choose "Select from saved jobs" if you have jobs saved, or "Paste manually" to enter a job description<br>
            <strong>Step 2:</strong> If using saved jobs, select the job from the dropdown menu<br>
            <strong>Step 3:</strong> If pasting manually, copy and paste the full job description<br>
            <strong>Step 4:</strong> Click "Rewrite My CV" button<br>
            <strong>Step 5:</strong> Review the optimized CV and download it<br>
            <strong>Step 6:</strong> <em>Important:</em> Edit the output to ensure it accurately reflects your experience before using
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.warning("⚠️ **AI-generated content is a draft. Always review, edit, and personalize before submitting to employers.**")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        opt = st.radio("Choose option:", ["📋 Select from saved jobs", "✍️ Paste manually"], key="rewrite_opt")
        job_desc = ""
        
        if opt == "📋 Select from saved jobs" and st.session_state.saved_jobs:
            opts = [f"{j.get('job_title')} at {j.get('employer_name')}" for j in st.session_state.saved_jobs]
            sel = st.selectbox("Select a job:", opts, key="rewrite_sel")
            idx = opts.index(sel)
            job_desc = st.session_state.saved_jobs[idx].get("job_description", "")
            st.info(f"📄 Using: {sel}")
        else:
            job_desc = st.text_area("Paste job description:", height=150, key="rewrite_desc", 
                                   placeholder="Copy and paste the full job description here...")
        
        if st.button("✨ Rewrite My CV", key="btn_rewrite", type="primary", use_container_width=True, disabled=st.session_state.is_processing):
            if job_desc:
                st.session_state.is_processing = True
                
                progress_container = st.container()
                with progress_container:
                    st.markdown('<div class="loading-text">⏳ Preparing CV optimization...</div>', unsafe_allow_html=True)
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        from groq import Groq
                        
                        time.sleep(0.3)
                        progress_bar.progress(20)
                        status_text.markdown('<div class="loading-text">📤 Sending CV and job description...</div>', unsafe_allow_html=True)
                        
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        time.sleep(0.3)
                        progress_bar.progress(40)
                        status_text.markdown('<div class="loading-text">🤖 AI is analyzing job requirements...</div>', unsafe_allow_html=True)
                        
                        prompt = f"Optimize this CV for the following job. Highlight relevant skills and experience.\nCV: {st.session_state.cv_text[:2000]}\nJob: {job_desc[:1000]}"
                        resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], max_tokens=1000)
                        
                        time.sleep(0.5)
                        progress_bar.progress(70)
                        status_text.markdown('<div class="loading-text">✨ Rewriting CV with optimized content...</div>', unsafe_allow_html=True)
                        
                        time.sleep(0.5)
                        progress_bar.progress(100)
                        status_text.markdown('<div class="loading-text">✅ CV optimization complete!</div>', unsafe_allow_html=True)
                        
                        time.sleep(0.5)
                        progress_bar.empty()
                        status_text.empty()
                        
                        st.success("✅ CV Optimized!")
                        st.text_area("Optimized CV", resp.choices[0].message.content, height=400)
                        st.download_button("📥 Download Optimized CV", resp.choices[0].message.content, "optimized_cv.txt")
                        st.session_state.is_processing = False
                        
                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"Rewriting failed: {e}")
                        st.session_state.is_processing = False

# TAB 5: COVER LETTER
with tab5:
    st.header("📧 AI Cover Letter Generator")
    st.markdown('<p class="text-muted">Generate personalized cover letters in seconds</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">✉️ What This Does</div>
        <div class="info-box-text">
            Generate personalized, professional cover letters in seconds:
            <ul style="margin: 8px 0 0 20px; padding: 0;">
                <li><strong>Personalized Content:</strong> Tailored to each specific job and company</li>
                <li><strong>Professional Tone:</strong> Industry-appropriate language and formatting</li>
                <li><strong>Skills Highlighting:</strong> Emphasizes your most relevant qualifications</li>
                <li><strong>Time-Saving:</strong> Creates a first draft in seconds</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="steps-box">
        <div class="steps-box-title">✅ How to Use</div>
        <div class="steps-box-text">
            <strong>Step 1:</strong> Choose "Select from saved jobs" if you have jobs saved, or "Enter manually" to input details<br>
            <strong>Step 2:</strong> If using saved jobs, select the job from the dropdown menu<br>
            <strong>Step 3:</strong> If entering manually, fill in company name, job title, and optionally paste the job description<br>
            <strong>Step 4:</strong> Click "Generate Cover Letter" button<br>
            <strong>Step 5:</strong> Review the generated cover letter<br>
            <strong>Step 6:</strong> <em>Important:</em> Edit the output to personalize it further, add specific examples from your experience, and ensure accuracy before sending to employers
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.warning("⚠️ **AI-generated cover letters are starting points. Always customize with specific examples and verify company details before sending.**")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        opt = st.radio("Choose option:", ["📋 Select from saved jobs", "✍️ Enter manually"], key="cl_opt")
        company = ""
        title = ""
        job_desc = ""
        
        if opt == "📋 Select from saved jobs" and st.session_state.saved_jobs:
            opts = [f"{j.get('job_title')} at {j.get('employer_name')}" for j in st.session_state.saved_jobs]
            sel = st.selectbox("Select a job:", opts, key="cl_sel")
            idx = opts.index(sel)
            job = st.session_state.saved_jobs[idx]
            company = str(job.get("employer_name", ""))
            title = str(job.get("job_title", ""))
            job_desc = job.get("job_description", "")
            st.info(f"📄 Using: {company} - {title}")
        else:
            c1, c2 = st.columns(2)
            with c1: company = st.text_input("Company Name", key="cl_comp")
            with c2: title = st.text_input("Job Title", key="cl_title")
            job_desc = st.text_area("Job Description", height=150, key="cl_desc", 
                                   placeholder="Paste job description for more targeted letter (optional)...")
        
        if st.button("✍️ Generate Cover Letter", key="btn_cl", type="primary", use_container_width=True, disabled=st.session_state.is_processing):
            if company and title:
                st.session_state.is_processing = True
                
                progress_container = st.container()
                with progress_container:
                    st.markdown('<div class="loading-text">⏳ Preparing cover letter generation...</div>', unsafe_allow_html=True)
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        from groq import Groq
                        
                        time.sleep(0.3)
                        progress_bar.progress(20)
                        status_text.markdown('<div class="loading-text">📤 Sending your information...</div>', unsafe_allow_html=True)
                        
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        
                        time.sleep(0.3)
                        progress_bar.progress(40)
                        status_text.markdown('<div class="loading-text">🤖 AI is analyzing job requirements...</div>', unsafe_allow_html=True)
                        
                        prompt = f"Write a professional cover letter for {company} - {title}.\nCV: {st.session_state.cv_text[:1500]}\nJob Details: {job_desc[:500]}"
                        resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}], max_tokens=600)
                        
                        time.sleep(0.5)
                        progress_bar.progress(70)
                        status_text.markdown('<div class="loading-text">✍️ Writing personalized cover letter...</div>', unsafe_allow_html=True)
                        
                        time.sleep(0.5)
                        progress_bar.progress(100)
                        status_text.markdown('<div class="loading-text">✅ Cover letter generated!</div>', unsafe_allow_html=True)
                        
                        time.sleep(0.5)
                        progress_bar.empty()
                        status_text.empty()
                        
                        st.success("✅ Cover Letter Generated!")
                        st.text_area("Your Cover Letter", resp.choices[0].message.content, height=400)
                        st.download_button("📥 Download Cover Letter", resp.choices[0].message.content, "cover_letter.txt")
                        st.session_state.is_processing = False
                        
                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"Generation failed: {e}")
                        st.session_state.is_processing = False

# ==========================================
# PROFESSIONAL FOOTER (NO LINKS)
# ==========================================
st.markdown("""
<div class="footer">
    <div class="footer-grid">
        <div class="footer-col">
            <h4>🧭 Career Compass</h4>
            <p style="line-height: 1.6;">AI-powered tools to accelerate your career journey. Find jobs, optimize your CV, and generate cover letters in seconds.</p>
        </div>
        <div class="footer-col">
            <h4>Services</h4>
            <ul>
                <li>Our Services</li>
                <li>Job Matching</li>
                <li>CV Analysis</li>
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
            <h4>Connect</h4>
            <ul>
                <li>Contact Us</li>
            </ul>
        </div>
    </div>
    <div class="footer-bottom">
        <p>© 2026 Career Compass. A Community Project. All rights reserved.</p>
    </div>
</div>
""", unsafe_allow_html=True)