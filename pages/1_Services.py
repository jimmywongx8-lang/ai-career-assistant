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
# PROFESSIONAL THEME & STYLING (WIX-LEVEL)
# ==========================================
st.markdown("""
<style>
    /* Import Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Root Variables for Consistency */
    :root {
        --primary-color: #6366F1;
        --primary-hover: #4F46E5;
        --secondary-color: #8B5CF6;
        --success-color: #10B981;
        --warning-color: #F59E0B;
        --error-color: #EF4444;
        --text-primary: #111827;
        --text-secondary: #6B7280;
        --bg-primary: #FFFFFF;
        --bg-secondary: #F9FAFB;
        --border-color: #E5E7EB;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
    }
    
    /* Global Styles */
    body, .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        background-attachment: fixed;
        color: var(--text-primary);
        font-size: 16px;
        line-height: 1.6;
    }
    
    /* Main Container */
    .main .block-container {
        padding: 2rem 3rem 3rem 3rem;
        max-width: 1400px;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        line-height: 1.2;
        letter-spacing: -0.02em;
        color: var(--text-primary);
    }
    
    h1 { font-size: 3rem; margin-bottom: 1.5rem; }
    h2 { font-size: 2.25rem; margin-bottom: 1.25rem; }
    h3 { font-size: 1.75rem; margin-bottom: 1rem; }
    
    /* Hero Section - Premium Gradient with Animation */
    .hero-section {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 50%, #F093FB 100%);
        padding: 4rem 3rem;
        border-radius: var(--radius-xl);
        margin-bottom: 3rem;
        box-shadow: var(--shadow-xl), 0 0 0 1px rgba(255,255,255,0.1) inset;
        position: relative;
        overflow: hidden;
        animation: gradientShift 8s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 600px;
        height: 600px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
        filter: blur(60px);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0 0 1rem 0;
        background: linear-gradient(135deg, #FFFFFF 0%, #E0E7FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.03em;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.35rem;
        font-weight: 400;
        opacity: 0.95;
        color: rgba(255,255,255,0.95);
        max-width: 600px;
        position: relative;
        z-index: 1;
    }
    
    /* Cards - Modern Glassmorphism */
    .job-card, .info-box, .steps-box {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: var(--radius-lg);
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-lg);
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .job-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .job-card:hover {
        transform: translateY(-4px) scale(1.01);
        box-shadow: var(--shadow-xl);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    /* Buttons - Premium Styling */
    .stButton button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white !important;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: var(--shadow-md), 0 0 0 2px rgba(99, 102, 241, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg), 0 0 0 4px rgba(99, 102, 241, 0.3);
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    /* Tabs - Modern Design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.9);
        padding: 8px;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 24px !important;
        background: transparent;
        border-radius: var(--radius-md);
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-secondary);
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(99, 102, 241, 0.1);
        color: var(--primary-color);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important;
        font-weight: 700;
        box-shadow: var(--shadow-md);
        border: 2px solid var(--primary-color) !important;
    }
    
    /* Sidebar - Enhanced */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255,255,255,0.3);
        box-shadow: var(--shadow-lg);
    }
    
    /* Metrics - Premium Cards */
    .stMetric {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
        border-radius: var(--radius-md);
        padding: 1.5rem;
        border: 2px solid rgba(99, 102, 241, 0.2);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary-color);
    }
    
    /* Input Fields - Modern */
    .stTextInput > div > div,
    .stTextArea > div > div,
    .stSelectbox > div > div {
        border: 2px solid var(--border-color);
        border-radius: var(--radius-md);
        transition: all 0.3s ease;
        background: white;
    }
    
    .stTextInput > div > div:focus-within,
    .stTextArea > div > div:focus-within,
    .stSelectbox > div > div:focus-within {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
    }
    
    /* Badges - Professional */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        box-shadow: var(--shadow-sm);
    }
    
    .badge-excellent {
        background: linear-gradient(135deg, #10B981, #34D399);
        color: white;
    }
    
    .badge-good {
        background: linear-gradient(135deg, #F59E0B, #FBBF24);
        color: white;
    }
    
    /* Info Boxes - Enhanced */
    .info-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(147, 197, 253, 0.05));
        border-left: 4px solid var(--primary-color);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .info-box-title {
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.75rem;
        font-size: 1.1rem;
    }
    
    .steps-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(52, 211, 153, 0.05));
        border-left: 4px solid var(--success-color);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    /* Loading Animation - Smooth */
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    .loading-skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
        border-radius: var(--radius-md);
    }
    
    /* Footer - Professional */
    .footer {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 3rem 0 2rem 0;
        margin-top: 4rem;
        border-top: 1px solid rgba(255,255,255,0.3);
        box-shadow: var(--shadow-lg);
        border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    }
    
    /* Scrollbar - Custom */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--primary-hover), var(--secondary-color));
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem; }
        .hero-section { padding: 2rem 1.5rem; }
        .main .block-container { padding: 1rem; }
        h1 { font-size: 2rem; }
        h2 { font-size: 1.5rem; }
    }
    
    /* Smooth Transitions */
    * {
        transition: background-color 0.3s ease, color 0.3s ease, transform 0.3s ease;
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
# HERO SECTION - PREMIUM WITH ANIMATIONS
# ==========================================
st.markdown("""
<div class="hero-section">
    <div style="position: relative; z-index: 1;">
        <div style="font-size: 4rem; margin-bottom: 1rem; animation: float 3s ease-in-out infinite;">🧭</div>
        <h1 class="hero-title">Career Compass</h1>
        <p class="hero-subtitle">AI-powered tools to accelerate your career journey • 100% Free • No Signup Required</p>
        <div style="margin-top: 2rem; display: flex; gap: 1rem; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.2); padding: 0.75rem 1.5rem; border-radius: 12px; backdrop-filter: blur(10px);">
                <div style="font-weight: 700; color: white;">✨ AI-Powered</div>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 0.75rem 1.5rem; border-radius: 12px; backdrop-filter: blur(10px);">
                <div style="font-weight: 700; color: white;">🔒 Privacy-First</div>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 0.75rem 1.5rem; border-radius: 12px; backdrop-filter: blur(10px);">
                <div style="font-weight: 700; color: white;">⚡ Instant Results</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    # --- ENHANCED SESSION METRICS ---
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1)); 
                 padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; 
                 border: 2px solid rgba(99, 102, 241, 0.2);">
        <div style="font-weight: 700; color: #4F46E5; margin-bottom: 1rem; font-size: 1.1rem;">
            📊 Your Session
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 2rem; font-weight: 800; color: #6366F1; line-height: 1;">
                    {jobs_saved}
                </div>
                <div style="font-size: 0.85rem; color: #6B7280; margin-top: 0.25rem;">
                    Jobs Saved
                </div>
            </div>
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 2rem; font-weight: 800; color: #8B5CF6; line-height: 1;">
                    {searches}
                </div>
                <div style="font-size: 0.85rem; color: #6B7280; margin-top: 0.25rem;">
                    Searches
                </div>
            </div>
        </div>
    </div>
    """.format(jobs_saved=len(st.session_state.saved_jobs), searches=st.session_state.search_count), 
    unsafe_allow_html=True)
    st.divider()
    # --- END METRICS ---
    
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
        st.markdown("### 📤 Export Jobs")
        st.markdown('<p class="text-muted" style="font-size:0.85rem;">Download your saved jobs to track your applications</p>', unsafe_allow_html=True)
        
        # Prepare export data
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
        
        # CSV Download Button
        st.download_button(
            "📥 Download Jobs as CSV",
            data=csv,
            file_name="my_saved_jobs.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
        
        st.info("💡 **Tip:** Download the CSV and email it to yourself for easy tracking!")
        
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
            st.session_state.search_count += 1  # ← TRACK_SEARCH
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
# PROFESSIONAL FOOTER
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