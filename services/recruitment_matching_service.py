from typing import List, Dict
from datetime import datetime
from entities import Profile, JobDescription
from dao import DocumentReader, AzureExtractor, ComparisonAgent, RankingAgent
from utilities import ExportUtils

class RecruitmentMatchingService:
    
    def __init__(self):
        self.document_reader = DocumentReader()
        self.extractor = AzureExtractor()
        self.comparison_agent = ComparisonAgent()
        self.ranking_agent = RankingAgent()
        self.export_utils = ExportUtils()

    def process_resume_files(self, resume_files: List[str]) -> List[Profile]:
        profiles = []
        
        print(f"Processing {len(resume_files)} resume files...")
        
        for idx, file_path in enumerate(resume_files):
            print(f"Processing file {idx+1}/{len(resume_files)}: {file_path}")
            
            text = self.document_reader.read_document(file_path)
            if not text:
                print(f"Warning: Could not extract text from {file_path}")
                continue
            
            info = self.extractor.extract_resume_info(text)
            if not info:
                print(f"Warning: Could not extract info from {file_path}")
                continue
            
            profile = Profile(
                id=f"profile_{idx+1}",
                name=info.get("name", f"Candidate_{idx+1}"),
                email=info.get("email", ""),
                phone=info.get("phone", ""),
                skills=info.get("skills", []),
                experience=f"{info.get('experience_years', '0')} years",
                education=info.get("education", ""),
                summary=info.get("summary", ""),
                raw_text=text
            )
            
            profiles.append(profile)
            print(f"Successfully processed: {profile.name}")
        
        print(f"\nSuccessfully processed {len(profiles)} profiles")
        return profiles

    def run_matching_process(self, job_description: JobDescription, resume_files: List[str]) -> Dict:
        """Run the complete matching process"""
        print(f"Starting recruitment matching process...")
        print(f"Job Description: {job_description.title} (ID: {job_description.id})")
        
        profiles = self.process_resume_files(resume_files)
        
        if not profiles:
            print("No profiles were successfully processed.")
            return self._create_empty_result(job_description)
        
        print(f"\nComparing {len(profiles)} profiles with job description...")
        scored_profiles = self.comparison_agent.compare_profiles_with_jd(job_description, profiles)
        
        print("Ranking profiles...")
        top_matches = self.ranking_agent.get_top_matches(scored_profiles)
        
        self.export_utils.print_ranking_summary(scored_profiles)
        
        if top_matches:
            self.export_utils.export_to_csv(top_matches)
        
        # Step 6: Creat result summary
        result = self._create_match_result(job_description, profiles, top_matches)
        
        self.export_utils.export_to_json(result)
        
        print(f"\nMatching process completed. Found {len(top_matches)} top matches.")
        return result

    def _create_match_result(self, job_description: JobDescription, all_profiles: List[Profile], top_matches: List[Profile]) -> Dict:
        """Create structured match result"""
        return {
            "job_id": job_description.id,
            "job_title": job_description.title,
            "total_profiles": len(all_profiles),
            "qualified_matches": len([p for p in all_profiles if p.similarity_score >= self.ranking_agent.min_similarity_threshold]),
            "top_matches": len(top_matches),
            "matches": [profile.to_dict() for profile in top_matches],
            "timestamp": datetime.now().isoformat(),
            "processing_summary": {
                "min_similarity_threshold": self.ranking_agent.min_similarity_threshold,
                "top_candidates_limit": 3
            }
        }
    
    def _create_empty_result(self, job_description: JobDescription) -> Dict:
        """Create empty result when no profiles are processed"""
        return {
            "job_id": job_description.id,
            "job_title": job_description.title,
            "total_profiles": 0,
            "qualified_matches": 0,
            "top_matches": 0,
            "matches": [],
            "timestamp": datetime.now().isoformat(),
            "error": "No profiles were successfully processed"
        }