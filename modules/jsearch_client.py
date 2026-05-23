import requests
import streamlit as st

class JSearchClient:
    BASE_URL = "https://jsearch.p.rapidapi.com"

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

    def search_jobs(self, query, location=None, employment_types=None, 
                   date_posted="all", num_pages=1, user_skills=None):
        
        # ==========================================
        # 1. ATTEMPT REAL API CALL
        # ==========================================
        try:
            # Build search query
            search_query = query.strip()
            if location:
                search_query += f" in {location}"
            
            # API Parameters
            params = {
                "query": search_query,
                "page": 1,
                "num_pages": num_pages
            }
            
            if date_posted != "all":
                params["date_posted"] = date_posted
            
            if employment_types:
                params["employment_types"] = ",".join(employment_types)

            # Make Request
            response = requests.get(
                f"{self.BASE_URL}/search-v2",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            # Check for Success
            if response.status_code == 200:
                data = response.json()
                
                # Verify API returned valid data
                if data.get("status") == "OK" and data.get("data"):
                    processed_jobs = []
                    for job in data["data"]:
                        # Clean and score each job
                        processed_jobs.append(self._clean_job(job, user_skills))
                    
                    print(f"✅ Real API Success: Found {len(processed_jobs)} jobs")
                    return {"data": processed_jobs, "status": "OK"}
                else:
                    print("⚠️ API returned empty data or error status")
                    
        except Exception as e:
            # Log error for debugging (visible in Streamlit logs)
            print(f"❌ Real API Failed: {e}")
            
        # ==========================================
        # 2. FALLBACK TO MOCK DATA
        # (Ensures app never breaks during demos)
        # ==========================================
        print("🔄 Using Mock Data Fallback")
        mock_jobs = self._get_mock_jobs(user_skills)
        return {"data": mock_jobs, "status": "OK"}

    def _clean_job(self, job, user_skills):
        """Parse raw API data into a clean format for the UI"""
        
        # Extract fields safely
        title = job.get("job_title", "Unknown Role")
        employer = job.get("employer_name", "Company")
        city = job.get("job_city", "")
        state = job.get("job_state", "")
        desc = job.get("job_description", "")
        apply_link = job.get("job_apply_link") or "#"
        skills = job.get("job_required_skills") or []
        
        # Parse Salary Info
        salary_data = job.get("estimated_salaries") or []
        normalized_salary = None
        if salary_data:
            try:
                first_salary = salary_data[0]
                normalized_salary = {
                    "min_annual_usd": first_salary.get("min"),
                    "max_annual_usd": first_salary.get("max"),
                    "currency": first_salary.get("currency", "USD")
                }
            except Exception:
                pass
        
        # Calculate Match Score
        match_score = self._calculate_match_score(title, desc, skills, user_skills)
        
        return {
            "job_title": title,
            "employer_name": employer,
            "job_city": city,
            "job_state": state,
            "job_description": desc,
            "job_required_skills": skills,
            "job_apply_link": apply_link,
            "normalized_salary": normalized_salary,
            "career_compass_match_score": match_score
        }

    def _calculate_match_score(self, title, desc, job_skills, user_skills):
        """Calculate how well the job matches the user's CV skills"""
        if not user_skills:
            return 0.5  # Default score if no skills provided
            
        score = 0.0
        combined_text = (title + " " + desc).lower()
        job_skills_lower = [s.lower() for s in job_skills]
        user_skills_lower = [s.lower() for s in user_skills]
        
        # 1. Skill Matching (60% weight)
        if job_skills_lower:
            matches = sum(1 for s in user_skills_lower if s in job_skills_lower)
            score += 0.6 * (matches / len(user_skills_lower))
            
        # 2. Keyword Matching in Description (40% weight)
        keywords = [s.lower() for s in user_skills if len(s) > 3]
        if keywords:
            text_matches = sum(1 for k in keywords if k in combined_text)
            score += 0.4 * (text_matches / len(keywords))
            
        return min(1.0, round(score, 2))

    def _get_mock_jobs(self, user_skills):
        """Return demo jobs if API fails"""
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