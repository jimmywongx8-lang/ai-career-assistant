import streamlit as st

st.set_page_config(page_title="Contact", page_icon="📞")

st.title("📞 Contact Us")

st.markdown("""
### 📧 Get In Touch

We'd love to hear from you!

**Email:** career.aisupport@gmail.com  
**Response Time:** Within 24 hours
""")

with st.form("contact_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    subject = st.selectbox("Subject", ["General Inquiry", "Technical Support", "Feedback", "Other"])
    message = st.text_area("Message", height=150)
    
    submitted = st.form_submit_button("Send Message", use_container_width=True)
    
    if submitted:
        st.success("✅ Thank you for your message! We'll get back to you soon.")

st.markdown("""
### 💬 Community Support

Join our community of professionals supporting each other through career transitions.
""")