# modules/cv_analyzer.py
import os
import re
import json
import streamlit as st
from groq import Groq

def get_groq_key():
    """Get API key from Streamlit secrets or environment"""
    try:
        # Try Streamlit Cloud secrets first
        if hasattr(st, 'secrets') and "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception as e:
        print(f"Error reading secrets: {e}")
    
    # Fallback to environment variable
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    
    return None

def analyze_cv(cv_text):
    """Analyze CV and extract key information"""
    
    # Get API key
    api_key = get_groq_key()
    if not api_key:
        st.error("❌ API key not found!")
        return {
            "current_sector": "Unknown",
            "seniority_level": "Unknown", 
            "top_5_skills": []
        }
    
    try:
        client = Groq(api_key=api_key)
        
        prompt = f"""Analyze this CV and extract the following information.
Return ONLY a valid JSON object in this exact format:

{{
    "current_sector": "sector name or Unknown",
    "seniority_level": "level or Unknown",
    "top_5_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"]
}}

CV Text:
{cv_text[:2000]}

JSON Response:"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result