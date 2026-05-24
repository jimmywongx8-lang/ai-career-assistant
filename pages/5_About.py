import streamlit as st

st.set_page_config(page_title="About Our Services", page_icon="📖")

# CSS for consistent styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    body, .stApp { font-family: 'Inter', sans-serif; background-color: #F8FAFC; color: #1E293B; }
    .about-content { max-width: 800px; margin: 0 auto; padding: 20px; }
    .service-card { background: white; padding: 24px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-left: 4px solid #4F46E5; }
    .service-card h3 { color: #4F46E5; margin-top: 0; display: flex; align-items: center; gap: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("📖 About Our Services")

st.markdown('<div class="about-content">', unsafe_allow_html=True)

st.markdown("""
<p style="font-size: 1.1rem; color: #64748B; margin-bottom: 30px;">
    Learn more about how Career Compass helps you navigate your career journey.
</p>
""", unsafe_allow_html=True)

st.markdown("""
<div class="service-card">
    <h3>💼 Job Matching</h3>
    <p>Finding the right role shouldn't be a guessing game. Our AI scans thousands of live job listings to identify positions that genuinely match your unique skill set and experience. It calculates a relevance score for every result, ensuring you spend your time applying to high-potential opportunities rather than endless searching.</p>
</div>

<div class="service-card">
    <h3>🔍 CV Analysis</h3>
    <p>Think of this as your personal career coach. Our AI analyzes your uploaded resume to provide an objective assessment of your professional profile. It identifies your core strengths, highlights potential skill gaps, and suggests target job titles based on your background, helping you understand your true market value.</p>
</div>

<div class="service-card">
    <h3>✨ CV Optimization</h3>
    <p>Tailor your resume for the specific roles you want. Our optimization tool takes your existing CV and a target job description, then intelligently rewrites your content to highlight the most relevant keywords and experiences. This helps your application stand out and pass automated screening systems.</p>
</div>

<div class="service-card">
    <h3>📧 Cover Letter Generator</h3>
    <p>Stop struggling with the blank page. Our AI generates professional, personalized cover letter drafts in seconds. It connects your specific achievements to the employer's needs, ensuring a perfect tone and focus that saves you hours of writing time.</p>
</div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("Career Compass — A Community Project")