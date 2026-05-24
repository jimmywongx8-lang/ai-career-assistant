import streamlit as st

st.set_page_config(page_title="Contact Us", page_icon="📬")

# CSS for consistent styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    body, .stApp { font-family: 'Inter', sans-serif; background-color: #F8FAFC; color: #1E293B; }
    .contact-content { max-width: 800px; margin: 0 auto; padding: 20px; }
    .contact-section { background: white; padding: 24px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .contact-section h3 { color: #4F46E5; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

st.title("📬 Contact Us")

st.markdown("""
<div class="contact-content">
    <div class="contact-section">
        <h3>Get in Touch</h3>
        <p>We value your feedback! Whether you have a feature request, found a bug, or just want to share your success story, we'd love to hear from you.</p>
    </div>
    
    <div class="contact-section">
        <h3>How to Reach Us</h3>
        <ul>
            <li><strong>Email:</strong> <a href="mailto:career.aisupport@gmail.com">career.aisupport@gmail.com</a></li>
            <li><strong>Feedback Form:</strong> Please use the form below to send us a message directly.</li>
        </ul>
        <p>We strive to respond to all inquiries within 48 hours. Thank you for being part of our community!</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

with st.form("contact_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Name *")
    with col2:
        email = st.text_input("Your Email *")
    
    subject = st.text_input("Subject")
    message = st.text_area("Message *", height=150, placeholder="How can we help you?")
    
    submitted = st.form_submit_button("🚀 Send Message")
    
    if submitted:
        if name and email and message:
            st.success(f"Thank you, {name}! Your message has been received. We will respond to {email} within 48 hours.")
        else:
            st.warning("Please fill in all required fields (marked with *).")