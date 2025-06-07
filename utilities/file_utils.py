import os
from typing import List
from pathlib import Path

class FileUtils:    
    @staticmethod
    def get_resume_files(folder_path: str) -> List[str]:
        if not os.path.exists(folder_path):
            print(f"Warning: Folder '{folder_path}' does not exist")
            return []
        
        supported_extensions = {'.pdf', '.docx'}
        resume_files = []
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if Path(filename).suffix.lower() in supported_extensions:
                resume_files.append(file_path)
        
        return resume_files
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> None:
        os.makedirs(directory_path, exist_ok=True)
    
    @staticmethod
    def is_valid_file_extension(file_path: str) -> bool:
        supported_extensions = {'.pdf', '.docx'}
        return Path(file_path).suffix.lower() in supported_extensions