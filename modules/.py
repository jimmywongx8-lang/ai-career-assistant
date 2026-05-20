# app.py
import streamlit as st
import os
import sys
import time
from datetime import datetime

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from cv_parser import extract_text_from_file
from cv_analyzer import analyze_cv
from job_matcher import find_matching_jobs
from cv_rewriter import rewrite_cv
from cover_letter import generate_cover_letter

# PDF Generation Function (Fixed & Robust)
def create_pdf(text_content, title="Document"):
    """Create a reliable PDF using fpdf2"""
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Title
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, title, align="C")
        pdf.ln(12)
        
        # Content
        pdf.set_font("Helvetica", size=11)
        # Clean text for PDF encoding
        clean_text = text_content.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, clean_text)
        
        # Return as bytes
        return pdf.output().encode('utf-8')
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        return text_content.encode('utf-8')

# Custom CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .success-card {
        background: #ecfdf5;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
    }
    
    .metric-value {
        font-size: 1.25rem;
        color: #1e293b;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Page config
st.set_page_config(
    page_title="AI Outplacement Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Header
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 2rem; 
            border-radius: 15px; 
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);'>
    <h1 style='color: white; margin: 0; font-size: 2.5rem;'>🚀 AI Outplacement Assistant</h1>
    <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
        Free, privacy-first AI for career transitions
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize session states
if 'cv_text' not in st.session_state:
    st.session_state.cv_text = None
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'matches' not in st.session_state:
    st.session_state.matches = None
if 'selected_job' not in st.session_state:
    st.session_state.selected_job = None
if 'rewritten_cv' not in st.session_state:
    st.session_state.rewritten_cv = None
if 'cover_letter' not in st.session_state:
    st.session_state.cover_letter = None

# Reset function
def reset_app():
    st.session_state.cv_text = None
    st.session_state.analysis = None
    st.session_state.matches = None
    st.session_state.selected_job = None
    st.session_state.rewritten_cv = None
    st.session_state.cover_letter = None
    st.rerun()

# Progress tracker
def show_progress(step):
    steps = ["Upload CV", "Analyze CV", "Find Jobs", "Tailor CV", "Cover Letter"]
    progress = (step + 1) / len(steps)
    st.progress(progress)
    st.caption(f"Step {step + 1} of {len(steps)}: {steps[step]}")

# --- Top Reset Button ---
if st.session_state.cv_text or st.session_state.analysis:
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🔄 Reset App", use_container_width=True, key="reset_btn_top"):
            reset_app()

# --- Step 1: Upload CV ---
st.markdown('<div class="section-header">📄 Step 1: Upload Your CV</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a PDF or DOCX file",
    type=['pdf', 'docx'],
    help="Upload your current CV/resume",
    label_visibility="collapsed",
    key="cv_uploader"
)

if uploaded_file is not None and st.session_state.cv_text is None:
    with st.spinner("📖 Reading your CV..."):
        progress_bar = st.progress(0)
        time.sleep(0.5)
        progress_bar.progress(50)
        
        save_path = os.path.join("data", "temp_cv." + uploaded_file.name.split('.')[-1])
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        time.sleep(0.5)
        progress_bar.progress(100)
        
        st.session_state.cv_text = extract_text_from_file(save_path)
        st.success("✅ CV loaded successfully!")
        st.rerun()

if uploaded_file:
    st.info(f"📄 **File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

st.divider()

# --- Step 2: Analyze CV ---
st.markdown('<div class="section-header">🔍 Step 2: Analyze Your CV</div>', unsafe_allow_html=True)

if st.session_state.cv_text:
    show_progress(1)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        analyze_btn = st.button("✨ Analyze CV", use_container_width=True, key="analyze_btn")
    
    if analyze_btn:
        with st.spinner("🤖 AI is analyzing your profile..."):
            progress_bar = st.progress(0)
            time.sleep(0.3)
            progress_bar.progress(30)
            
            try:
                result = analyze_cv(st.session_state.cv_text)
                time.sleep(0.3)
                progress_bar.progress(70)
                
                st.session_state.analysis = result
                time.sleep(0.4)
                progress_bar.progress(100)
                
                st.success("✅ Analysis complete!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.session_state.analysis = None
    
    if st.session_state.analysis:
        st.markdown('<div class="success-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-label">Sector</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{st.session_state.analysis.get("current_sector", "N/A")}</div>', 
                       unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-label">Level</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{st.session_state.analysis.get("seniority_level", "N/A").title()}</div>', 
                       unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-label">Top Skills</div>', unsafe_allow_html=True)
            skills = st.session_state.analysis.get('top_5_skills', [])
            skills_text = ', '.join(skills[:3]) if skills else 'N/A'
            st.markdown(f'<div class="metric-value" style="font-size: 1rem;">{skills_text}</div>', 
                       unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        weaknesses = st.session_state.analysis.get('cv_weaknesses', [])
        if weaknesses:
            st.markdown("### 💡 Areas for Improvement")
            for i, weakness in enumerate(weaknesses, 1):
                st.warning(f"{i}. {weakness}")
        
        pivots = st.session_state.analysis.get('recommended_pivot_sectors', [])
        if pivots:
            st.markdown("### 🎯 Recommended Career Pivots")
            cols = st.columns(len(pivots))
            for i, sector in enumerate(pivots):
                with cols[i]:
                    st.info(f"• {sector}")
else:
    st.info("👆 Please upload your CV in Step 1 to begin analysis")

st.divider()

# --- Step 3: Find Matching Jobs ---
st.markdown('<div class="section-header"> Step 3: Find Matching Jobs</div>', unsafe_allow_html=True)

if st.session_state.cv_text:
    show_progress(2)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        search_btn = st.button("🔍 Search Jobs", use_container_width=True, key="search_btn")
    
    if search_btn:
        with st.spinner("🔎 Searching for opportunities..."):
            progress_bar = st.progress(0)
            time.sleep(0.3)
            progress_bar.progress(40)
            
            try:
                matches = find_matching_jobs(st.session_state.cv_text, num_matches=3)
                st.session_state.matches = matches
                
                time.sleep(0.4)
                progress_bar.progress(100)
                
                if matches:
                    st.success(f"✅ Found {len(matches)} matching jobs!")
                else:
                    st.warning("No matches found")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    if st.session_state.matches and len(st.session_state.matches) > 0:
        st.markdown("### 💼 Select a Job to Target")
        
        job_options = []
        for m in st.session_state.matches:
            label = f"{m['title']} at {m['company']} ({m['location']})"
            job_options.append(label)
        
        selected = st.selectbox(
            "Choose your target position:",
            job_options,
            label_visibility="collapsed",
            key="job_selectbox"
        )
        
        if selected:
            idx = job_options.index(selected)
            st.session_state.selected_job = st.session_state.matches[idx]
            
            st.markdown(f"""
            <div class='info-card'>
                <h3 style='margin: 0 0 0.5rem 0; color: #667eea;'>🎯 {st.session_state.selected_job['title']}</h3>
                <p style='margin: 0; color: #64748b;'>
                    <strong>Company:</strong> {st.session_state.selected_job['company']} | 
                    <strong>Location:</strong> {st.session_state.selected_job['location']}
                </p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("👆 Please upload your CV in Step 1 first")

st.divider()

# --- Step 4: Rewrite CV ---
st.markdown('<div class="section-header">📝 Step 4: Tailor Your CV</div>', unsafe_allow_html=True)

if st.session_state.cv_text and st.session_state.selected_job:
    show_progress(3)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        rewrite_btn = st.button("✏️ Rewrite CV", use_container_width=True, key="rewrite_btn")
    
    if rewrite_btn:
        with st.spinner("✍️ Tailoring your CV..."):
            progress_bar = st.progress(0)
            time.sleep(0.3)
            progress_bar.progress(30)
            
            try:
                result = rewrite_cv(
                    st.session_state.cv_text,
                    st.session_state.selected_job['title'],
                    st.session_state.selected_job.get('description', '')
                )
                st.session_state.rewritten_cv = result
                
                time.sleep(0.4)
                progress_bar.progress(100)
                st.success("✅ CV tailored successfully!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    if st.session_state.rewritten_cv:
        st.markdown("### ✨ Your Tailored CV")
        st.markdown(st.session_state.rewritten_cv)
        
        # Generate PDF
        pdf_title = f"Tailored CV - {st.session_state.selected_job['title']}"
        pdf_data = create_pdf(st.session_state.rewritten_cv, pdf_title)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Download as TXT",
                data=st.session_state.rewritten_cv,
                file_name=f"tailored_cv_{st.session_state.selected_job['company'].replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_cv_txt"
            )
        
        with col2:
            st.download_button(
                label=" Download as PDF",
                data=pdf_data,
                file_name=f"tailored_cv_{st.session_state.selected_job['company'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_cv_pdf"
            )
else:
    st.info("👆 Please complete Steps 1-3 first")

st.divider()

# --- Step 5: Cover Letter ---
st.markdown('<div class="section-header">✉️ Step 5: Generate Cover Letter</div>', unsafe_allow_html=True)

if st.session_state.cv_text and st.session_state.selected_job:
    show_progress(4)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        cover_btn = st.button("📄 Generate Letter", use_container_width=True, key="cover_btn")
    
    if cover_btn:
        with st.spinner("✍️ Writing your cover letter..."):
            progress_bar = st.progress(0)
            time.sleep(0.3)
            progress_bar.progress(40)
            
            try:
                result = generate_cover_letter(
                    st.session_state.cv_text,
                    st.session_state.selected_job['title'],
                    st.session_state.selected_job.get('description', '')
                )
                st.session_state.cover_letter = result
                
                time.sleep(0.4)
                progress_bar.progress(100)
                st.success("✅ Cover letter generated!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    if st.session_state.cover_letter:
        st.markdown("### 📄 Your Cover Letter")
        st.markdown(st.session_state.cover_letter)
        
        # Generate PDF
        pdf_title = f"Cover Letter - {st.session_state.selected_job['title']}"
        pdf_data = create_pdf(st.session_state.cover_letter, pdf_title)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Download as TXT",
                data=st.session_state.cover_letter,
                file_name=f"cover_letter_{st.session_state.selected_job['company'].replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_cl_txt"
            )
        
        with col2:
            st.download_button(
                label="📄 Download as PDF",
                data=pdf_data,
                file_name=f"cover_letter_{st.session_state.selected_job['company'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_cl_pdf"
            )
else:
    st.info("👆 Please complete Steps 1-3 first")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #94a3b8; font-size: 0.875rem;'>
    <p> <strong>Your privacy matters:</strong> All data is processed locally on your device. 
    No uploads, no storage, no tracking.</p>
    <p style='margin-top: 0.5rem;'>Built with ❤️ using Streamlit & Groq</p>
</div>
""", unsafe_allow_html=True)