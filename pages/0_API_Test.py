import streamlit as st
import requests

st.set_page_config(page_title="API Test", page_icon="🧪")

st.title("🧪 JSearch API Test")
st.markdown("Test if your RapidAPI key is working correctly")

if "JSEARCH_API_KEY" in st.secrets:
    api_key = st.secrets["JSEARCH_API_KEY"]
    st.success("✅ API Key found in secrets")
    st.write(f"Key starts with: `{api_key[:20]}...`")
    
    if st.button(" Test API Connection", type="primary"):
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
                    data = response.json()
                    if data.get("status") == "OK":
                        jobs = data.get("data", [])
                        st.success(f"✅ API Working! Found {len(jobs)} real jobs")
                        
                        if jobs:
                            st.write("**Sample Job:**")
                            st.json(jobs[0])
                    else:
                        st.error(f"❌ API returned error: {data.get('message')}")
                elif response.status_code == 401:
                    st.error("❌ Invalid API Key (401)")
                    st.info("Check your API key in Streamlit secrets")
                elif response.status_code == 429:
                    st.error("❌ Rate Limit Exceeded (429)")
                    st.info("You've used up your free tier quota")
                else:
                    st.error(f"❌ HTTP Error: {response.status_code}")
                    st.write(response.text[:500])
                    
            except Exception as e:
                st.error(f"❌ Request failed: {e}")
else:
    st.error("❌ JSEARCH_API_KEY not found in secrets")
    st.info("Add it in Streamlit Cloud Settings > Secrets")