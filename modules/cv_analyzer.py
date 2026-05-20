import os
import re
import json
import streamlit as st
from groq import Groq

def get_groq_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except:
        pass
    
    return os.getenv("GROQ_API_KEY")

def analyze_cv(cv_text):
    api_key = get_groq_key()
    if not api_key:
        return {
            "current_sector": "Unknown",
            "seniority_level": "Unknown", 
            "top_5_skills": []
        }
    
    try:
        client = Groq(api_key=api_key)
        
        prompt = """Analyze this CV and extract: current_sector, seniority_level, top_5_skills.
Return ONLY valid JSON like this:
{
    "current_sector": "sector name",
    "seniority_level": "level",
    "top_5_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"]
}

CV Text:
""" + cv_text[:2000]

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        
        if json_match:
            result = json.loads(json_match.group())
            return {
                "current_sector": result.get("current_sector", "Unknown"),
                "seniority_level": result.get("seniority_level", "Unknown"),
                "top_5_skills": result.get("top_5_skills", [])
            }
        
        return {
            "current_sector": "Unknown",
            "seniority_level": "Unknown",
            "top_5_skills": []
        }
            
    except Exception as e:
        return {
            "current_sector": "Unknown",
            "seniority_level": "Unknown",
            "top_5_skills": []
        }