import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

# Temporarily disable JSearch import
# from modules.jsearch_client import JSearchClient
JSearchClient = None

st.set_page_config(page_title="Services - Career Compass", page_icon="🛠️", layout="wide")

st.title("🛠️ Career Services")
st.markdown("AI-powered tools to accelerate your career journey")

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 CV Upload", 
    "🔍 AI Profile Analysis", 
    "💼 Job Matching",
    "✍️ CV Rewriting",
    "📧 Cover Letter"
])

with tab1:
    st.header("📄 Upload Your CV")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])
    
    if uploaded_file is not None:
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        
        try:
            if uploaded_file.type == "application/pdf":
                import PyPDF2
                from io import BytesIO
                pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
                cv_text = ""
                for page in pdf_reader.pages:
                    cv_text += page.extract_text()
            else:
                cv_text = uploaded_file.read().decode("utf-8")
            
            st.session_state.cv_text = cv_text
            st.session_state.user_profile["cv_uploaded"] = True
            
            with st.expander("📋 View CV Preview"):
                st.text_area("CV Content", cv_text, height=300)
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.header("🔍 AI Profile Analysis")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        if st.button("Analyze My Profile", type="primary"):
            with st.spinner("🤖 Analyzing..."):
                try:
                    from groq import Groq
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    prompt = f"Analyze this CV:\n{st.session_state.cv_text[:3000]}"
                    
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=500
                    )
                    
                    st.success("✅ Analysis Complete!")
                    st.markdown(response.choices[0].message.content)
                    st.session_state.user_profile["analyzed"] = True
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

with tab3:
    st.header("💼 Job Matching")
    st.info("Job matching will be enabled soon. For now, use the other features!")

with tab4:
    st.header("✍️ CV Rewriting")
    st.info("Coming soon!")

with tab5:
    st.header("📧 Cover Letter")
    st.info("Coming soon!")