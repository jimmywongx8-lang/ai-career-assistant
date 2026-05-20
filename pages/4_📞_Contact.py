import streamlit as st

st.set_page_config(page_title="Contact | Career Compass", page_icon="📞")

st.markdown("""
<style>
    .contact-box {
        background: white;
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 3rem 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
    <h1 style="margin: 0; font-size: 2.5rem;">Contact Us</h1>
    <p style="margin: 1rem 0 0 0; font-size: 1.2rem;">We're here to help you succeed</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="contact-box">
        <h3>📧 Email Us</h3>
        <p style="font-size: 1.1rem; color: #64748b;">For general inquiries:</p>
        <p style="font-size: 1.2rem; font-weight: 600; color: #3b82f6;">support@careercompass.ai</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="contact-box">
        <h3>💬 Feedback</h3>
        <p style="font-size: 1.1rem; color: #64748b;">Help us improve:</p>
        <p style="font-size: 1.2rem; font-weight: 600; color: #3b82f6;">feedback@careercompass.ai</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="contact-box">
    <h3>📝 Send Us a Message</h3>
    <p style="color: #64748b;">We typically respond within 24 hours</p>
    
    With st.form("contact_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        subject = st.selectbox("Subject", ["General Inquiry", "Technical Support", "Feedback", "Other"])
        message = st.text_area("Message", height=150)
        
        submitted = st.form_submit_button("Send Message", use_container_width=True)
        
        if submitted:
            st.success("✅ Thank you for your message! We'll get back to you soon.")
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: #f0f9ff; padding: 2rem; border-radius: 15px; text-align: center; margin: 2rem 0;">
    <h3> Community Support</h3>
    <p>Join our community of professionals supporting each other through career transitions.</p>
</div>
""", unsafe_allow_html=True)