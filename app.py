import streamlit as st

# --- PAGE CONFIGURATION ---
# 'expanded' forces the sidebar to be open by default
st.set_page_config(
    page_title="Career Compass",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
st.markdown("""
<style>
    /* Hero Section Style */
    .hero-section {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 60px 20px;
        text-align: center;
        color: white;
        border-radius: 20px;
        margin-bottom: 40px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .hero-title {
        font-size: 3rem;
        margin: 0;
        font-weight: 800;
    }
    .hero-subtitle {
        font-size: 1.3rem;
        margin: 10px 0 0 0;
        opacity: 0.9;
    }
    /* Sidebar Style */
    [data-testid="stSidebar"] {
        width: 250px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HERO BANNER ---
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">Welcome to Career Compass</h1>
    <p class="hero-subtitle">Professional AI-Powered Outplacement Services</p>
</div>
""", unsafe_allow_html=True)

# --- INSTRUCTIONS ---
st.header("👈 Please use the Sidebar on the left to navigate.")

st.markdown("""
**How to get started:**

1.  **Services** - Upload your CV, analyze your profile, and find matching jobs.
2.  **About** - Learn about our mission to help professionals transition careers.
3.  **Contact** - Get in touch with our support team.
""")

st.divider()

st.info("⚠️ **Note:** If you don't see the sidebar, click the little arrow icon in the top-left corner to expand the menu.")