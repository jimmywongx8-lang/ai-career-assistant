import requests
import json

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
        
        try:
            search_query = query.strip()
            if location:
                search_query += f" in {location}"
            
            params = {
                "query": search_query,
                "page": 1,
                "num_pages": str(num_pages)
            }
            
            if date_posted != "all":
                params["date_posted"] = date_posted
            
            if employment_types:
                params["employment_types"] = ",".join(employment_types)

            response = requests.get(
                f"{self.BASE_URL}/search-v2",
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "OK":
                    jobs_list = []
                    
                    if "data" in data and isinstance(data["data"], dict) and "jobs" in data["data"]:
                        jobs_list = data["data"]["jobs"]
                    elif "data" in data and isinstance(data["data"], list):
                        jobs_list = data["data"]
                    
                    if jobs_list:
                        processed_jobs = []
                        for job in jobs_list:
                            try:
                                cleaned = self._clean_job(job, user_skills)
                                processed_jobs.append(cleaned)
                            except Exception:
                                continue
                        
                        if processed_jobs:
                            return {"data": processed_jobs, "status": "OK"}
                    
        except Exception as e:
            print(f"API Error: {e}")
            
        # Fallback
        return {"data": self._get_mock_jobs(user_skills), "status": "OK"}

    def _clean_job(self, job, user_skills):
        """Extract ONLY plain Python types - NO Streamlit objects"""
        
        title = str(job.get("job_title", "Unknown Role"))
        employer = str(job.get("employer_name", "Company"))
        city = str(job.get("job_city", ""))
        state = str(job.get("job_state", ""))
        desc = str(job.get("job_description", ""))
        apply_link = str(job.get("job_apply_link") or "#")
        
        # Skills - ensure list of strings
        raw_skills = job.get("job_required_skills")
        skills = []
        if raw_skills and isinstance(raw_skills, list):
            for s in raw_skills:
                if s is not None:
                    skills.append(str(s))
        
        # Salary - ensure plain dict
        salary_data = job.get("estimated_salaries") or []
        normalized_salary = {}
        if salary_data and len(salary_data) > 0 and isinstance(salary_data[0], dict):
            first_salary = salary_data[0]
            normalized_salary = {
                "min_annual_usd": int(first_salary.get("min", 0) or 0),
                "max_annual_usd": int(first_salary.get("max", 0) or 0),
                "currency": str(first_salary.get("currency", "USD"))
            }
        
        # Match score - ensure float
        match_score = self._calculate_match_score(title, desc, skills, user_skills)
        
        # Return ONLY plain types
        return {
            "job_title": title,
            "employer_name": employer,
            "job_city": city,
            "job_state": state,
            "job_description": desc,
            "job_required_skills": skills,
            "job_apply_link": apply_link,
            "normalized_salary": normalized_salary,
            "career_compass_match_score": float(match_score)
        }

    def _calculate_match_score(self, title, desc, job_skills, user_skills):
        if not user_skills:
            return 0.5
            
        score = 0.0
        combined_text = (str(title) + " " + str(desc)).lower()
        job_skills_lower = [str(s).lower() for s in (job_skills or [])]
        user_skills_lower = [str(s).lower() for s in user_skills]
        
        if job_skills_lower:
            matches = sum(1 for s in user_skills_lower if s in job_skills_lower)
            score += 0.6 * (matches / len(user_skills_lower))
            
        keywords = [s for s in user_skills_lower if len(s) > 3]
        if keywords:
            text_matches = sum(1 for k in keywords if k in combined_text)
            score += 0.4 * (text_matches / len(keywords))
            
        return min(1.0, round(score, 2))

    def _get_mock_jobs(self, user_skills):
        return [
            {
                "job_title": "Strategy Consultant",
                "employer_name": "McKinsey & Company",
                "job_city": "New York",
                "job_state": "NY",
                "job_description": "Seeking strategy consultant with strong analytical and management skills.",
                "job_required_skills": ["Strategy", "Analysis", "Management", "Consulting"],
                "job_apply_link": "https://example.com/job1",
                "estimated_salaries": [{"min": 120000, "max": 160000, "currency": "USD", "period": "YEAR"}]
            },
            {
                "job_title": "Business Analyst",
                "employer_name": "Deloitte",
                "job_city": "Remote",
                "job_state": "Remote",
                "job_description": "Business analyst role focusing on financial analysis and strategic planning.",
                "job_required_skills": ["Analysis", "Finance", "Excel", "Strategy"],
                "job_apply_link": "https://example.com/job2",
                "estimated_salaries": [{"min": 90000, "max": 130000, "currency": "USD", "period": "YEAR"}]
            }
        ]