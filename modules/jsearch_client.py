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
        """Return sample jobs based on John Smith's CV for demo purposes"""
        return [
            {
                "job_title": "Senior Software Engineer",
                "employer_name": "Tech Innovations Inc",
                "job_city": "San Francisco",
                "job_state": "CA",
                "job_description": "We are seeking a Senior Software Engineer with expertise in cloud-based microservices architecture. You will lead development teams and work with Python, JavaScript, React, Node.js, Docker, and Kubernetes. Experience with AWS and CI/CD pipelines using Jenkins required.",
                "job_required_skills": ["Python", "JavaScript", "React", "Node.js", "Docker", "Kubernetes", "AWS", "Jenkins", "Agile"],
                "job_apply_link": "https://example.com/apply1",
                "estimated_salaries": [{"min": 140000, "max": 180000, "currency": "USD", "period": "YEAR"}],
                "job_employment_type": "FULLTIME"
            },
            {
                "job_title": "Lead Software Developer",
                "employer_name": "Cloud Solutions Corp",
                "job_city": "New York",
                "job_state": "NY",
                "job_description": "Join our team as a Lead Developer. You'll manage a team of junior developers while architecting scalable solutions. Strong skills in Python, React, Docker, Kubernetes, and AWS required. Experience with Git, Agile methodologies, and team leadership essential.",
                "job_required_skills": ["Python", "React", "Docker", "Kubernetes", "AWS", "Git", "Agile", "Team Leadership"],
                "job_apply_link": "https://example.com/apply2",
                "estimated_salaries": [{"min": 150000, "max": 190000, "currency": "USD", "period": "YEAR"}],
                "job_employment_type": "FULLTIME"
            },
            {
                "job_title": "Senior Full Stack Engineer",
                "employer_name": "StartupXYZ",
                "job_city": "Remote",
                "job_state": "Remote",
                "job_description": "Remote opportunity for a Senior Full Stack Engineer. Build RESTful APIs using Python and Node.js, develop frontend applications with React. Work with modern cloud technologies including Docker, Kubernetes, and AWS. Collaborate with product teams in an Agile environment.",
                "job_required_skills": ["Python", "Node.js", "React", "JavaScript", "Docker", "AWS", "Git"],
                "job_apply_link": "https://example.com/apply3",
                "estimated_salaries": [{"min": 130000, "max": 170000, "currency": "USD", "period": "YEAR"}],
                "job_employment_type": "FULLTIME"
            },
            {
                "job_title": "Cloud Software Architect",
                "employer_name": "Enterprise Solutions LLC",
                "job_city": "Austin",
                "job_state": "TX",
                "job_description": "Seeking a Cloud Software Architect to design and implement microservices architecture. Lead technical initiatives, optimize system performance, and mentor junior developers. Expertise in Python, Kubernetes, Docker, AWS, and CI/CD pipelines required.",
                "job_required_skills": ["Python", "Kubernetes", "Docker", "AWS", "Jenkins", "Agile", "Team Leadership"],
                "job_apply_link": "https://example.com/apply4",
                "estimated_salaries": [{"min": 160000, "max": 200000, "currency": "USD", "period": "YEAR"}],
                "job_employment_type": "FULLTIME"
            },
            {
                "job_title": "Senior Backend Developer (Python)",
                "employer_name": "DataTech Systems",
                "job_city": "Seattle",
                "job_state": "WA",
                "job_description": "We need a Senior Backend Developer specializing in Python development. Build scalable APIs, optimize system latency, and implement CI/CD pipelines. Experience with Node.js, React, Docker, Kubernetes, and Git essential. Team collaboration in Agile environment.",
                "job_required_skills": ["Python", "Node.js", "Docker", "Kubernetes", "Git", "Agile"],
                "job_apply_link": "https://example.com/apply5",
                "estimated_salaries": [{"min": 135000, "max": 175000, "currency": "USD", "period": "YEAR"}],
                "job_employment_type": "FULLTIME"
            }
        ]

    @st.cache_data(ttl=1800, show_spinner="Searching for jobs...")
    def search_jobs(_self, query, location=None, employment_types=None, 
                   date_posted="all", num_pages=1, country="us", user_skills=None):
        
        if not query:
            return {"data": [], "status": "error", "message": "No query provided"}
        
        try:
            search_query = query.strip()
            if location and location.strip():
                search_query = f"{search_query} in {location.strip()}"
            
            params = {
                "query": search_query,
                "num_pages": "1",
            }
            
            if date_posted and date_posted != "all":
                params["date_posted"] = date_posted
            
            if employment_types and len(employment_types) > 0:
                params["employment_types"] = ",".join(employment_types)
            
            response = requests.get(
                f"{_self.BASE_URL}/search-v2",
                headers=_self.headers,
                params=params,
                timeout=60
            )
            
            st.write(f"**HTTP Status:** {response.status_code}")
            
            if response.status_code != 200:
                st.error(f"❌ HTTP Error {response.status_code}")
                st.info("💡 Using demo jobs instead")
                jobs = _self._get_mock_jobs()
            else:
                try:
                    result = response.json()
                    
                    if result.get("status") != "OK":
                        st.warning(f"⚠️ API returned: {result.get('message', 'Unknown error')}")
                        st.info("💡 Using demo jobs instead")
                        jobs = _self._get_mock_jobs()
                    else:
                        jobs = result.get("data", [])
                        
                        if not jobs:
                            st.warning("⚠️ API returned no jobs")
                            st.info("💡 Using demo jobs for demonstration")
                            jobs = _self._get_mock_jobs()
                
                except Exception as e:
                    st.error(f"❌ JSON parse error: {e}")
                    st.info("💡 Using demo jobs instead")
                    jobs = _self._get_mock_jobs()
            
            # Process jobs
            processed_jobs = []
            for job in jobs:
                if not isinstance(job, dict):
                    continue
                
                try:
                    job["career_compass_match_score"] = _self._calculate_match_score(
                        job, query, user_skills
                    )
                    job["fetched_at"] = datetime.now().isoformat()
                    job["normalized_salary"] = _self._normalize_salary(
                        job.get("estimated_salaries")
                    )
                    processed_jobs.append(job)
                except Exception as e:
                    continue
            
            if not processed_jobs:
                return {"data": [], "status": "OK", "message": "No valid jobs"}
            
            processed_jobs.sort(
                key=lambda x: x.get("career_compass_match_score", 0), 
                reverse=True
            )
            
            st.success(f"✅ Found {len(processed_jobs)} jobs!")
            
            return {"data": processed_jobs, "status": "OK"}
            
        except Exception as e:
            st.error(f"❌ Request failed: {e}")
            st.info("💡 Using demo jobs instead")
            jobs = _self._get_mock_jobs()
            
            processed_jobs = []
            for job in jobs:
                job["career_compass_match_score"] = _self._calculate_match_score(
                    job, query, user_skills
                )
                job["fetched_at"] = datetime.now().isoformat()
                job["normalized_salary"] = _self._normalize_salary(
                    job.get("estimated_salaries")
                )
                processed_jobs.append(job)
            
            processed_jobs.sort(
                key=lambda x: x.get("career_compass_match_score", 0), 
                reverse=True
            )
            
            return {"data": processed_jobs, "status": "OK"}
    
    def _calculate_match_score(_self, job, query, user_skills=None):
        if not isinstance(job, dict):
            return 0.0
        
        score = 0.0
        job_text = (
            str(job.get("job_title", "")).lower() + " " + 
            str(job.get("job_description", "")).lower()
        )
        
        query_terms = [t.strip().lower() for t in query.split() if len(t) > 3]
        if query_terms:
            matches = sum(1 for term in query_terms if term in job_text)
            score += 0.4 * (matches / len(query_terms))
        
        if user_skills and job.get("job_required_skills"):
            job_skills = [str(s).lower() for s in job["job_required_skills"]]
            skill_matches = sum(
                1 for skill in user_skills 
                if any(skill.lower() in js for js in job_skills)
            )
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