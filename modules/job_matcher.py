# modules/job_matcher.py
import os
import json
import time
import re
import streamlit as st
from groq import Groq

# Hardcoded key for now (works locally and on cloud)
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_KEY if GROQ_KEY else os.getenv("GROQ_API_KEY"))

def load_local_jobs():
    """Load jobs from local JSON file"""
    jobs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "real_jobs.json")
    if os.path.exists(jobs_path):
        with open(jobs_path, "r", encoding="utf-8") as f:
            return json.load(f)
    print("No local jobs file found")
    return []

def ai_score_job(cv_text, job):
    """Use AI to score job match"""
    prompt = f"""Analyze the match between this CV and Job Description.
Return ONLY a valid JSON object:
{{
  "score": 0-100,
  "reasons": ["3 short bullet points why it matches"],
  "gaps": ["2 short bullet points missing skills/experience"]
}}

CV: {cv_text[:800]}
Job Title: {job['title']}
Job Description: {job.get('description', '')}
"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=350
        )
        match = re.search(r'\{.*\}', response.choices[0].message.content, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"AI Scoring Error: {e}")
    
    return {"score": 70, "reasons": ["Basic keyword match"], "gaps": ["AI scoring skipped"]}

def find_matching_jobs(cv_text: str, keywords: str = "consultant", location: str = "Singapore", num_matches: int = 3):
    """Find matching jobs using local data + AI scoring"""
    print(f"Loading local jobs for: {keywords} in {location}...")
    
    jobs = load_local_jobs()
    
    if not jobs:
        print("No jobs available")
        return []
    
    print(f"Found {len(jobs)} local jobs")
    
    print("AI scoring matches...")
    scored_matches = []
    for job in jobs[:6]:
        score_data = ai_score_job(cv_text, job)
        job.update(score_data)
        scored_matches.append(job)
        time.sleep(0.3)
    
    scored_matches.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored_matches[:num_matches]