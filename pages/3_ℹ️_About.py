import streamlit as st

st.set_page_config(page_title="About | Career Compass", page_icon="ℹ️")

st.markdown("""
<style>
    .about-section {
        background: white;
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 2rem 0;
    }
    
    .mission-box {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        color: white;
        padding: 3rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 3rem 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
    <h1 style="margin: 0; font-size: 2.5rem;">About Career Compass</h1>
    <p style="margin: 1rem 0 0 0; font-size: 1.2rem;">Empowering professionals through AI-driven career support</p>
</div>
""")

st.markdown("""
<div class="mission-box">
    <h2>🎯 Our Mission</h2>
    <p style="font-size: 1.2rem; line-height: 1.6;">To provide free, high-quality AI-powered outplacement services to everyone, ensuring no one faces career transitions alone.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-section">
    <h2>🌟 What We Offer</h2>
    <ul style="font-size: 1.1rem; line-height: 2;">
        <li>✅ <strong>AI-Powered CV Analysis</strong> - Get instant insights into your profile</li>
        <li>✅ <strong>Smart Job Matching</strong> - Find positions that truly fit your skills</li>
        <li>✅ <strong>Tailored Application Materials</strong> - Custom CVs and cover letters</li>
        <li>✅ <strong>100% Free</strong> - No hidden fees, ever</li>
        <li>✅ <strong>Privacy First</strong> - Your data stays secure</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-section">
    <h2>💡 Why We Built This</h2>
    <p style="font-size: 1.1rem; line-height: 1.8;">
        Career transitions are challenging. Traditional outplacement services are expensive and inaccessible to many. 
        We believe everyone deserves access to professional career support, regardless of their budget.
    </p>
    <p style="font-size: 1.1rem; line-height: 1.8; margin-top: 1rem;">
        By leveraging cutting-edge AI technology, we've created a platform that delivers enterprise-level 
        career support to anyone, anywhere, completely free.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: #f0f9ff; padding: 3rem; border-radius: 15px; text-align: center; margin: 2rem 0;">
    <h2>📧 Get In Touch</h2>
    <p style="font-size: 1.1rem;">Have questions or feedback? We'd love to hear from you!</p>
    <a href="/Contact" style="display: inline-block; background: #3b82f6; color: white; padding: 1rem 2rem; border-radius: 50px; text-decoration: none; font-weight: 700; margin-top: 1rem;">Contact Us →</a>
</div>
""", unsafe_allow_html=True)