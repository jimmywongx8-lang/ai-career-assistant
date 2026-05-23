import requests
import streamlit as st
from datetime import datetime
import json

class JSearchClient:
    BASE_URL = "https://jsearch.p.rapidapi.com"

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("JSearch API key is required")
        self.api_key = api_key.strip()  # Remove any whitespace
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

    @st.cache_data(ttl=1800, show_spinner="Fetching job matches...")
    def search_jobs(_self, query, location=None, employment_types=None, 
                   date_posted="all", num_pages=1, country="us", user_skills=None):
        
        if not query:
            return {"data": [], "status": "error", "message": "Query is required"}
        
        search_query = query.strip()
        if location and location.strip():
            search_query = search_query + " in " + location.strip()
        
        params = {
            "query": search_query,
            "num_pages": str(min(num_pages, 10)),  # Ensure it's a string
            "country": country,
            "date_posted": date_posted
        }
        
        if employment_types and len(employment_types) > 0:
            params["employment_types"] = ",".join(employment_types)
        
        try:
            response = requests.get(
                f"{_self.BASE_URL}/search-v2",
                headers=_self.headers,
                params=params,
                timeout=60
            )
            
            # Log the actual request details for debugging
            st.write(f"**Request URL:** {response.url}")
            st.write(f"**Status Code:** {response.status_code}")
            
            if response.status_code == 401:
                st.error("❌ API Error 401: Invalid API Key")
                st.error("Please check your JSEARCH_API_KEY in Streamlit secrets")
                return {"data": [], "status": "error", "message": "Invalid API key"}
            elif response.status_code == 403:
                st.error("❌ API Error 403: Access Forbidden")
                st.error("Check if you're subscribed to the JSearch API on RapidAPI")
                return {"data": [], "status": "error", "message": "Forbidden"}
            elif response.status_code == 429:
                st.error("❌ API Error 429: Rate Limit Exceeded")
                return {"data": [], "status": "error", "message": "Rate limit"}
            elif response.status_code != 200:
                st.error(f"❌ API HTTP Error {response.status_code}")
                st.write(f"Response: {response.text[:500]}")
                return {"data": [], "status": "error", "message": f"HTTP {response.status_code}"}
            
            try:
                data = response.json()
            except Exception as e:
                st.error(f"❌ Failed to parse JSON: {e}")
                st.write(f"Raw response: {response.text[:500]}")
                return {"data": [], "status": "error", "message": "Invalid JSON"}
            
            # Check if we got an error in the response
            if data.get("status") == "error":
                st.error(f"❌ API Error: {data.get('message', 'Unknown error')}")
                return {"data": [], "status": "error", "message": data.get("message")}
            
            jobs_list = data.get("data", [])
            
            if not isinstance(jobs_list, list):
                st.error(f"❌ Data is not a list! Type: {type(jobs_list).__name__}")
                return {"data": [], "status": "error", "message": "Invalid data format"}
            
            if not jobs_list:
                st.warning("ℹ️ No jobs found for this search")
                return {"data": [], "status": "ok", "message": "No jobs found"}
            
            # Process jobs
            processed_jobs = []
            for i, job in enumerate(jobs_list):
                if not isinstance(job, dict):
                    continue
                
                try:
                    job["career_compass_match_score"] = _self._calculate_match_score(job, query, user_skills)
                    job["fetched_at"] = datetime.now().isoformat()
                    job["normalized_salary"] = _self._normalize_salary(job.get("estimated_salaries"))
                    processed_jobs.append(job)
                except Exception as e:
                    st.warning(f"⚠️ Error processing job {i}: {e}")
            
            if not processed_jobs:
                return {"data": [], "status": "ok", "message": "No valid jobs"}
            
            processed_jobs.sort(key=lambda x: x.get("career_compass_match_score", 0), reverse=True)
            data["data"] = processed_jobs
            
            return data
            
        except Exception as e:
            st.error(f"❌ Request failed: {e}")
            return {"data": [], "status": "error", "message": str(e)}
    
    def _calculate_match_score(_self, job, query, user_skills=None):
        if not isinstance(job, dict):
            return 0.0
        job_text = (job.get("job_title", "") + " " + str(job.get("job_description", ""))).lower()
        score = 0.0
        
        query_terms = [t.strip().lower() for t in query.split() if len(t) > 3]
        if query_terms:
            matches = sum(1 for term in query_terms if term in job_text)
            score += 0.4 * (matches / len(query_terms))
        
        if user_skills and job.get("job_required_skills"):
            job_skills = [s.lower() for s in job["job_required_skills"]]
            skill_matches = sum(1 for skill in user_skills if any(skill.lower() in js for js in job_skills))
            score += 0.5 * min(1.0, skill_matches / max(1, len(user_skills)))
        
        return min(1.0, round(score, 2))
    
    def _normalize_salary(_self, salary_data):
        if not salary_data or not isinstance(salary_data, list):
            return None
        try:
            salary = salary_data[0]
            if not isinstance(salary, dict):
                return None
            return {"min_annual_usd": int(salary.get("min", 0)), "max_annual_usd": int(salary.get("max", 0))}
        except:
            return None