import streamlit as st
import os
import sys
from urllib.parse import quote

st.set_page_config(
    page_title="Career Compass | Home",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS
st.markdown("""
<style>
    .hero-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 4rem 2rem;
        text-align: center;
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    .hero-title { font-size: 3rem; margin-bottom: 1rem; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="hero-box">
    <h1 class="hero-title">Welcome to Career Compass</h1>
    <p style="font-size: 1.3rem">Professional AI-Powered Outplacement Services</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### How It Works")
st.markdown("Career Compass helps you navigate your career transition with AI-powered tools:")
st.markdown("- **Services Page** - Upload your CV, get analyzed, find jobs