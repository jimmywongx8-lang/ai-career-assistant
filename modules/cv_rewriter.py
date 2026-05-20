import os
import re
import json
import streamlit as st
from groq import Groq

# Hardcoded key
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_KEY if GROQ_KEY else os.getenv("GROQ_API_KEY"))

def rewrite_cv(cv_text, job_title, job_description):
    """Rewrite CV to match a specific job description"""
    
    prompt = f"""You are an expert career coach. Rewrite the following CV to highlight skills and experience relevant to the job description.
    
    **Rules:**
    - Use a professional tone.
    - Keep it concise.
    - Format as Markdown.
    - Focus on achievements that match the job requirements.
    
    **Job Title:** {job_title}
    **Job Description:** {job_description}
    
    **Original CV:**
    {cv_text}
    
    **Rewritten CV:**
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error rewriting CV: {e}"