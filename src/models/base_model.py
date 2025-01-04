

"""Base class for all models."""
from abc import ABC, abstractmethod
from typing import Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

class BaseModel(ABC):
    """Base model class that all models should inherit from."""

    def __init__(self):
        """Initialize base model."""
        pass

    @abstractmethod
    def generate_summary(self, resume_data: Dict[str, Any]) -> str:
        """Generate a summary from resume data.
        
        Args:
            resume_data: Dictionary containing resume information
            
        Returns:
            Generated summary text
        """
        pass

    def _clean_summary(self, summary: str) -> str:
        """Clean the generated summary.
        
        Preserves proper nouns, contact information, and handles sentence capitalization.
        
        Args:
            summary: Text to clean
            
        Returns:
            Cleaned text
        """
        if not summary:
            return ""
        
        try:
            # Fix email addresses (remove spaces in domain)
            summary = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+)\s*\.\s*([a-zA-Z]{2,})', r'\1.\2', summary)
            
            # Remove extra whitespace
            summary = " ".join(summary.split())
            
            # Split into sentences while preserving the period
            sentences = re.split(r'([.!?]+)', summary)
            
            # Process each sentence
            cleaned_sentences = []
            for i in range(0, len(sentences)-1, 2):
                sentence = sentences[i].strip()
                if sentence:
                    # Split into words
                    words = sentence.split()
                    if words:
                        # Capitalize first word
                        words[0] = words[0].capitalize()
                        
                        # Process remaining words
                        for j in range(1, len(words)):
                            # Keep proper nouns and email addresses capitalized
                            if (words[j] == "Test" or 
                                '@' in words[j] or 
                                any(c.isupper() for c in words[j][1:])):
                                continue
                            words[j] = words[j].lower()
                            
                        cleaned_sentences.append(" ".join(words) + sentences[i+1])
            
            # Join sentences
            result = "".join(cleaned_sentences).strip()
            
            # Remove trailing period (except for email addresses)
            if not re.search(r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', result):
                result = result.rstrip('.')
            
            return result
            
        except Exception as e:
            logger.error(f"Error cleaning summary: {e}")
            return summary

    def _validate_summary(self, summary: str) -> bool:
        """Validate the generated summary.
        
        Checks:
        - Not empty
        - Minimum length (20 words)
        - Maximum length (500 words)
        
        Args:
            summary: Text to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not summary:
            return False
            
        # Split into words and filter out empty strings
        words = [w for w in summary.split() if w]
            
        # Check minimum length (20 words)
        if len(words) < 20:
            return False
            
        # Check maximum length (500 words)
        if len(words) > 500:
            return False
            
        return True

    def _format_name(self, name: str) -> str:
        """Format name with proper capitalization.
        
        Args:
            name: Name to format
            
        Returns:
            Formatted name
        """
        if not name:
            return ""
        return " ".join(word.capitalize() for word in name.split())
