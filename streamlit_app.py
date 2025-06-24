import streamlit as st
import os
import tempfile
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict
import sys
from pathlib import Path

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Streamlit configuration
st.set_page_config(
    page_title="Recruitment Matching System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check configuration first
try:
    from config.settings import validate_config, AZURE_TOKEN, EMAIL_ADDRESS, EMAIL_PASSWORD
    
    # Validate configuration
    missing_vars = validate_config()
    if missing_vars:
        st.error("⚠️ **Configuration Error**")
        st.error("The following environment variables are missing or not set:")
        for var in missing_vars:
            st.error(f"• `{var}`")
        
        st.info("**For Azure Web App deployment:**")
        st.code("""
# Set these as Application Settings in Azure Portal:
# Go to: Azure Portal → Your Web App → Configuration → Application Settings

AZURE_OPEN_API = "your_azure_api_key_here"
EMAIL_ADDRESS = "your_email@gmail.com" 
EMAIL_PASSWORD = "your_gmail_app_password"
        """)
        
        st.info("**For local development, create a `.env` file in your project root:**")
        st.code("""
AZURE_OPEN_API=your_azure_api_key_here
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
        """)
        
        st.stop()

except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please check that all required modules are installed and available.")
    st.stop()

# Now import other modules
try:
    from entities import JobDescription, Profile
    from services import RecruitmentMatchingService
    from dao import CommunicationAgent
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please check that all required modules are installed and available.")
    st.stop()

# Custom CSS
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
    .stAlert > div {
        padding: 1rem;
    }
    .config-status {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
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
        # Ensure safe filename
        safe_filename = "".join(c for c in uploaded_file.name if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
        file_path = os.path.join(temp_dir, safe_filename)
        
        try:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)
        except Exception as e:
            st.error(f"Error saving file {safe_filename}: {e}")
            continue
    
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
    
    # Safely handle potentially missing fields
    name = candidate.get('name', 'N/A')
    email = candidate.get('email', 'N/A')
    phone = candidate.get('phone', 'N/A')
    experience = candidate.get('experience', 'N/A')
    education = candidate.get('education', 'N/A')
    similarity_score = candidate.get('similarity_score', 0.0)
    skills = candidate.get('skills', [])
    summary = candidate.get('summary', 'N/A')
    
    st.markdown(f"""
    <div class="candidate-card">
        <h4>#{rank} - {name}</h4>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone}</p>
        <p><strong>Experience:</strong> {experience}</p>
        <p><strong>Education:</strong> {education}</p>
        <p><strong>Similarity Score:</strong> <span class="{score_class}">{similarity_score:.3f}</span></p>
        <p><strong>Skills:</strong> {', '.join(skills) if skills else 'N/A'}</p>
        <p><strong>Summary:</strong> {summary}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">🎯 Recruitment Matching System</h1>', unsafe_allow_html=True)
    
    # Show configuration status
    st.markdown("""
    <div class="config-status">
        ✅ <strong>Configuration Status:</strong> All required environment variables are properly configured.
    </div>
    """, unsafe_allow_html=True)
    
    # Test service initialization
    try:
        test_service = RecruitmentMatchingService()
        st.success("🔧 Service initialized successfully!")
    except Exception as e:
        st.error(f"⚠️ Service initialization failed: {e}")
        st.error("Please check your Azure API configuration.")
        st.stop()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Show current environment
        env_info = os.getenv('WEBSITE_SITE_NAME', 'Local Development')
        st.info(f"Environment: {env_info}")
        
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
        
        # Email configuration
        st.subheader("📧 Email Notifications")
        enable_email = st.checkbox("Enable Email Notifications")
        
        if enable_email:
            ar_email = st.text_input("AR Requestor Email", placeholder="ar@company.com")
            recruiter_email = st.text_input("Recruiter Email", placeholder="recruiter@company.com")
    
    # Main tabs
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
        
        # File upload with better error handling
        uploaded_files = st.file_uploader(
            "Choose resume files",
            accept_multiple_files=True,
            type=['pdf', 'docx'],
            help="Upload PDF or DOCX resume files (max 200MB per file)"
        )
        
        if uploaded_files:
            st.write(f"📁 {len(uploaded_files)} files uploaded:")
            total_size = 0
            for file in uploaded_files:
                file_size_mb = file.size / (1024 * 1024)
                total_size += file_size_mb
                st.write(f"• {file.name} ({file_size_mb:.1f} MB)")
            
            if total_size > 100:  # Warn if total size is large
                st.warning(f"⚠️ Large total file size: {total_size:.1f} MB. Processing may take longer.")
        
        if st.button("🚀 Start Matching Process", type="primary", disabled=not uploaded_files):
            if not st.session_state.job_description:
                st.error("❌ Please save a job description first!")
                return
            
            if not uploaded_files:
                st.error("❌ Please upload resume files first!")
                return
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Save uploaded files
                status_text.text("💾 Saving uploaded files...")
                progress_bar.progress(10)
                file_paths = save_uploaded_files(uploaded_files)
                
                if not file_paths:
                    st.error("❌ Failed to save uploaded files!")
                    return
                
                # Initialize matching service
                status_text.text("🔧 Initializing matching service...")
                progress_bar.progress(20)
                matching_service = RecruitmentMatchingService()
                
                # Set similarity threshold
                matching_service.ranking_agent.min_similarity_threshold = similarity_threshold
                
                # Run matching process
                status_text.text("🔍 Processing resumes and matching...")
                progress_bar.progress(50)
                
                with st.spinner("Processing resumes..."):
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
                
                st.success(f"🎉 Found {len(result.get('matches', []))} top matches out of {result.get('total_profiles', 0)} profiles!")
                
                # Auto-switch to results tab
                st.info("👉 Check the 'Results' tab to view the matching candidates!")
                
            except Exception as e:
                st.error(f"❌ An error occurred during processing: {str(e)}")
                st.error("Please check your configuration and try again.")
                progress_bar.empty()
                status_text.empty()
    
    with tab3:
        st.markdown('<div class="section-header">Matching Results</div>', unsafe_allow_html=True)
        
        if st.session_state.matching_results:
            result = st.session_state.matching_results
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Profiles", result.get('total_profiles', 0))
            
            with col2:
                st.metric("Qualified Matches", result.get('qualified_matches', 0))
            
            with col3:
                st.metric("Top Matches", result.get('top_matches', 0))
            
            with col4:
                matches = result.get('matches', [])
                if matches:
                    avg_score = sum(match.get('similarity_score', 0) for match in matches) / len(matches)
                    st.metric("Avg. Score", f"{avg_score:.3f}")
                else:
                    st.metric("Avg. Score", "N/A")
            
            if result.get('matches'):
                st.subheader("🏆 Top Candidates")
                
                # Display candidates
                for idx, candidate in enumerate(result['matches'], 1):
                    display_candidate_card(candidate, idx)
                
                # Download section
                st.subheader("📥 Download Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # CSV download
                    try:
                        df = pd.DataFrame(result['matches'])
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📊 Download CSV",
                            data=csv,
                            file_name=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    except Exception as e:
                        st.error(f"Error creating CSV: {e}")
                
                with col2:
                    # JSON download
                    try:
                        json_str = json.dumps(result, indent=2)
                        st.download_button(
                            label="📋 Download JSON",
                            data=json_str,
                            file_name=f"match_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    except Exception as e:
                        st.error(f"Error creating JSON: {e}")
                
                # Detailed view toggle
                if st.checkbox("📋 Show Detailed JSON Results"):
                    st.json(result)
            
            else:
                st.warning("⚠️ No qualified candidates found. Try lowering the similarity threshold.")
                
                # Show debug info if available
                if 'error' in result:
                    st.error(f"Error: {result['error']}")
        
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