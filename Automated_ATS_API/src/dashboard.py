import os

# Fetch API URL dynamically so it works locally AND inside Docker networks
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Smart ATS Dashboard", page_icon="🤖", layout="wide")

st.title("🚀 Smart ATS Evaluation Dashboard")
st.markdown("Upload a resume and a job description to instantly get an AI-powered match score and structured profile.")

# We create a clean sidebar for inputs
with st.sidebar:
    st.header("Candidate Input")
    jd_input = st.text_area("Job Description", height=250, placeholder="Paste the target Job Description here...")
    resume_file = st.file_uploader("Upload Candidate Resume (PDF)", type=["pdf"])
    
    # This button triggers the API call
    analyze_btn = st.button("Evaluate Candidate", type="primary", use_container_width=True)

# Main area logic
if analyze_btn:
    if not jd_input or not resume_file:
        st.error("Please provide both a Job Description and a Resume PDF.")
    else:
        with st.spinner("AI is crunching the vectors and extracting JSON..."):
            # Prepare the multipart form-data to send to our FastAPI backend
            files = {"resume": (resume_file.name, resume_file.getvalue(), "application/pdf")}
            data = {"job_description": jd_input}
            
            try:
                # Make a POST request to our dynamically routed API
                response = requests.post(f"{API_URL}/evaluate-resume", files=files, data=data)
                response.raise_for_status()
                result = response.json()
                
                st.success("Analysis Complete & Saved to Database!")
                
                # Extract variables for clean UI display
                score = result.get("match_score", 0)
                profile = result.get("candidate_profile", {})
                
                # Create a two-column layout
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Streamlit metrics look really cool for dashboards
                    st.metric(label="AI Semantic Match Score", value=f"{score}%")
                    st.markdown("---")
                    st.write(f"**🆔 DB Candidate ID:** #{result.get('candidate_id')}")
                    st.write(f"**👤 Name:** {profile.get('name')}")
                    st.write(f"**📧 Email:** {profile.get('email')}")
                    st.write(f"**💼 Experience:** {profile.get('years_of_experience')} Years")
                    
                with col2:
                    st.subheader("🤖 AI Summary")
                    st.info(profile.get('summary'))
                    
                    st.subheader("⚡ Extracted Skills")
                    skills = profile.get('skills', [])
                    
                    # Create nice visual tags for skills using some basic HTML/CSS injection
                    skills_html = " ".join([
                        f"<span style='background-color:#1E88E5; padding:4px 10px; border-radius:15px; color:white; font-size:14px; margin-right:5px; display:inline-block; margin-bottom:5px;'>{s}</span>" 
                        for s in skills
                    ])
                    st.markdown(skills_html, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Error connecting to API. Is the FastAPI server running? Details: {e}")
