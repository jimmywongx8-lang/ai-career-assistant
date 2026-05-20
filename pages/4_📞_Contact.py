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
    <h1 style="margin:0">📞 Contact Us</h1>
    <p style="margin:0.5rem 0 0 0">We'd love to hear from you</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#f8fafc; padding:2rem; border-radius:12px; border:1px solid #e2e8f0; margin-bottom:2rem;">
    <h3>📧 Email Support</h3>
    <p style="color:#64748b">For technical issues or inquiries:</p>
    <p style="font-weight:700; color:#3b82f6">support@careercompass.ai</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 💬 Send a Message")
with st.form("contact"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    msg = st.text_area("Message")
    submit = st.form_submit_button("Send")
    
    if submit:
        st.success("✅ Thanks! We'll get back to you soon.")