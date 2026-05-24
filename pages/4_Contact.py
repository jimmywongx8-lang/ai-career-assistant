import streamlit as st

st.set_page_config(page_title="Contact Us", page_icon="📬")

st.title("📬 Contact Us")

st.markdown("### Get in Touch")
st.write("We value your feedback! Whether you have a feature request, found a bug, or just want to share your success story, we'd love to hear from you.")

st.markdown("### How to Reach Us")
st.markdown("- **Email:** info@careeraisupport.org")
st.markdown("- **Feedback Form:** Please use the form below to send us a message directly.")
st.write("We strive to respond to all inquiries within 48 hours. Thank you for being part of our community!")

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