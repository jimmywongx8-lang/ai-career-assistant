with tab5:
    st.header("📧 AI Cover Letter Generator")
    st.markdown("Generate personalized cover letters in seconds")
    
    if not st.session_state.cv_text:
        st.warning("⚠️ Please upload your CV first.")
    else:
        # Option to select from saved jobs or enter manually
        cover_letter_option = st.radio(
            "Choose how to provide job details:",
            ["📋 Select from my saved jobs", "✍️ Enter job details manually"],
            key="cover_letter_option_select"
        )
        
        company_name = ""
        job_title = ""
        job_desc = ""
        
        if cover_letter_option == "📋 Select from my saved jobs":
            if st.session_state.saved_jobs:
                job_options = [f"{job.get('job_title', 'Job')} at {job.get('employer_name', 'Company')}" 
                              for job in st.session_state.saved_jobs]
                selected_job = st.selectbox(
                    "Select a job to generate cover letter for:",
                    job_options,
                    key="saved_job_selector_cover_letter"
                )
                
                # Get the full job details
                selected_idx = job_options.index(selected_job)
                selected_job_data = st.session_state.saved_jobs[selected_idx]
                
                company_name = selected_job_data.get("employer_name", "")
                job_title = selected_job_data.get("job_title", "")
                job_desc = selected_job_data.get("job_description", "")
                
                st.info(f"📄 Using details from **{selected_job}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Company", value=company_name, disabled=True, key="cl_company_disabled")
                with col2:
                    st.text_input("Job Title", value=job_title, disabled=True, key="cl_title_disabled")
                
                if job_desc:
                    with st.expander("👀 Preview job description"):
                        st.write(job_desc[:500] + "..." if len(job_desc) > 500 else job_desc)
            else:
                st.warning("You haven't saved any jobs yet. Please save jobs from the Jobs tab first.")
                col1, col2 = st.columns(2)
                with col1:
                    company_name = st.text_input("🏢 Company Name", placeholder="e.g., Google, Microsoft", key="cl_company_manual")
                with col2:
                    job_title = st.text_input("💼 Job Title", placeholder="e.g., Software Engineer", key="cl_title_manual")
                job_desc = st.text_area("📝 Job Description (Optional)", height=150, placeholder="Paste job description...", key="cl_desc_manual")
        else:
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("🏢 Company Name", placeholder="e.g., Google, Microsoft", key="cl_company_manual2")
            with col2:
                job_title = st.text_input("💼 Job Title", placeholder="e.g., Software Engineer", key="cl_title_manual2")
            job_desc = st.text_area("📝 Job Description (Optional)", height=150, placeholder="Paste the job description for a more targeted cover letter...", key="cl_desc_manual2")
        
        if st.button("✍️ Generate Cover Letter", key="btn_generate_cover_letter", type="primary", use_container_width=True):
            if not company_name or not job_title:
                st.warning("Please fill in company name and job title")
            else:
                with st.spinner("🤖 Writing your cover letter..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        prompt = f"""
                        Write a professional cover letter for the following:
                        
                        My CV: {st.session_state.cv_text[:1500]}
                        Company: {company_name}
                        Position: {job_title}
                        Job Details: {job_desc[:500] if job_desc else "Not provided"}
                        
                        Make it professional, concise (300-400 words), and highlight relevant skills.
                        Use a friendly but professional tone.
                        """
                        
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=600
                        )
                        
                        st.success("✅ Cover Letter Generated!")
                        st.text_area("Your Cover Letter", response.choices[0].message.content, height=400, key="cover_letter_output")
                        
                        st.download_button(
                            "📥 Download Cover Letter",
                            data=response.choices[0].message.content,
                            file_name="cover_letter.txt",
                            mime="text/plain",
                            key="download_cover_letter"
                        )
                    except Exception as e:
                        st.error(f"Generation failed: {e}")