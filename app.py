import streamlit as st
import os

st.set_page_config(
    page_title="Career Compass | Professional Outplacement Services",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Navigation Bar */
    .nav-container {
        background: white;
        padding: 1rem 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    
    .nav-links {
        display: flex;
        justify-content: center;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-link {
        color: #1e293b;
        text-decoration: none;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .nav-link:hover {
        background: #3b82f6;
        color: white;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
        padding: 5rem 2rem;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0 0 1rem 0;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        opacity: 0.95;
        margin: 0 0 2rem 0;
    }
    
    .hero-cta {
        display: inline-block;
        background: white;
        color: #3b82f6;
        padding: 1rem 2.5rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    
    .hero-cta:hover {
        transform: translateY(-3px);
    }
    
    /* Service Cards */
    .services-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .service-card {
        background: white;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-top: 4px solid #3b82f6;
        transition: transform 0.3s ease;
    }
    
    .service-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .service-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .service-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
    }
    
    .service-desc {
        color: #64748b;
        line-height: 1.6;
    }
    
    /* Section Styling */
    .section-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        color: #1e293b;
        margin: 4rem 0 2rem 0;
    }
    
    .section-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Navigation Bar
st.markdown("""
<div class="nav-container">
    <div class="nav-links">
        <a href="/" class="nav-link">🏠 Home</a>
        <a href="/Services" class="nav-link">📋 Services</a>
        <a href="/About" class="nav-link">ℹ️ About</a>
        <a href="/Contact" class="nav-link">📞 Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Welcome message
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">Welcome to Career Compass</h1>
    <p class="hero-subtitle">Professional AI-Powered Outplacement Services</p>
    <p style="font-size: 1.1rem; margin-bottom: 2rem;">Navigate your career transition with confidence</p>
</div>

<div style="max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
    <h2 class="section-title">How Can We Help You Today?</h2>
    <p class="section-subtitle">Choose from our professional services below</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 👆 Use the navigation menu above to access our services")