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
        # Validate query - ensure it's not empty
        if not query or not query.strip():
            st.error("❌ Please enter a job title or search term")
            return {"data": [], "status": "error", "message": "Query is required"}
        
        # Build query properly - handle empty location
        search_query = query.strip()
        if location and location.strip():
            search_query = f"{search_query} in {location.strip()}"
        
        # Debug info (remove after testing)
        st.info(f"🔍 Searching for: '{search_query}'")
        
        # Build parameters
        params = {
            "query": search_query,  # This is now guaranteed to have content
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
                    continue
                
                job["career_compass_match_score"] = _self._calculate_match_score(
                    job, query, user_skills
                )
                job["fetched_at"] = datetime.now().isoformat()
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