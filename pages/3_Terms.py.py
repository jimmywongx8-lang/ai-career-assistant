import streamlit as st

st.set_page_config(page_title="Terms of Service", page_icon="📜")

# CSS for consistent styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    body, .stApp { font-family: 'Inter', sans-serif; background-color: #F8FAFC; color: #1E293B; }
    .policy-content { max-width: 800px; margin: 0 auto; padding: 20px; }
    .policy-section { background: white; padding: 24px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .policy-section h3 { color: #4F46E5; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

st.title("📜 Terms of Service")

st.markdown("""
<div class="policy-content">
    <div class="policy-section">
        <h3>Community Service</h3>
        <p>Career Compass is provided as a free community service on an <strong>"As Is"</strong> basis. We make no warranties regarding the accuracy, reliability, or availability of the tools.</p>
    </div>
    
    <div class="policy-section">
        <h3>User Responsibility</h3>
        <p>You are solely responsible for your use of this platform. While our AI tools are designed to assist you, they are not a substitute for professional advice. You should always review and verify all AI-generated content (such as resumes and cover letters) before using them.</p>
    </div>
    
    <div class="policy-section">
        <h3>Use at Your Own Risk</h3>
        <p>We are not liable for any damages or losses resulting from your use of the service, including but not limited to job application outcomes. By using Career Compass, you agree to use the platform at your own risk.</p>
    </div>
    
    <div class="policy-section">
        <h3>Modifications</h3>
        <p>We reserve the right to modify or discontinue the service at any time without notice.</p>
        <p>Thank you for being part of our community!</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("Last updated: May 2026")