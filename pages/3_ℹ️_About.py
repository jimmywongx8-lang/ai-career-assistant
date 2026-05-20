import streamlit as st

# --- NAVIGATION BAR ---
st.markdown("""<style>.nav-bar{background:white;padding:15px 20px;box-shadow:0 2px 10px rgba(0,0,0,0.1);display:flex;justify-content:center;gap:2rem;margin-bottom:2rem;border-radius:8px;}</style>""", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1: st.page_link("app.py", label="🏠 Home")
with col2: st.page_link("pages/1_🏠_Home.py", label="📋 Services")
with col3: st.page_link("pages/3_ℹ️_About.py", label="ℹ️ About")
with col4: st.page_link("pages/4_📞_Contact.py", label=" Contact")

st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
    <h1 style="margin:0">ℹ️ About Us</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
### 🎯 Our Mission
We believe career transitions are challenging enough without expensive agencies. 
**Career Compass** is a community-driven project to provide **free, privacy-first AI support** for outplacement.

### 🌟 What We Do
- **CV Analysis**: Instant insights into your profile.
- **Smart Matching**: Find jobs that fit your skills.
- **Tailored Applications**: Auto-generated CVs and letters.

###  Why We Built This
We want to level the playing field. High-quality career support should be accessible to everyone, not just executives at top firms.
""")

st.markdown("---")
st.markdown("### 📧 Have Questions?")
st.info("Visit our Contact page to get in touch!")