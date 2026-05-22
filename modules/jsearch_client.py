import requests
import streamlit as st
from datetime import datetime
import time

class JSearchClient:
    BASE_URL = "https://jsearch.p.rapidapi.com"

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

    @st.cache_data(ttl=1800)
    def search_jobs(_self, query, location=None, employment_types=None, 
                   date_posted="all", num_pages=1, country="us", user_skills=None):
        
        if not query:
            return {"data": [], "status": "error"}
        
        search_query = query
        if location:
            search_query = query + " in " + location
        
        params = {
            "query": search_query,
            "num_pages": min(num_pages, 10),
            "country": country,
            "date_posted": date_posted
        }
        
        if employment_types:
            params["employment_types"] = ",".join(employment_types)
        
        try:
            response = requests.get(
                _self.BASE_URL + "/search-v2",
                headers=_self.headers,
                params=params,
                timeout=60
            )
            
            if response.status_code != 200:
                st.error("API Error: " + str(response.status_code))
                return {"data": [], "status": "error"}
            
            data = response.json()
            jobs_list = data.get("data", [])
            
            if not jobs_list:
                return {"data": [], "status": "ok"}
            
            for job in jobs_list:
                job["career_compass_match_score"] = 0.5
                job["fetched_at"] = datetime.now().isoformat()
                job["normalized_salary"] = None
            
            return data
            
        except Exception as e:
            st.error("Error: " + str(e))
            return {"data": [], "status": "error"}
