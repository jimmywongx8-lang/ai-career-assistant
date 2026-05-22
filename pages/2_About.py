import streamlit as st

st.set_page_config(page_title="About", page_icon="ℹ️")

# --- STYLING ---
st.markdown("""
<style>
    .story-box {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin: 1.5rem 0;
        line-height: 1.8;
    }
    .mission-header {
        color: #1e3a8a;
        font-size: 2rem;
        font-weight: 700;
        margin-top: 2rem;
    }
    .sub-header {
        color: #334155;
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    .highlight-text {
        color: #1e293b;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- CONTENT ---
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem;">
    <h1 style="font-size: 2.5rem; color: #1e3a8a;">Our Story</h1>
    <p style="font-size: 1.2rem; color: #64748b;">Built by professionals, for professionals.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="story-box">
    <p class="highlight-text">
        Career Compass was created by a small group of professionals in their 50s who personally experienced the difficulties and frustrations of job searching later in their careers.
    </p>
    <p>
        After facing repeated challenges navigating today’s hiring landscape, we realized how many people — especially those in-between jobs or transitioning due to changing circumstances — are left without affordable, practical support.
    </p>
    <p>
        From that shared experience, we built a simple AI-powered tool designed to help others in similar situations. Our goal is to make career support more accessible, especially for individuals who may not have access to expensive outplacement services or dedicated career coaching.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🎯 Our Mission")
st.write("Our mission remains simple — to support job seekers with practical, AI-powered tools that are accessible to everyone.")

st.divider()

# --- STATUS & PRIVACY ---
col1, col2 = st.columns(2)

with col1:
    st.info("🚧 **Beta Version:** We are actively improving the platform and will continue to add useful features based on real community feedback.")

with col2:
    st.success("🔒 **Privacy First:** CVs and personal data are processed locally on your device and are not stored on our servers.")

st.divider()

st.markdown("""
<small style="color: #94a3b8;">
*The service is provided free of charge. To help sustain and further develop the platform, we may include affiliate links in the future, which may generate small commissions at no additional cost to users.
</small>
""", unsafe_allow_html=True)
