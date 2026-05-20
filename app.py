import streamlit as st

st.set_page_config(
    page_title="Career Compass | AI Outplacement",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS for styling
st.markdown("""
<style>
    /* Navigation Bar */
    .nav-bar {
        background: white;
        padding: 15px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 2rem;
        border-radius: 8px;
    }
    
    /* Hero Section */
    .hero-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 4rem 2rem;
        text-align: center;
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    
    .hero-title { font-size: 3rem; margin-bottom: 1rem; font-weight: 800; }
    .hero-sub { font-size: 1.2rem; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# --- NAVIGATION BAR ---
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1: st.page_link("app.py", label="🏠 Home")
with col2: st.page_link("pages/1_🏠_Home.py", label=" Services")
with col3: st.page_link("pages/3_ℹ️_About.py", label="ℹ️ About")
with col4: st.page_link("pages/4_📞_Contact.py", label="📞 Contact")

# --- MAIN CONTENT ---
st.markdown("""
<div class="hero-box">
    <h1 class="hero-title">🚀 Welcome to Career Compass</h1>
    <p class="hero-sub">Professional AI-Powered Outplacement Services</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align:center;'><h2>How Can We Help You?</h2></div>", unsafe_allow_html=True)

st.markdown("""
<div style='display:grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; text-align:center; margin-top: 2rem;'>
    <div style='background:#f8fafc; padding:2rem; border-radius:12px; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>
        <div style='font-size:3rem;'>🎯</div>
        <h3>Smart Matching</h3>
        <p style='color:#64748b'>Find jobs that match your unique skills</p>
    </div>
    <div style='background:#f8fafc; padding:2rem; border-radius:12px; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>
        <div style='font-size:3rem;'>✍️</div>
        <h3>Tailored Content</h3>
        <p style='color:#64748b'>Custom CVs and cover letters</p>
    </div>
    <div style='background:#f8fafc; padding:2rem; border-radius:12px; box-shadow:0 4px 6px rgba(0,0,0,0.05);'>
        <div style='font-size:3rem;'>🔒</div>
        <h3>Privacy First</h3>
        <p style='color:#64748b'>Secure and private processing</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 👆 Use the menu above to access our services")