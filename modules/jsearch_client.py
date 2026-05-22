import requests
import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime
import time


class JSearchClient:
    BASE_URL = "https://jsearch.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("JSearch API key is required")
        self.api_key = api_key
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
    
    @st.cache_data(ttl=1800, show_spinner="Fetching smart job matches...")
    def search_jobs(_self, 
                   query: str,
                   location: Optional[str] = None,
                   employment_types: Optional[List[str]] = None,
                   date_posted: str = "all",
                   num_pages: int = 1,
                   country: str = "us",
                   user_skills: Optional[List[str]] = None) -> Dict:
        if not query or not query.strip():
            st.error("Please enter a job title or search term")
            return {"data": [], "status": "error", "message": "Query is required"}
        
        search_query = query.strip()
        if location and location.strip():
            search_query = f"{search_query} in {location.strip()}"
        
        params = {
            "query": search_query,
            "num_pages": min(num_pages, 10),
            "country": country,
            "date_posted": date_posted
        }
        
        if employment_types and len(employment_types) > 0:
            params["employment_types"] = ",".join(employment_types)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    f"{_self.BASE_URL}/search-v2",
                    headers=_self.headers,
                    params=params,
                    timeout=60
                )
                
                if response.status_code == 400:
                    try:
                        error_json = response.json()
                        error_msg = str(error_json)
                    except:
                        error_msg = response.text[:200]
                    st.error(f"API Error 400: {error_msg}")
                    return {"data": [], "status": "error", "message": error_msg}
                
                elif response.status_code == 401:
                    st.error("API Error 401: Invalid API Key")
                    return {"data": [], "status": "error", "message": "Invalid API key"}
                    
                elif response.status_code == 429:
                    st.error("API Error 429: Rate Limit Exceeded")
                    return {"data": [], "status": "error", "message": "Rate limit"}
                
                response.raise_for_status()
                
                try:
                    data = response.json()
                except ValueError as e:
                    st.error(f"Failed to parse API response: {e}")
                    return {"data": [], "status": "error", "message": "Invalid JSON"}
                
                if not isinstance(data, dict):
                    st.error(f"Unexpected response format: {type(data).__name__}")
                    return {"data": [], "status": "error", "message": "Invalid format"}
                
                jobs_list = data.get("data", [])
                if not jobs_list:
                    st.info("No jobs found for this search")
                    return {"data": [], "status": data.get("status", "unknown")}
                
                processed_jobs = []
                for job in jobs_list:
                    if not isinstance(job, dict):
                        continue
                    
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
                
                data["data"] = processed_jobs
                return data
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    st.warning(f"Timeout (attempt {attempt + 1}/{max_retries}). Retrying...")
                    time.sleep(5)
                    continue
                else:
                    st.error("Job search timed out after 3 attempts.")
                    return {"data": [], "status": "error", "message": "timeout"}
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                return {"data": [], "status": "error", "message": str(e)}
        
        return {"data": [], "status": "error", "message": "Max retries exceeded"}
    
    def _calculate_match_score(_self, job: Dict, query: str, 
                            user_skills: Optional[List[str]] = None) -> float:
        if not isinstance(job, dict):
            return 0.0
            
        job_description = job.get("job_description", "")
        if not job_description:
            return 0.0
        
        score = 0.0
        job_text = f"{job.get('job_title', '')} {job_description}".lower()
        
        query_terms = [t.strip().lower() for t in query.split() if len(t) > 3]
        if query_terms:
            matches = sum(1 for term in query_terms if term in job_text)
            score += 0.4 * (matches / len(query_terms))
        
        if user_skills and job.get("job_required_skills"):
            job_skills = [s.lower() for s in job["job_required_skills"]]
            skill_matches = sum(1 for skill in user_skills 
                              if any(skill.lower() in js for js in job_skills))
            score += 0.5 * min(1.0, skill_matches / max(1, len(user_skills)))
        
        return min(1.0, round(score, 2))
    
    def _normalize_salary(_self, salary_data: Optional[List[Dict]]) -> Optional[Dict]:
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
                min_sal *= 2080
                max_sal *= 2080
            elif period == "MONTH":
                min_sal *= 12
                max_sal *= 12
            
            if currency != "USD":
                return {
                    "min_annual_usd": None,
                    "max_annual_usd": None,
                    "original": salary,
                    "note": f"Currency: {currency}"
                }
            
            return {
                "min_annual_usd": int(min_sal),
                "max_annual_usd": int(max_sal),
                "currency": "USD",
                "period": "YEAR"
            }
        except (IndexError, TypeError, KeyError, AttributeError):
            return None