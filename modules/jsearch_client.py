import requests
import streamlit as st
from datetime import datetime
import time

class JSearchClient:
    BASE_URL = "https://jsearch.p.rapidapi.com"

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("JSearch API key is required")
        self.api_key = api_key
        self.headers = {
            "X-RapidAPI-Key": api_key,
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
            "num_pages": min(num_pages, 10),
            "country": country,
            "date_posted": date_posted
        }
        
        if employment_types and len(employment_types) > 0:
            params["employment_types"] = ",".join(employment_types)
        
        try:
            # st.info(f"📡 Calling JSearch API...") # Optional: comment out to reduce noise
            
            response = requests.get(
                _self.BASE_URL + "/search-v2",
                headers=_self.headers,
                params=params,
                timeout=60
            )
            
            if response.status_code != 200:
                error_text = response.text[:300]
                st.error(f"❌ API HTTP Error {response.status_code}: {error_text}")
                return {"data": [], "status": "error", "message": f"HTTP {response.status_code}"}
            
            try:
                data = response.json()
            except Exception as e:
                st.error(f"❌ Failed to parse JSON: {e}")
                return {"data": [], "status": "error", "message": "Invalid JSON"}
            
            # --- DEBUGGING LOGIC START ---
            # Check if 'data' field exists and is a list
            raw_data = data.get("data")
            
            if raw_data is None:
                st.error("❌ API response missing 'data' field.")
                st.write("Full Response:", data)
                return {"data": [], "status": "error", "message": "Missing data field"}
            
            if not isinstance(raw_data, list):
                # This is the likely issue: API returning a string error in the data field
                st.error(f"❌ API 'data' field is not a list! It is a {type(raw_data).__name__}.")
                st.warning(f"Content: {str(raw_data)[:300]}")
                st.info("💡 This usually means your API Key is invalid, expired, or you hit a rate limit.")
                return {"data": [], "status": "error", "message": "Invalid data format from API"}
            # --- DEBUGGING LOGIC END ---
            
            jobs_list = raw_data
            
            if not jobs_list:
                return {"data": [], "status": "ok", "message": "No jobs found"}
            
            processed_jobs = []
            for i, job in enumerate(jobs_list):
                if not isinstance(job, dict):
                    st.warning(f"️ Job {i} is not a dictionary (Type: {type(job).__name__}). Skipping.")
                    continue
                
                try:
                    job["career_compass_match_score"] = _self._calculate_match_score(job, query, user_skills)
                    job["fetched_at"] = datetime.now().isoformat()
                    job["normalized_salary"] = _self._normalize_salary(job.get("estimated_salaries"))
                    processed_jobs.append(job)
                except Exception as e:
                    st.warning(f"⚠️ Error processing job {i}: {e}")
            
            if not processed_jobs:
                return {"data": [], "status": "ok", "message": "No valid jobs processed"}
            
            processed_jobs.sort(key=lambda x: x.get("career_compass_match_score", 0), reverse=True)
            data["data"] = processed_jobs
            return data
            
        except requests.exceptions.Timeout:
            return {"data": [], "status": "error", "message": "Timeout"}
        except Exception as e:
            st.error(f"❌ Unexpected Error: {e}")
            return {"data": [], "status": "error", "message": str(e)}
    
    def _calculate_match_score(_self, job, query, user_skills=None):
        if not isinstance(job, dict): return 0.0
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
        if not salary_data or not isinstance(salary_data, list): return None
        try:
            salary = salary_data[0]
            if not isinstance(salary, dict): return None
            return {"min_annual_usd": int(salary.get("min", 0)), "max_annual_usd": int(salary.get("max", 0))}
        except Exception:
            return None