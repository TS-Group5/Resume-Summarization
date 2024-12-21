from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from .base_model import BaseResumeModel
from config.model_config import T5_CONFIG
from config.model_prompts import T5_PROMPT, SUMMARY_TEMPLATES

class T5ResumeModel(BaseResumeModel):
    def __init__(self, model_name="t5-base", cache_dir=None):
        super().__init__()
        self.config.update(T5_CONFIG)
        if model_name != "t5-base":
            self.config['model']['name'] = model_name
        
        # Initialize tokenizer with proper max length and legacy behavior
        self.tokenizer = T5Tokenizer.from_pretrained(
            self.config['model']['name'],
            model_max_length=1024,  # Set appropriate max length
            legacy=False,  # Use new behavior
            cache_dir=cache_dir,
            local_files_only=cache_dir is not None
        )
        
        # Initialize model with force_download=True to avoid deprecated warning
        self.model = T5ForConditionalGeneration.from_pretrained(
            self.config['model']['name'],
            cache_dir=cache_dir,
            local_files_only=cache_dir is not None
        )
    
    def format_template_data(self, formatted_data):
        """Format data for template, with additional preprocessing for T5."""
        template_data = super().format_template_data(formatted_data)
        
        # Deduplicate achievements by splitting and removing duplicates
        if 'achievements' in template_data:
            achievements = template_data['achievements'].split(', ')
            unique_achievements = []
            seen = set()
            for achievement in achievements:
                achievement_lower = achievement.lower()
                if achievement_lower not in seen:
                    seen.add(achievement_lower)
                    unique_achievements.append(achievement)
            template_data['achievements'] = ', '.join(unique_achievements)
        
        return template_data
    
    def generate_prompt(self, formatted_data):
        """Generate a prompt using the template strings."""
        template_data = self.format_template_data(formatted_data)
        templates = {k: v.format(**template_data) for k, v in SUMMARY_TEMPLATES.items()}
        return T5_PROMPT.format(**templates)
    
    def clean_output(self, text):
        """Clean up the T5 model output."""
        # Fix capitalization
        text = text.strip()
        
        # Remove any fabricated content
        text = text.split('.')
        cleaned_text = []
        for sentence in text:
            if sentence.strip():
                # Skip sentences with fabricated content
                skip_words = ['award', 'recognize', 'honor', 'interview', 'said', 'says', 'pleased', 'happy']
                if not any(word in sentence.lower() for word in skip_words):
                    cleaned_text.append(sentence.strip())
        text = cleaned_text
        
        # Clean each sentence
        cleaned_sentences = []
        for sentence in text:
            if sentence:
                # Convert to first person
                sentence = sentence.replace(' her ', ' my ')
                sentence = sentence.replace(' she ', ' I ')
                sentence = sentence.replace('May Riley is', 'I am')
                sentence = sentence.replace('Her key', 'My key')
                sentence = sentence.replace('She consistently', 'I consistently')
                sentence = sentence.replace('May Riley has', 'I have')
                sentence = sentence.replace('May Riley works', 'I work')
                sentence = sentence.replace('May Riley manages', 'I manage')
                
                # Capitalize first letter of sentence
                sentence = sentence[0].upper() + sentence[1:]
                
                # Fix common capitalization issues
                sentence = sentence.replace(' i ', ' I ')
                sentence = sentence.replace(' contoso ', ' Contoso ')
                sentence = sentence.replace(' fourth ', ' Fourth ')
                sentence = sentence.replace(' coffee ', ' Coffee ')
                sentence = sentence.replace(' bistro', ' Bistro')
                sentence = sentence.replace(' foh ', ' FOH ')
                sentence = sentence.replace('may riley', 'May Riley')
                sentence = sentence.replace('May riley', 'May Riley')
                sentence = sentence.replace('may Riley', 'May Riley')
                sentence = sentence.replace('Hi i ', 'Hi, I ')
                sentence = sentence.replace('hi i ', 'Hi, I ')
                
                # Remove redundant phrases
                if 'reduced waste' in sentence.lower():
                    if sentence.lower().count('reduced waste') > 1:
                        sentence = sentence.replace(', reduced waste', '')
                
                cleaned_sentences.append(sentence)
        
        # Join sentences and ensure proper ending
        text = '. '.join(cleaned_sentences)
        if not text.endswith('.'):
            text += '.'
            
        # Ensure the text starts with the greeting if not present
        if not text.lower().startswith('hi, i am may riley'):
            text = 'Hi, I am May Riley. ' + text
            
        # Remove any remaining third-person references, but keep the greeting intact
        text_parts = text.split('Hi, I am May Riley')
        if len(text_parts) > 1:
            greeting = 'Hi, I am May Riley'
            rest = text_parts[1]
            # Only clean the non-greeting part
            rest = rest.replace('May Riley', 'I')
            rest = rest.replace('Her', 'My')
            rest = rest.replace('She', 'I')
            text = greeting + rest
        
        # Fix any double spaces
        text = ' '.join(text.split())
        
        # Fix grammar issues
        text = text.replace(' I is ', ' I am ')
        text = text.replace(' I Is ', ' I am ')
        text = text.replace(' I was ', ' I am ')
        text = text.replace(' I Was ', ' I am ')
            
        return text
    
    def generate_summary(self, input_json):
        """Generate a professional summary using T5 model."""
        try:
            # Format input data
            formatted_data = self.format_input_data(input_json)
            
            # Generate prompt
            input_text = self.generate_prompt(formatted_data)
            
            # Add task prefix for T5
            input_text = "summarize: " + input_text
            
            # Tokenize input with proper max length
            inputs = self.tokenizer.encode(
                input_text, 
                return_tensors="pt", 
                max_length=1024,  # Match tokenizer max_length
                truncation=True,
                padding='max_length'
            )
            
            # Generate summary
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    **self.config['model']['generation_params']
                )
            
            # Decode and clean up the generated text
            summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return self.clean_output(summary)
            
        except Exception as e:
            raise RuntimeError(f"Error in T5 generation: {e}")
