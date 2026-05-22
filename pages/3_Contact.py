import streamlit as st
import requests
import json

st.set_page_config(page_title="Contact", page_icon="📞")

st.title("📞 Contact Us")

st.markdown("""
### 📧 Get In Touch

We'd love to hear from you!

**Email:** career.aisupport@gmail.com  
**Response Time:** Within 24 hours
""")

# Contact Form using FormSubmit.co
with st.form("contact_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    subject = st.selectbox("Subject", ["General Inquiry", "Technical Support", "Feedback", "Other"])
    message = st.text_area("Message", height=150)
    
    submitted = st.form_submit_button("Send Message", use_container_width=True)
    
    if submitted:
        if not name or not email or not message:
            st.error("❌ Please fill in all required fields.")
        else:
            try:
                # Send to FormSubmit.co
                response = requests.post(
                    "https://formsubmit.co/career.aisupport@gmail.com",
                    data={
                        "name": name,
                        "email": email,
                        "subject": subject,
                        "message": message,
                        "_next": "https://ai-career-assistant-eijldwuwtjy9dmubh3ktqh.streamlit.app",  # Redirect back to app
                        "_template": "table"
                    },
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code == 200:
                    st.success("✅ Message sent successfully! We'll get back to you within 24 hours.")
                else:
                    st.error("❌ Something went wrong. Please try emailing us directly at career.aisupport@gmail.com")
                    
            except Exception as e:
                st.error(f"❌ Error sending message. Please email us directly at career.aisupport@gmail.com")
                st.write(f"Error details: {e}")

st.markdown("---")
st.markdown("""
### 💬 Community Support

Join our community of professionals supporting each other through career transitions.
""")

