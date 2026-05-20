import streamlit as st

st.set_page_config(
    page_title="Career Compass",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
.hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    padding: 60px 20px;
    text-align: center;
    color: white;
    border-radius: 20px;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>Welcome to Career Compass</h1><p>Professional AI-Powered Outplacement Services</p></div>', unsafe_allow_html=True)

st.header("How It Works")
st.write("1. Go to **Services** page (left sidebar)")
st.write("2. Upload your CV")
st.write("3. Get AI analysis and job matches")
st.write("4. Generate tailored CV and cover letter")

st.divider()
st.write("👈 **Use the sidebar on the left to navigate**")