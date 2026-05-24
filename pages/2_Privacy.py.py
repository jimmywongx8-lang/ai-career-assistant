import streamlit as st

st.set_page_config(page_title="Privacy Policy", page_icon="🔒")

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

st.title("🔒 Privacy Policy")

st.markdown("""
<div class="policy-content">
    <div class="policy-section">
        <h3>Your Privacy is Our Priority</h3>
        <p>At <strong>Career Compass</strong>, we are committed to protecting your personal information. We believe that your data belongs to you, not us.</p>
    </div>
    
    <div class="policy-section">
        <h3>Community Project</h3>
        <p>We are a community-driven project dedicated to helping job seekers. We do not sell, trade, or rent your personal data to third parties for marketing purposes.</p>
    </div>
    
    <div class="policy-section">
        <h3>No Permanent Data Storage</h3>
        <p>We respect your privacy by not storing your sensitive data.</p>
        <ul>
            <li><strong>Real-Time Processing:</strong> Your CV and job preferences are processed in real-time by our AI engine to generate insights.</li>
            <li><strong>Session Only:</strong> Data is held temporarily in your browser session to enable the app's functionality. Once you refresh or close the app, your session data is cleared. We do not retain copies of your CV on our servers.</li>
        </ul>
    </div>
    
    <div class="policy-section">
        <h3>AI Processing</h3>
        <p>Your input is sent to third-party AI providers solely for the purpose of processing your specific request. These providers adhere to their own strict privacy standards.</p>
    </div>
    
    <div class="policy-section">
        <h3>Changes to This Policy</h3>
        <p>We may update this policy as our community project evolves. We encourage you to review this page periodically.</p>
        <p>If you have questions, please reach out via our <a href="/Contact">Contact page</a>.</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("Last updated: May 2026")