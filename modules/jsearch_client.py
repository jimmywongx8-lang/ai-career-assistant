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

    @st.cache_data(ttl=1800, show_spinner="Fetching jobs...")
    def search_jobs(_self, query, location=None, employment_types=None, 
                   date_posted="all", num_pages=1, country="us", user_skills=None):
        
        if not query:
            return {"data": [], "status": "error", "message": "No query"}
        
        # Build query string
        search_query = query.strip()
        if location and location.strip():
            search_query += f" in {location.strip()}"
        
        # Build URL with query parameters
        url = f"{_self.BASE_URL}/search-v2"
        
        params = {
            "query": search_query,
            "num_pages": str(num_pages),
            "date_posted": date_posted,
        }
        
        if country:
            params["country"] = country
        
        if employment_types and len(employment_types) > 0:
            params["employment_types"] = ",".join(employment_types)
        
        try:
            # Make the request
            response = requests.get(
                url,
                headers=_self.headers,
                params=params,
                timeout=60
            )
            
            st.write(f"**HTTP Status:** {response.status_code}")
            
            # Check HTTP status
            if response.status_code == 401:
                st.error("❌ 401: Invalid API Key")
                return {"data": [], "status": "error", "message": "Invalid API key"}
            elif response.status_code == 403:
                st.error("❌ 403: Forbidden - Check API subscription")
                return {"data": [], "status": "error", "message": "Forbidden"}
            elif response.status_code != 200:
                st.error(f"❌ HTTP {response.status_code}")
                st.write(response.text[:500])
                return {"data": [], "status": "error", "message": f"HTTP {response.status_code}"}
            
            # Parse response
            try:
                result = response.json()
            except:
                st.error("❌ Invalid JSON response")
                return {"data": [], "status": "error", "message": "Invalid JSON"}
            
            # Check API status
            if result.get("status") != "OK":
                error_msg = result.get("message", "Unknown API error")
                st.error(f"❌ API Error: {error_msg}")
                
                # Show helpful hints
                if "invalid" in error_msg.lower() or "format" in error_msg.lower():
                    st.warning("💡 This usually means:")
                    st.warning("1. API key is incorrect")
                    st.warning("2. You haven't subscribed to JSearch on RapidAPI")
                    st.warning("3. Rate limit exceeded")
                
                return {"data": [], "status": "error", "message": error_msg}
            
            jobs = result.get("data", [])
            
            if not jobs:
                st.info("ℹ️ No jobs found")
                return {"data": [], "status": "OK", "message": "No jobs found"}
            
            # Process jobs
            processed = []
            for job in jobs:
                if not isinstance(job, dict):
                    continue
                job["career_compass_match_score"] = _self._calculate_match_score(job, query, user_skills)
                job["fetched_at"] = datetime.now().isoformat()
                job["normalized_salary"] = _self._normalize_salary(job.get("estimated_salaries"))
                processed.append(job)
            
            processed.sort(key=lambda x: x.get("career_compass_match_score", 0), reverse=True)
            result["data"] = processed
            
            return result
            
        except Exception as e:
            st.error(f"❌ Error: {e}")
            return {"data": [], "status": "error", "message": str(e)}
    
    def _calculate_match_score(_self, job, query, user_skills=None):
        if not isinstance(job, dict):
            return 0.0
        text = (job.get("job_title", "") + " " + str(job.get("job_description", ""))).lower()
        score = 0.0
        
        terms = [t.lower() for t in query.split() if len(t) > 3]
        if terms:
            matches = sum(1 for t in terms if t in text)
            score += 0.4 * (matches / len(terms))
        
        if user_skills and job.get("job_required_skills"):
            job_skills = [s.lower() for s in job["job_required_skills"]]
            matches = sum(1 for s in user_skills if any(s.lower() in j for j in job_skills))
            score += 0.5 * min(1.0, matches / max(1, len(user_skills)))
        
        return round(min(1.0, score), 2)
    
    def _normalize_salary(_self, data):
        if not data or not isinstance(data, list):
            return None
        try:
            s = data[0]
            if not isinstance(s, dict):
                return None
            return {"min_annual_usd": int(s.get("min", 0)), "max_annual_usd": int(s.get("max", 0))}
        except:
            return None