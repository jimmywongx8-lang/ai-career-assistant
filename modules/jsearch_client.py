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
        
        # Show API attempt in UI
        st.info(f"🔄 Attempting real API call for: {query}")
        
        try:
            search_query = query.strip()
            if location:
                search_query += f" in {location}"
            
            params = {
                "query": search_query,
                "page": 1,
                "num_pages": str(num_pages)  # Ensure string
            }
            
            if date_posted != "all":
                params["date_posted"] = date_posted
            
            if employment_types:
                params["employment_types"] = ",".join(employment_types)

            st.write(f"**Request URL:** {self.BASE_URL}/search-v2")
            st.write(f"**Params:** {params}")

            response = requests.get(
                f"{self.BASE_URL}/search-v2",
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            st.write(f"**HTTP Status:** {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                st.write(f"**API Status:** {data.get('status')}")
                st.write(f"**Jobs Found:** {len(data.get('data', []))}")
                
                if data.get("status") == "OK" and data.get("data"):
                    processed_jobs = []
                    for job in data["data"]:
                        processed_jobs.append(self._clean_job(job, user_skills))
                    
                    st.success(f"✅ Real API Success: {len(processed_jobs)} jobs")
                    return {"data": processed_jobs, "status": "OK"}
                else:
                    st.warning(f"⚠️ API returned no data: {data.get('message')}")
            elif response.status_code == 401:
                st.error("❌ 401 Unauthorized - Invalid API Key")
            elif response.status_code == 429:
                st.error("❌ 429 Rate Limit Exceeded")
            else:
                st.error(f"❌ HTTP {response.status_code}: {response.text[:200]}")
                    
        except Exception as e:
            st.error(f"❌ Exception: {e}")
            
        # Fallback
        st.warning("🔄 Using mock data fallback")
        mock_jobs = self._get_mock_jobs(user_skills)
        return {"data": mock_jobs, "status": "OK"}

    def _clean_job(self, job, user_skills):
        title = job.get("job_title", "Unknown Role")
        employer = job.get("employer_name", "Company")
        city = job.get("job_city", "")
        state = job.get("job_state", "")
        desc = job.get("job_description", "")
        apply_link = job.get("job_apply_link") or "#"
        skills = job.get("job_required_skills") or []
        
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
        if not user_skills:
            return 0.5
            
        score = 0.0
        combined_text = (title + " " + desc).lower()
        job_skills_lower = [s.lower() for s in job_skills]
        user_skills_lower = [s.lower() for s in user_skills]
        
        if job_skills_lower:
            matches = sum(1 for s in user_skills_lower if s in job_skills_lower)
            score += 0.6 * (matches / len(user_skills_lower))
            
        keywords = [s.lower() for s in user_skills if len(s) > 3]
        if keywords:
            text_matches = sum(1 for k in keywords if k in combined_text)
            score += 0.4 * (text_matches / len(keywords))
            
        return min(1.0, round(score, 2))

    def _get_mock_jobs(self, user_skills):
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