
from abc import ABC, abstractmethod
from typing import Optional


class BaseResumeParser(ABC):
    """Abstract base class for resume parsing"""
    
    @abstractmethod
    def parse_resume(self, file_path) -> str:
        """Parse the resume and return structured data"""
        pass
    
    @abstractmethod
    def parse_personal_info(self, text, is_first_line):
        """Parse personal information from the line"""
        pass
    
    @abstractmethod
    def parse_position(self, text) -> Optional[dict]:
        """Parse position/experience information from the line"""
        pass
    
    @abstractmethod
    def parse_education(self, text):
        """Parse education information from the line"""
        pass
    
    @abstractmethod
    def parse_skills(self, text):
        """Parse skills from the line"""
        pass
    
    @abstractmethod
    def parse_interests(self, text):
        """Parse interests/activities from the line"""
        pass
    
    @abstractmethod
    def clean_up_data(self):
        """Clean and validate the parsed data"""
        pass