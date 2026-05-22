# modules/jsearch_client.py
"""
Enhanced JSearch API client for Career Compass
Features: caching, error handling, match scoring, and career-focused filtering
"""
import requests
import streamlit as st
import time
from typing import Optional, List, Dict, Any
from datetime import datetime


class JSearchClient:
    """Production-ready JSearch API client with Career Compass enhancements"""
    
    BASE_URL = "https://jsearch.p.rapidapi.com"
    
    def __init__(self, api_key: str):
        """Initialize with RapidAPI key from Streamlit secrets"""
        if not api_key:
            raise ValueError("JSearch API key is required")
        self.api_key = api_key
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
    
    @st.cache_data(ttl=3600, show_spinner="🔍 Fetching smart job matches...")
    def search_jobs(_self, 
                   query: str,
                   location: Optional[str] = None,
                   employment_types: Optional[List[str]] = None,
                   date_posted: str = "week",
                   num_pages: int = 1,
                   country: str = "us",
                   user_skills: Optional[List[str]] = None) -> Dict:
        """
        Search jobs with intelligent caching and career-matching logic
        """
        # Build query with location if provided
        search_query = f"{query} in {location}" if location else query
        
        # Simplified parameters to avoid 400 errors
        params = {
            "query": search_query,
            "num_pages": min(num_pages, 10),
            "country": country,
            "date_posted": date_posted
        }
        
        # Only add employment_types if it's not empty
        if employment_types and len(employment_types) > 0:
            params["employment_types"] = ",".join(employment_types)
        
        try:
            response = requests.get(
                f"{_self.BASE_URL}/search-v2",
                headers=_self.headers,
                params=params,
                timeout=30
            )
            
            # Handle different status codes
            if response.status_code == 400:
                try:
                    error_json = response.json()
                    error_msg = str(error_json) if error_json else "Bad Request"
                except:
                    error_msg = response.text[:200] if response.text else "Bad Request"
                st.error(f"❌ API Error 400: {error_msg}")
                st.warning("💡 Check your API key and search parameters")
                return {"data": [], "status": "error", "message": error_msg}
            
            elif response.status_code == 401:
                st.error("❌ API Error 401: Invalid API Key")
                st.warning("💡 Check your JSEARCH_API_KEY in Streamlit secrets")
                return {"data": [], "status": "error", "message": "Invalid API key"}
                
            elif response.status_code == 429:
                st.error("❌ API Error 429: Rate Limit Exceeded")
                st.warning("💡 You've used too many requests. Wait a minute and try again.")
                return {"data": [], "status": "error", "message": "Rate limit"}
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            # Parse JSON response safely
            try:
                data = response.json()
            except ValueError as e:
                st.error(f"❌ Failed to parse API response as JSON")
                st.error(f"Response: {response.text[:300]}")
                return {"data": [], "status": "error", "message": "Invalid JSON response"}
            
            # Validate response structure
            if not isinstance(data, dict):
                st.error(f"❌ API returned unexpected format: {type(data).__name__}")
                st.error(f"Response: {str(data)[:300]}")
                return {"data": [], "status": "error", "message": "Invalid response format"}
            
            # Check for successful status
            if data.get("status") != "OK":
                st.warning(f"⚠️ API returned status: {data.get('status', 'unknown')}")
                if data.get("message"):
                    st.error(f"Message: {data.get('message')}")
            
            # Process jobs if available
            jobs_list = data.get("data", [])
            if not jobs_list:
                st.info("ℹ️ No jobs found for this search")
                return {"data": [], "status": data.get("status", "unknown")}
            
            # Enhance results with Career Compass matching
            processed_jobs = []
            for job in jobs_list:
                if not isinstance(job, dict):
                    continue  # Skip invalid entries
                
                # Add match score based on user profile/skills
                job["career_compass_match_score"] = _self._calculate_match_score(
                    job, query, user_skills
                )
                # Add fetch timestamp
                job["fetched_at"] = datetime.now().isoformat()
                # Normalize salary
                job["normalized_salary"] = _self._normalize_salary(
                    job.get("estimated_salaries")
                )
                processed_jobs.append(job)
            
            # Sort by match score
            processed_jobs.sort(
                key=lambda x: x.get("career_compass_match_score", 0), 
                reverse=True
            )
            
            data["data"] = processed_jobs
            return data
            
        except requests.exceptions.Timeout:
            st.error("⏱️ Job search timed out. Please try again.")
            return {"data": [], "status": "error", "message": "timeout"}
        except Exception as e:
            error_msg = str(e)
            st.error(f"⚠️ Unexpected error: {error_msg}")
            st.info("💡 Try refreshing the page or check your API key")
            return {"data": [], "status": "error", "message": error_msg}
    
    def _calculate_match_score(_self, job: Dict, query: str, 
                            user_skills: Optional[List[str]] = None) -> float:
        """
        Calculate relevance score (0.0 to 1.0) based on job match
        """
        if not isinstance(job, dict):
            return 0.0
            
        job_description = job.get("job_description", "")
        if not job_description:
            return 0.0
        
        score = 0.0
        job_text = f"{job.get('job_title', '')} {job_description}".lower()
        
        # 1. Query keyword matching (40% weight)
        query_terms = [t.strip().lower() for t in query.split() if len(t) > 3]
        if query_terms:
            matches = sum(1 for term in query_terms if term in job_text)
            score += 0.4 * (matches / len(query_terms))
        
        # 2. Skills alignment (50% weight)
        if user_skills and job.get("job_required_skills"):
            job_skills = [s.lower() for s in job["job_required_skills"]]
            skill_matches = sum(1 for skill in user_skills 
                              if any(skill.lower() in js for js in job_skills))
            score += 0.5 * min(1.0, skill_matches / max(1, len(user_skills)))
        
        # 3. Experience level hint (10% weight)
        exp_keywords = ["senior", "lead", "principal", "junior", "entry", "mid"]
        query_exp = [kw for kw in exp_keywords if kw in query.lower()]
        job_exp = [kw for kw in exp_keywords if kw in job_text]
        if query_exp and job_exp and query_exp[0] == job_exp[0]:
            score += 0.1
        
        return min(1.0, round(score, 2))
    
    def _normalize_salary(_self, salary_data: Optional[List[Dict]]) -> Optional[Dict]:
        """Convert salary estimates to consistent annual USD format"""
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
            
            # Convert to annual if needed
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
    
    def get_job_details(_self, job_id: str) -> Optional[Dict]:
        """Fetch detailed info for a specific job"""
        try:
            response = requests.get(
                f"{_self.BASE_URL}/job-details",
                headers=_self.headers,
                params={"job_id": job_id},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [{}])[0] if data.get("data") else None
        except Exception as e:
            st.warning(f"Could not fetch job details: {e}")
            return None