# modules/cv_analyzer.py
import os
import re
import streamlit as st
from groq import Groq

# Get API key from environment or secrets
def get_groq_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=get_groq_key())

def analyze_cv(cv_text):
    """Analyze CV and extract key information"""
    
    prompt = f"""Analyze this CV and extract the following information in JSON format:
    - current_sector
    - seniority_level  
    - top_5_skills
    
    CV Text:
    {cv_text}
    
    Return ONLY valid JSON like this:
    {{
        "current_sector": "sector name",
        "seniority_level": "level",
        "top_5_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"]
    }}
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        
        import json
        result = response.choices[0].message.content
        return json.loads(result)
    except Exception as e:
        return {
            "current_sector": "Unknown",
            "seniority_level": "Unknown",
            "top_5_skills": []
        }