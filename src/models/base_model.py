"""Base class for all resume models."""
import re
from abc import ABC, abstractmethod
from config.model_prompts import SUMMARY_TEMPLATES

class BaseResumeModel(ABC):
    def __init__(self):
        """Initialize base model with default configuration."""
        self.config = {
            'model': {
                'name': None,
                'generation_params': {
                    'max_length': 256,
                    'num_beams': 4,
                    'length_penalty': 2.0,
                    'early_stopping': True,
                    'no_repeat_ngram_size': 2,
                    'temperature': 0.7
                }
            },
            'formatting': {
                'max_achievements': 2,
                'max_skills': 5,
                'skill_exclusions': set(['the', 'and', 'or', 'in', 'at', 'for']),
                'cleanup_words': ['Write a professional summary:', 'Generate a professional summary:', 'Here is a professional summary:']
            }
        }

    def format_input_data(self, input_json):
        """Validate and format input data."""
        required_fields = ['name', 'current_role', 'years_experience', 'companies', 'achievements', 'skills', 'education']
        for field in required_fields:
            if field not in input_json:
                raise ValueError(f"Missing required field: {field}")
        
        # Format the data
        formatted_data = {
            'name': input_json['name'],
            'current_role': input_json['current_role'],
            'years_experience': input_json['years_experience'],
            'companies': input_json['companies'][:2],  # Limit to top 2 companies
            'achievements': input_json['achievements'][:self.config['formatting']['max_achievements']],
            'skills': [s for s in input_json['skills'][:self.config['formatting']['max_skills']] 
                      if s.lower() not in self.config['formatting']['skill_exclusions']],
            'education': input_json['education'][:2],  # Limit to top 2 education entries
            'recognition': input_json.get('recognition', '')  # Optional recognition field
        }
        
        return formatted_data

    def format_template_data(self, formatted_data):
        """Format data for template strings."""
        template_data = formatted_data.copy()
        
        # Convert lists to comma-separated strings
        list_fields = ['companies', 'achievements', 'skills', 'education']
        for field in list_fields:
            if isinstance(template_data[field], list):
                template_data[field] = ', '.join(template_data[field])
        
        # Ensure years_experience is an integer
        if 'years_experience' in template_data:
            template_data['years_experience'] = int(template_data['years_experience'])
        
        return template_data

    def clean_output(self, text):
        """Clean up the generated text."""
        # Remove cleanup words
        for word in self.config['formatting']['cleanup_words']:
            text = text.replace(word, "")
        
        # Remove trailing punctuation
        text = re.sub(r'[.,;:!?]+$', '', text.strip())
        
        # Remove trailing "in" if present
        text = re.sub(r'\s+in\s*$', '', text)
        
        # Add period at the end if not present
        if not text.endswith('.'):
            text += '.'
        
        return text.strip()

    @abstractmethod
    def generate_prompt(self, formatted_data):
        """Generate prompt from formatted data."""
        pass

    @abstractmethod
    def generate_summary(self, input_json):
        """Generate summary from input JSON."""
        pass
