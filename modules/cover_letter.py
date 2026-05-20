import os
import re
import json
import streamlit as st
from groq import Groq

# Hardcoded key
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_KEY if GROQ_KEY else os.getenv("GROQ_API_KEY"))

def generate_cover_letter(cv_text, job_title, job_description):
    """Generate a tailored cover letter"""
    
    prompt = f"""You are an expert resume writer. Write a compelling cover letter for the following job application based on the provided CV.
    
    **Rules:**
    - Address it to the Hiring Manager.
    - Use a professional yet engaging tone.
    - Highlight 2-3 key achievements that match the job description.
    - Format as Markdown.
    
    **Job Title:** {job_title}
    **Job Description:** {job_description}
    
    **Candidate CV:**
    {cv_text}
    
    **Cover Letter:**
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
        return f"Error generating cover letter: {e}"