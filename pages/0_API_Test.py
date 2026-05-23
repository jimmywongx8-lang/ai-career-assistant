import streamlit as st
import requests

st.set_page_config(page_title="API Test", page_icon="🧪")

st.title("🧪 JSearch API Test")
st.markdown("Test if your RapidAPI key is working correctly")

if "JSEARCH_API_KEY" in st.secrets:
    api_key = st.secrets["JSEARCH_API_KEY"]
    st.success("✅ API Key found in secrets")
    st.write(f"Key starts with: `{api_key[:20]}...`")
    
    if st.button("🚀 Test API Connection", type="primary"):
        with st.spinner("Testing API..."):
            try:
                headers = {
                    "X-RapidAPI-Key": api_key,
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
                }
                
                params = {
                    "query": "software developer",
                    "num_pages": "1"
                }
                
                response = requests.get(
                    "https://jsearch.p.rapidapi.com/search-v2",
                    headers=headers,
                    params=params,
                    timeout=10
                )
                
                st.write(f"**HTTP Status Code:** {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        st.write("**Full Response:**")
                        st.json(data)  # Show entire response for debugging
                        
                        if data.get("status") == "OK":
                            jobs = data.get("data", [])
                            st.success(f"✅ API Working! Found {len(jobs)} real jobs")
                            
                            if len(jobs) > 0:
                                st.write("**First Job Details:**")
                                st.write(f"Title: {jobs[0].get('job_title', 'N/A')}")
                                st.write(f"Company: {jobs[0].get('employer_name', 'N/A')}")
                    except Exception as parse_error:
                        st.error(f"Error parsing JSON: {parse_error}")
                        st.code(response.text[:500])
                elif response.status_code == 401:
                    st.error("❌ Invalid API Key (401)")
                elif response.status_code == 429:
                    st.error("❌ Rate Limit Exceeded (429)")
                else:
                    st.error(f"❌ HTTP Error: {response.status_code}")
                    st.write(response.text[:500])
                    
            except Exception as e:
                st.error(f"❌ Request failed: {e}")
else:
    st.error("❌ JSEARCH_API_KEY not found in secrets")