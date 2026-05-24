import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def fetch_jobs_from_api(location="Singapore", keyword="strategy", max_results=10):
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("RAPIDAPI_KEY not found - using local jobs")
        return []
    
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": f"{keyword} {location}",
        "num_pages": "1"
    }
    
    try:
        print("Fetching jobs from API...")
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            jobs_raw = data.get("data", [])
            
            jobs = []
            for job in jobs_raw[:max_results]:
                jobs.append({
                    "title": job.get("job_title", "Unknown"),
                    "company": job.get("employer_name", "Unknown"),
                    "location": job.get("job_country", "Remote"),
                    "description": job.get("job_description", "")[:1500],
                    "apply_link": job.get("job_apply_link", "#"),
                    "source": "JSearch"
                })
            
            return jobs
        return []
    except Exception as e:
        print(f"API Error: {e}")
        return []

def load_local_jobs():
    jobs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "real_jobs.json")
    if os.path.exists(jobs_path):
        with open(jobs_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_all_jobs(location="Singapore", keyword="strategy", max_results=10):
    api_jobs = fetch_jobs_from_api(location, keyword, max_results)
    
    if api_jobs:
        print(f"Using {len(api_jobs)} jobs from API")
        return api_jobs
    
    print("Using local jobs")
    return load_local_jobs()[:max_results]