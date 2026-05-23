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

    @st.cache_data(ttl=1800, show_spinner="Searching for jobs...")
    def search_jobs(_self, query, location=None, employment_types=None, 
                   date_posted="all", num_pages=1, country="us", user_skills=None):
        
        if not query:
            return {"data": [], "status": "error", "message": "No query provided"}
        
        # Build search query
        search_query = query.strip()
        if location and location.strip():
            search_query = f"{search_query} in {location.strip()}"
        
        # Minimal parameters for better results
        params = {
            "query": search_query,
            "num_pages": "1",  # Keep it simple
        }
        
        # Only add optional params if they have values
        if date_posted and date_posted != "all":
            params["date_posted"] = date_posted
        
        if employment_types and len(employment_types) > 0:
            params["employment_types"] = ",".join(employment_types)
        
        try:
            response = requests.get(
                f"{_self.BASE_URL}/search-v2",
                headers=_self.headers,
                params=params,
                timeout=60
            )
            
            st.write(f"**HTTP Status:** {response.status_code}")
            
            if response.status_code != 200:
                st.error(f"❌ HTTP Error {response.status_code}")
                st.write(response.text[:500])
                return {"data": [], "status": "error", "message": f"HTTP {response.status_code}"}
            
            try:
                result = response.json()
            except Exception as e:
                st.error(f"❌ JSON parse error: {e}")
                return {"data": [], "status": "error", "message": "Invalid JSON"}
            
            # Check API response status
            if result.get("status") != "OK":
                error_msg = result.get("message", "Unknown error")
                st.error(f"❌ API Error: {error_msg}")
                return {"data": [], "status": "error", "message": error_msg}
            
            jobs = result.get("data", [])
            
            if not jobs:
                st.warning("⚠️ No jobs found. Try:")
                st.info("• Different search terms (e.g., 'python', 'engineer')")
                st.info("• Removing location filter")
                st.info("• Checking RapidAPI subscription status")
                return {"data": [], "status": "OK", "message": "No jobs found"}
            
            # Process jobs
            processed_jobs = []
            for job in jobs:
                if not isinstance(job, dict):
                    continue
                
                try:
                    # Add match score
                    job["career_compass_match_score"] = _self._calculate_match_score(
                        job, query, user_skills
                    )
                    job["fetched_at"] = datetime.now().isoformat()
                    job["normalized_salary"] = _self._normalize_salary(
                        job.get("estimated_salaries")
                    )
                    processed_jobs.append(job)
                except Exception as e:
                    st.warning(f"⚠️ Error processing job: {e}")
                    continue
            
            if not processed_jobs:
                return {"data": [], "status": "OK", "message": "No valid jobs"}
            
            # Sort by match score
            processed_jobs.sort(
                key=lambda x: x.get("career_compass_match_score", 0), 
                reverse=True
            )
            
            result["data"] = processed_jobs
            st.success(f"✅ Found {len(processed_jobs)} jobs!")
            
            return result
            
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out")
            return {"data": [], "status": "error", "message": "timeout"}
        except Exception as e:
            st.error(f"❌ Request failed: {e}")
            return {"data": [], "status": "error", "message": str(e)}
    
    def _calculate_match_score(_self, job, query, user_skills=None):
        """Calculate how well the job matches the user's profile"""
        if not isinstance(job, dict):
            return 0.0
        
        score = 0.0
        job_text = (
            str(job.get("job_title", "")).lower() + " " + 
            str(job.get("job_description", "")).lower()
        )
        
        # Query match (40% weight)
        query_terms = [t.strip().lower() for t in query.split() if len(t) > 3]
        if query_terms:
            matches = sum(1 for term in query_terms if term in job_text)
            score += 0.4 * (matches / len(query_terms))
        
        # Skills match (50% weight)
        if user_skills and job.get("job_required_skills"):
            job_skills = [str(s).lower() for s in job["job_required_skills"]]
            skill_matches = sum(
                1 for skill in user_skills 
                if any(skill.lower() in js for js in job_skills)
            )
            score += 0.5 * min(1.0, skill_matches / max(1, len(user_skills)))
        
        return round(min(1.0, score), 2)
    
    def _normalize_salary(_self, salary_data):
        """Normalize salary information"""
        if not salary_data or not isinstance(salary_data, list):
            return None
        
        try:
            salary = salary_data[0]
            if not isinstance(salary, dict):
                return None
            
            min_sal = salary.get("min", 0)
            max_sal = salary.get("max", 0)
            period = salary.get("period", "YEAR").upper()
            
            # Convert to annual USD
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