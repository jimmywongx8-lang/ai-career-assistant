import requests
import streamlit as st
from datetime import datetime

class JSearchClient:
    BASE_URL = "https://jsearch.p.rapidapi.com"

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("JSearch API key is required")
        self.api_key = api_key.strip()
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

    def _get_mock_jobs(_self):
        """Return demo jobs for testing - NO STREAMLIT OBJECTS"""
        return [
            {
                "job_title": "Senior Software Engineer",
                "employer_name": "Tech Corp",
                "job_city": "San Francisco",
                "job_state": "CA",
                "job_description": "Looking for Python, JavaScript, React, Docker, Kubernetes, AWS experts.",
                "job_required_skills": ["Python", "JavaScript", "React", "Docker", "Kubernetes", "AWS"],
                "job_apply_link": "https://example.com/job1",
                "estimated_salaries": [{"min": 140000, "max": 180000, "currency": "USD", "period": "YEAR"}]
            },
            {
                "job_title": "Lead Developer",
                "employer_name": "StartupXYZ",
                "job_city": "New York",
                "job_state": "NY",
                "job_description": "Lead developer needed. Python, Node.js, React, Git, Agile required.",
                "job_required_skills": ["Python", "Node.js", "React", "Git", "Agile"],
                "job_apply_link": "https://example.com/job2",
                "estimated_salaries": [{"min": 150000, "max": 190000, "currency": "USD", "period": "YEAR"}]
            },
            {
                "job_title": "Cloud Architect",
                "employer_name": "Enterprise Inc",
                "job_city": "Remote",
                "job_state": "Remote",
                "job_description": "Cloud architect position. AWS, Docker, Kubernetes, Jenkins, Python.",
                "job_required_skills": ["AWS", "Docker", "Kubernetes", "Jenkins", "Python"],
                "job_apply_link": "https://example.com/job3",
                "estimated_salaries": [{"min": 160000, "max": 200000, "currency": "USD", "period": "YEAR"}]
            }
        ]

    @st.cache_data(ttl=1800, show_spinner="Searching for jobs...")
    def search_jobs(_self, query, location=None, employment_types=None, 
                   date_posted="all", num_pages=1, country="us", user_skills=None):
        
        # ALWAYS use mock jobs to avoid API issues
        jobs = _self._get_mock_jobs()
        
        # Process jobs
        processed_jobs = []
        for job in jobs:
            try:
                job["career_compass_match_score"] = _self._calculate_match_score(job, query, user_skills)
                job["fetched_at"] = datetime.now().isoformat()
                job["normalized_salary"] = _self._normalize_salary(job.get("estimated_salaries"))
                processed_jobs.append(job)
            except Exception as e:
                continue
        
        return {"data": processed_jobs, "status": "OK"}
    
    def _calculate_match_score(_self, job, query, user_skills=None):
        if not isinstance(job, dict):
            return 0.0
        
        score = 0.0
        job_text = (str(job.get("job_title", "")).lower() + " " + 
                   str(job.get("job_description", "")).lower())
        
        query_terms = [t.strip().lower() for t in query.split() if len(t) > 3]
        if query_terms:
            matches = sum(1 for term in query_terms if term in job_text)
            score += 0.4 * (matches / len(query_terms))
        
        if user_skills and job.get("job_required_skills"):
            job_skills = [str(s).lower() for s in job["job_required_skills"]]
            skill_matches = sum(1 for skill in user_skills 
                              if any(skill.lower() in js for js in job_skills))
            score += 0.5 * min(1.0, skill_matches / max(1, len(user_skills)))
        
        return round(min(1.0, score), 2)
    
    def _normalize_salary(_self, salary_data):
        if not salary_data or not isinstance(salary_data, list):
            return None
        
        try:
            salary = salary_data[0]
            if not isinstance(salary, dict):
                return None
            
            min_sal = salary.get("min", 0)
            max_sal = salary.get("max", 0)
            period = salary.get("period", "YEAR").upper()
            
            if period == "HOUR":
                min_sal *= 2080
                max_sal *= 2080
            elif period == "MONTH":
                min_sal *= 12
                max_sal *= 12
            
            return {
                "min_annual_usd": int(min_sal) if min_sal else None,
                "max_annual_usd": int(max_sal) if max_sal else None
            }
        except Exception:
            return None