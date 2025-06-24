import streamlit as st
import os
import tempfile
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict
import sys
from pathlib import Path


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities import JobDescription, Profile
from services import RecruitmentMatchingService
from dao import CommunicationAgent


st.set_page_config(
    page_title="Recruitment Matching System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .candidate-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .score-high {
        color: #28a745;
        font-weight: bold;
    }
    .score-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .score-low {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'matching_results' not in st.session_state:
        st.session_state.matching_results = None
    if 'processed_profiles' not in st.session_state:
        st.session_state.processed_profiles = []
    if 'job_description' not in st.session_state:
        st.session_state.job_description = None

def save_uploaded_files(uploaded_files) -> List[str]:
    """Save uploaded files to temporary directory and return file paths"""
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(file_path)
    
    return file_paths

def get_score_class(score: float) -> str:
    """Return CSS class based on similarity score"""
    if score >= 0.7:
        return "score-high"
    elif score >= 0.4:
        return "score-medium"
    else:
        return "score-low"

def display_candidate_card(candidate: Dict, rank: int):
    """Display a candidate card with styling"""
    score_class = get_score_class(candidate['similarity_score'])
    
    st.markdown(f"""
    <div class="candidate-card">
        <h4>#{rank} - {candidate['name']}</h4>
        <p><strong>Email:</strong> {candidate['email']}</p>
        <p><strong>Phone:</strong> {candidate['phone']}</p>
        <p><strong>Experience:</strong> {candidate['experience']}</p>
        <p><strong>Education:</strong> {candidate['education']}</p>
        <p><strong>Similarity Score:</strong> <span class="{score_class}">{candidate['similarity_score']:.3f}</span></p>
        <p><strong>Skills:</strong> {', '.join(candidate['skills'])}</p>
        <p><strong>Summary:</strong> {candidate['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">🎯 Recruitment Matching System</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Similarity threshold
        similarity_threshold = st.slider(
            "Minimum Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05,
            help="Minimum similarity score required for a candidate to be considered"
        )
        
        # Top matches limit
        top_matches_limit = st.number_input(
            "Top Matches Limit",
            min_value=1,
            max_value=20,
            value=3,
            help="Maximum number of top candidates to display"
        )
        
        st.divider()
        
        
        st.subheader("📧 Email Notifications")
        enable_email = st.checkbox("Enable Email Notifications")
        
        if enable_email:
            ar_email = st.text_input("AR Requestor Email", placeholder="ar@company.com")
            recruiter_email = st.text_input("Recruiter Email", placeholder="recruiter@company.com")
    
    
    tab1, tab2, tab3 = st.tabs(["📝 Job Description", "📄 Upload Resumes", "📊 Results"])
    
    with tab1:
        st.markdown('<div class="section-header">Job Description</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            job_title = st.text_input("Job Title", value="Senior Python Developer")
            
            job_description_text = st.text_area(
                "Job Description",
                height=300,
                value="""We are looking for a Senior Python Developer with 5+ years of experience 
in Python development. The ideal candidate should have strong experience 
with Django framework, PostgreSQL database, AWS cloud services, Docker 
containerization, REST API development, and Git version control.

Responsibilities:
- Develop and maintain web applications using Python and Django
- Design and implement REST APIs
- Work with PostgreSQL databases
- Deploy applications on AWS infrastructure
- Collaborate with cross-functional teams
- Write clean, maintainable code

Requirements:
- 5+ years of Python development experience
- Strong knowledge of Django framework
- Experience with PostgreSQL
- AWS cloud services experience
- Docker containerization knowledge
- Git version control proficiency
- Bachelor's degree in Computer Science or related field""",
                help="Enter the complete job description including requirements and responsibilities"
            )
        
        with col2:
            st.subheader("Required Skills")
            skills_input = st.text_area(
                "Skills (one per line)",
                height=200,
                value="Python\nDjango\nPostgreSQL\nAWS\nDocker\nREST API\nGit",
                help="Enter each required skill on a new line"
            )
            
            experience_required = st.text_input("Experience Required", value="5+ years")
        
        if st.button("💾 Save Job Description", type="primary"):
            required_skills = [skill.strip() for skill in skills_input.split('\n') if skill.strip()]
            
            st.session_state.job_description = JobDescription(
                id=f"JD_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=job_title,
                required_skills=required_skills,
                experience_required=experience_required,
                raw_text=job_description_text
            )
            
            st.success("✅ Job description saved successfully!")
    
    with tab2:
        st.markdown('<div class="section-header">Upload Resume Files</div>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose resume files",
            accept_multiple_files=True,
            type=['pdf', 'docx'],
            help="Upload PDF or DOCX resume files"
        )
        
        if uploaded_files:
            st.write(f"📁 {len(uploaded_files)} files uploaded:")
            for file in uploaded_files:
                st.write(f"• {file.name} ({file.size} bytes)")
        
        if st.button("🚀 Start Matching Process", type="primary", disabled=not uploaded_files):
            if not st.session_state.job_description:
                st.error("❌ Please save a job description first!")
                return
            
            if not uploaded_files:
                st.error("❌ Please upload resume files first!")
                return
            
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                
                status_text.text("💾 Saving uploaded files...")
                progress_bar.progress(10)
                file_paths = save_uploaded_files(uploaded_files)
                
                
                status_text.text("🔧 Initializing matching service...")
                progress_bar.progress(20)
                matching_service = RecruitmentMatchingService()
                
                matching_service.ranking_agent.min_similarity_threshold = similarity_threshold
                
                
                status_text.text("🔍 Processing resumes and matching...")
                progress_bar.progress(50)
                
                result = matching_service.run_matching_process(
                    st.session_state.job_description, 
                    file_paths
                )
                
                progress_bar.progress(80)
                
                # Store results
                st.session_state.matching_results = result
                
                # Send email notifications if enabled
                if enable_email and ar_email and recruiter_email:
                    status_text.text("📧 Sending email notifications...")
                    progress_bar.progress(90)
                    
                    try:
                        comm_agent = CommunicationAgent(ar_email, recruiter_email)
                        comm_agent.notify(result)
                        st.success("📧 Email notifications sent successfully!")
                    except Exception as e:
                        st.warning(f"⚠️ Email notification failed: {str(e)}")
                
                progress_bar.progress(100)
                status_text.text("✅ Matching process completed!")
                
                # Clean up temporary files
                for file_path in file_paths:
                    try:
                        os.remove(file_path)
                    except:
                        pass
                
                st.success(f"🎉 Found {len(result['matches'])} top matches out of {result['total_profiles']} profiles!")
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                progress_bar.empty()
                status_text.empty()
    
    with tab3:
        st.markdown('<div class="section-header">Matching Results</div>', unsafe_allow_html=True)
        
        if st.session_state.matching_results:
            result = st.session_state.matching_results
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Profiles", result['total_profiles'])
            
            with col2:
                st.metric("Qualified Matches", result['qualified_matches'])
            
            with col3:
                st.metric("Top Matches", result['top_matches'])
            
            with col4:
                avg_score = sum(match['similarity_score'] for match in result['matches']) / len(result['matches']) if result['matches'] else 0
                st.metric("Avg. Score", f"{avg_score:.3f}")
            
            if result['matches']:
                st.subheader("🏆 Top Candidates")
                
                # Display candidates
                for idx, candidate in enumerate(result['matches'], 1):
                    display_candidate_card(candidate, idx)
                
                # Download section
                st.subheader("📥 Download Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # CSV download
                    df = pd.DataFrame(result['matches'])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv,
                        file_name=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # JSON download
                    json_str = json.dumps(result, indent=2)
                    st.download_button(
                        label="📋 Download JSON",
                        data=json_str,
                        file_name=f"match_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                # Detailed view toggle
                if st.checkbox("📋 Show Detailed JSON Results"):
                    st.json(result)
            
            else:
                st.warning("⚠️ No qualified candidates found. Try lowering the similarity threshold.")
        
        else:
            st.info("👆 Upload resumes and run the matching process to see results here.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
        "🎯 Recruitment Matching System | Built with Streamlit"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()