import sys
import os
from typing import List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities import JobDescription
from services import RecruitmentMatchingService
from dao import CommunicationAgent
from utilities import FileUtils
from config.settings import RESUME_FOLDER

def main():
    try:
        print(f"\nLooking for resume files in: {RESUME_FOLDER}")
        resume_files = FileUtils.get_resume_files(RESUME_FOLDER)
        
        if not resume_files:
            print(f"No resume files found in '{RESUME_FOLDER}' folder.")
            print("Please add PDF or DOCX resume files to the folder and try again.")
            return
        
        print(f"Found {len(resume_files)} resume files:")
        for i, file_path in enumerate(resume_files, 1):
            print(f"   {i}. {os.path.basename(file_path)}")
        
        print(f"\nStarting recruitment matching process...")

        job_description = JobDescription(
            id="JD_001",
            title="Senior Python Developer",
            required_skills=["Python", "Django", "PostgreSQL", "AWS", "Docker", "REST API", "Git"],
            experience_required="5+ years",
            raw_text="""
            We are looking for a Senior Python Developer with 5+ years of experience 
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
            - Bachelor's degree in Computer Science or related field
            """
        )
        matching_service = RecruitmentMatchingService()
        result = matching_service.run_matching_process(job_description, resume_files)
        
        print("\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
        print(f"Total Profiles Processed: {result['total_profiles']}")
        print(f"Qualified Matches: {result['qualified_matches']}")
        print(f"Top Matches: {result['top_matches']}")
        
        if result['matches']:
            print(f"\nTop {len(result['matches'])} Candidates:")
            for i, match in enumerate(result['matches'], 1):
                print(f"{i}. {match['name']} (Score: {match['similarity_score']:.3f})")
        
        send_email = input("\nSend email notifications? (y/n): ").strip().lower()
        if send_email == 'y':
            ar_email = input("Enter AR Requestor email: ").strip()
            recruiter_email = input("Enter Recruiter email: ").strip()
            
            if ar_email and recruiter_email:
                print("Sending email notifications...")
                comm_agent = CommunicationAgent(ar_email, recruiter_email)
                comm_agent.notify(result)
            else:
                print("Email addresses not provided. Skipping email notifications.")
        
        print("\nProcess completed successfully!")
        print(f"Results saved in: {os.path.abspath('data/outputs/')}")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Please check your configuration and try again.")
    finally:
        print("\nThank you for using the Recruitment Matching System!")

if __name__ == "__main__":
    main()