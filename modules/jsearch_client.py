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
            st.error("Please enter a job title or search term")
            return {"data": [], "status": "error", "message": "No query provided"}
        
        # Build search query
        search_query = query.strip()
        if location and location.strip():
            search_query = query.strip() + " in " + location.strip()
        
        # Build parameters
        params = {
            "query": search_query,
            "num_pages": min(num_pages, 10),
            "country": country,
            "date_posted": date_posted
        }
        
        if employment_types and len(employment_types) > 0:
            params["employment_types"] = ",".join(employment_types)
        
        try:
            st.info(f"📡 Calling JSearch API with query: {search_query}")
            
            response = requests.get(
                _self.BASE_URL + "/search-v2",
                headers=_self.headers,
                params=params,
                timeout=60
            )
            
            st.info(f"📡 API Response Status Code: {response.status_code}")
            
            # Handle different status codes
            if response.status_code == 400:
                error_msg = response.text[:500] if response.text else "Bad Request"
                st.error(f"❌ API Error 400: {error_msg}")
                return {"data": [], "status": "error", "message": error_msg}
            elif response.status_code == 401:
                st.error("❌ API Error 401: Invalid API Key")
                return {"data": [], "status": "error", "message": "Invalid API key"}
            elif response.status_code == 429:
                st.error("❌ API Error 429: Rate Limit Exceeded")
                return {"data": [], "status": "error", "message": "Rate limit"}
            elif response.status_code != 200:
                st.error(f"❌ API Error {response.status_code}: {response.text[:500]}")
                return {"data": [], "status": "error", "message": f"HTTP {response.status_code}"}
            
            # Parse JSON response
            try:
                data = response.json()
            except Exception as e:
                st.error(f"❌ Failed to parse API response as JSON: {e}")
                st.error(f"Response text: {response.text[:500]}")
                return {"data": [], "status": "error", "message": "Invalid JSON response"}
            
            # Check if data is a dict
            if not isinstance(data, dict):
                st.error(f"❌ Unexpected response format: {type(data)}")
                return {"data": [], "status": "error", "message": "Invalid response format"}
            
            jobs_list = data.get("data", [])
            
            if not jobs_list:
                st.warning("ℹ️ API returned successfully but no jobs found")
                return {"data": [], "status": "ok", "message": "No jobs found"}
            
            # Process jobs safely
            processed_jobs = []
            for i, job in enumerate(jobs_list):
                # Ensure job is a dict before trying to modify it
                if not isinstance(job, dict):
                    st.warning(f"⚠️ Job {i} is not a dictionary, skipping")
                    continue
                
                try:
                    # Add match score
                    job["career_compass_match_score"] = _self._calculate_match_score(job, query, user_skills)
                    job["fetched_at"] = datetime.now().isoformat()
                    job["normalized_salary"] = _self._normalize_salary(job.get("estimated_salaries"))
                    processed_jobs.append(job)
                except Exception as e:
                    st.warning(f"⚠️ Error processing job {i}: {e}")
                    continue
            
            if not processed_jobs:
                st.warning("ℹ️ No valid jobs could be processed")
                return {"data": [], "status": "ok", "message": "No valid jobs"}
            
            # Sort by match score
            processed_jobs.sort(key=lambda x: x.get("career_compass_match_score", 0), reverse=True)
            
            data["data"] = processed_jobs
            st.success(f"✅ Successfully processed {len(processed_jobs)} jobs")
            return data
            
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out after 60 seconds")
            return {"data": [], "status": "error", "message": "timeout"}
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            import traceback
            st.code(traceback.format_exc())
            return {"data": [], "status": "error", "message": str(e)}
    
    def _calculate_match_score(_self, job, query, user_skills=None):
        if not isinstance(job, dict):
            return 0.0
        job_description = job.get("job_description", "")
        if not job_description:
            return 0.0
        
        score = 0.0
        job_text = (job.get("job_title", "") + " " + job_description).lower()
        
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
            min_sal = salary.get("min", 0)
            max_sal = salary.get("max", 0)
            currency = salary.get("currency", "USD")
            period = salary.get("period", "YEAR").upper()
            
            if period == "HOUR":
                min_sal = min_sal * 2080
                max_sal = max_sal * 2080
            elif period == "MONTH":
                min_sal = min_sal * 12
                max_sal = max_sal * 12
            
            if currency != "USD":
                return {"min_annual_usd": None, "max_annual_usd": None, "original": salary, "note": "Currency: " + currency}
            
            return {"min_annual_usd": int(min_sal), "max_annual_usd": int(max_sal), "currency": "USD", "period": "YEAR"}
        except (IndexError, TypeError, KeyError, AttributeError):
            return None
