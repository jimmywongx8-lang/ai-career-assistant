import streamlit as st

st.set_page_config(page_title="Home | Career Compass", page_icon="🏠")

st.markdown("""
<style>
    .feature-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 5px solid #0284c7;
    }
    
    .stat-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        color: #0284c7;
        margin: 0;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 4rem 2rem; border-radius: 20px; color: white; text-align: center; margin-bottom: 3rem;">
    <h1 style="font-size: 3rem; margin: 0;">🚀 Transform Your Career</h1>
    <p style="font-size: 1.3rem; margin: 1rem 0;">AI-powered outplacement services for the modern professional</p>
</div>
""", unsafe_allow_html=True)

# Features
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>🎯 Smart Matching</h3>
        <p>AI analyzes your CV and matches you with perfect job opportunities</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>✍️ Tailored Content</h3>
        <p>Customized CVs and cover letters for each application</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box">
        <h3>🔒 Privacy First</h3>
        <p>Your data is secure and never shared with third parties</p>
    </div>
    """, unsafe_allow_html=True)

# Stats Section
st.markdown("<h2 style='text-align: center; margin: 4rem 0 2rem 0;'>Why Choose Career Compass?</h2>", unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown('<div class="stat-card"><p class="stat-number">100%</p><p class="stat-label">Free Service</p></div>', unsafe_allow_html=True)
with s2:
    st.markdown('<div class="stat-card"><p class="stat-number">AI</p><p class="stat-label">Powered</p></div>', unsafe_allow_html=True)
with s3:
    st.markdown('<div class="stat-card"><p class="stat-number">24/7</p><p class="stat-label">Available</p></div>', unsafe_allow_html=True)
with s4:
    st.markdown('<div class="stat-card"><p class="stat-number">Privacy</p><p class="stat-label">Guaranteed</p></div>', unsafe_allow_html=True)

# CTA Section
st.markdown("""
<div style="background: #f8fafc; padding: 4rem 2rem; border-radius: 20px; text-align: center; margin: 4rem 0;">
    <h2 style="color: #1e293b; font-size: 2.5rem;">Ready to Get Started?</h2>
    <p style="color: #64748b; font-size: 1.2rem; margin: 1rem 0;">Upload your CV and let AI help you land your dream job</p>
    <a href="/Services" style="display: inline-block; background: #3b82f6; color: white; padding: 1rem 3rem; border-radius: 50px; text-decoration: none; font-weight: 700; margin-top: 1rem;">Explore Services →</a>
</div>
""", unsafe_allow_html=True)