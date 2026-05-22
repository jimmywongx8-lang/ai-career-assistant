import streamlit as st
import requests

st.set_page_config(page_title="Contact", page_icon="📞")

st.title("📞 Contact Us")

st.markdown("""
### 📧 Get In Touch

We'd love to hear from you!

**Email:** career.aisupport@gmail.com  
**Response Time:** Within 24 hours
""")

# Formspree endpoint
FORMSPREE_ENDPOINT = "https://formspree.io/f/mojbdgaz"

with st.form("contact_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    subject = st.selectbox("Subject", ["General Inquiry", "Technical Support", "Feedback", "Other"])
    message = st.text_area("Message", height=150)
    
    submitted = st.form_submit_button("Send Message", use_container_width=True)
    
    if submitted:
        # Manual validation
        if not name or not email or not message:
            st.error("❌ Please fill in all required fields (Name, Email, and Message).")
        elif "@" not in email:
            st.error("❌ Please enter a valid email address.")
        else:
            try:
                response = requests.post(
                    FORMSPREE_ENDPOINT,
                    json={
                        "name": name,
                        "email": email,
                        "subject": subject,
                        "message": message
                    },
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code == 200:
                    st.success("✅ Message sent successfully! We'll get back to you within 24 hours.")
                else:
                    st.error("❌ Something went wrong. Please try emailing us directly at career.aisupport@gmail.com")
                    
            except Exception as e:
                st.error("❌ Error sending message. Please email us directly at career.aisupport@gmail.com")

st.markdown("---")
st.markdown("""
### 💬 Community Support

Join our community of professionals supporting each other through career transitions.
""")