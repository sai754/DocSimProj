import csv
import json
import os
from typing import List, Dict
from entities import Profile
from config.settings import OUTPUT_FOLDER, DEFAULT_CSV_FILENAME
from .file_utils import FileUtils

class ExportUtils:    
    @staticmethod
    def export_to_csv(profiles: List[Profile], filename: str = None) -> str:
        if filename is None:
            filename = DEFAULT_CSV_FILENAME
        
        FileUtils.ensure_directory_exists(OUTPUT_FOLDER)
        
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Name", "Email", "Phone", "Similarity Score", 
                "Experience", "Education", "Skills", "Summary"
            ])
            
            for profile in profiles:
                writer.writerow([
                    profile.name,
                    profile.email,
                    profile.phone,
                    f"{profile.similarity_score:.2f}",
                    profile.experience,
                    profile.education,
                    ", ".join(profile.skills),
                    profile.summary
                ])
        
        print(f"Results exported to: {file_path}")
        return file_path
    
    @staticmethod
    def export_to_json(match_result: Dict, filename: str = "match_results.json") -> str:
        # Ensure outut directory exists
        FileUtils.ensure_directory_exists(OUTPUT_FOLDER)
        
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(match_result, file, indent=2, ensure_ascii=False)
        
        print(f"Match results exported to: {file_path}")
        return file_path
    
    @staticmethod
    def print_ranking_summary(profiles: List[Profile]) -> None:
        print("\n" + "="*60)
        print("CANDIDATE RANKING SUMMARY")
        print("="*60)
        
        sorted_profiles = sorted(profiles, key=lambda x: x.similarity_score, reverse=True)
        
        for idx, profile in enumerate(sorted_profiles, 1):
            print(f"{idx:2d}. {profile.name:<25} | Score: {profile.similarity_score:.3f} | {profile.email}")
        
        print("="*60)