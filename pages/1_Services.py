# TAB 3: JOBS
with tab3:
    st.header("AI-Powered Job Matching")
    st.markdown("Find jobs that match your skills and experience")
    
    if JSearchClient is None:
        st.error("Job matching module not loaded")
    else:
        # Smart job search - let user specify role or extract from CV
        if st.session_state.cv_text:
            # Try to extract target role from CV or let user specify
            st.markdown("**🎯 What type of roles are you looking for?**")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                target_role = st.text_input(
                    "Target Job Title",
                    placeholder="e.g., Strategy Consultant, Business Analyst, Product Manager",
                    help="Enter the type of role you're targeting",
                    key="target_role_input"
                )
            with col2:
                search_location = st.text_input(
                    "Location",
                    placeholder="Remote, New York, etc.",
                    key="search_location_input"
                )
            
            # Smart skill extraction based on CV content
            if st.session_state.cv_text:
                # Detect if CV mentions consulting/strategy terms
                cv_lower = st.session_state.cv_text.lower()
                
                # Common strategy/consulting skills
                strategy_keywords = {
                    "strategy": ["strategy", "strategic planning", "business strategy"],
                    "consulting": ["consulting", "consultant", "advisory"],
                    "analysis": ["analysis", "business analysis", "market research"],
                    "management": ["management", "project management", "program management"],
                    "finance": ["finance", "financial analysis", "financial modeling"],
                    "operations": ["operations", "operations management", "process improvement"],
                    "marketing": ["marketing", "digital marketing", "brand management"],
                    "sales": ["sales", "business development", "account management"]
                }
                
                # Extract relevant skills
                detected_skills = []
                for category, keywords in strategy_keywords.items():
                    for keyword in keywords:
                        if keyword in cv_lower:
                            detected_skills.append(category.title())
                            break
                
                # Also check for technical skills
                tech_skills = ["Python", "SQL", "Excel", "Tableau", "PowerBI", "Salesforce", "SAP"]
                for skill in tech_skills:
                    if skill.lower() in cv_lower:
                        detected_skills.append(skill)
                
                if detected_skills:
                    st.info(f"💡 **Detected Skills:** {', '.join(detected_skills[:8])}")
                else:
                    st.info("💡 Tip: Add your key skills to your CV for better matching")
        else:
            st.warning("⚠️ Please upload your CV first for personalized job matching")
            target_role = "software developer"
            search_location = ""
            detected_skills = []
        
        # Search button
        if st.button("🔍 Search Jobs", key="btn_search_main", type="primary"):
            # Determine what to search for
            search_query = target_role.strip() if target_role else "consultant"
            
            # Extract skills for matching
            search_skills = detected_skills if detected_skills else ["Strategy", "Analysis", "Management"]
            
            try:
                client = JSearchClient(api_key=st.secrets.get("JSEARCH_API_KEY", "demo-key"))
                results = client.search_jobs(
                    query=search_query,
                    location=search_location if search_location else None,
                    num_pages=1,
                    user_skills=search_skills
                )
                
                st.session_state.search_results = results.get("data", [])
                st.success(f"Found {len(st.session_state.search_results)} jobs for **{search_query}**!")
                
                if not target_role:
                    st.info("💡 Tip: Enter your target job title above for better results")
                    
            except Exception as e:
                st.error(f"Error: {e}")
        
        # Display results
        if st.session_state.search_results:
            st.markdown("---")
            for idx, job in enumerate(st.session_state.search_results):
                title = str(job.get("job_title", "Job"))
                company = str(job.get("employer_name", "Company"))
                city = str(job.get("job_city", ""))
                desc = str(job.get("job_description", ""))[:200]
                skills = job.get("job_required_skills", [])
                apply_url = str(job.get("job_apply_link", "#"))
                score = float(job.get("career_compass_match_score", 0))
                salary = job.get("normalized_salary", {})
                
                if score >= 0.7: badge = "🟢 Excellent"
                elif score >= 0.4: badge = "🟡 Good"
                else: badge = "⚪ Match"
                
                is_saved = any(
                    str(s.get("job_title")) == title and str(s.get("employer_name")) == company
                    for s in st.session_state.saved_jobs
                )
                
                st.markdown(f"""
                <div class="job-card">
                    <div style="font-size:24px; font-weight:bold;">{title}</div>
                    <div>🏢 {company} | 📍 {city}</div>
                    <div style="margin-top:10px;"><span class="badge">{badge}</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    if is_saved:
                        st.success("💾 Saved")
                    else:
                        st.info("Click Save to bookmark")
                
                with col2:
                    key = f"save_{idx}_{hashlib.md5(f'{title}{company}'.encode()).hexdigest()}"
                    if st.button("💾 Save", key=key):
                        if is_saved:
                            st.session_state.saved_jobs = [
                                j for j in st.session_state.saved_jobs
                                if not (str(j.get("job_title")) == title and str(j.get("employer_name")) == company)
                            ]
                        else:
                            st.session_state.saved_jobs.append(job.copy())
                        st.rerun()
                
                with st.expander("📋 View Full Job Details"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**📝 Full Description**")
                        st.write(desc if desc else "No description available")
                    
                    with col_b:
                        if skills:
                            st.markdown("**💡 Required Skills**")
                            skills_str = ", ".join(str(s) for s in skills)
                            st.write(skills_str)
                        
                        if salary and salary.get("min_annual_usd"):
                            st.markdown("**💰 Salary Range**")
                            min_sal = salary.get("min_annual_usd", 0)
                            max_sal = salary.get("max_annual_usd", 0)
                            st.info(f"${min_sal:,} - ${max_sal:,} / year")
                    
                    if apply_url and apply_url != "#":
                        st.markdown(f"""
                        <div style="text-align: center; margin-top: 20px;">
                            <a href="{apply_url}" target="_blank" 
                               style="background-color: #667eea; color: white; 
                                      padding: 12px 30px; border-radius: 5px; 
                                      text-decoration: none; font-weight: bold;
                                      display: inline-block;">
                                🚀 Apply Now
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")