from transformers import BartTokenizer, BartForConditionalGeneration
import torch
from .base_model import BaseResumeModel
from config.model_config import BART_CONFIG
from config.model_prompts import BART_PROMPT, SUMMARY_TEMPLATES

class BartResumeModel(BaseResumeModel):
    def __init__(self, model_name="facebook/bart-base", cache_dir=None):
        super().__init__()
        self.config.update(BART_CONFIG)
        if model_name != "facebook/bart-base":
            self.config['model']['name'] = model_name
        
        # Initialize tokenizer and model with caching
        self.tokenizer = BartTokenizer.from_pretrained(
            self.config['model']['name'],
            cache_dir=cache_dir,
            local_files_only=cache_dir is not None,
            model_max_length=1024,
            force_download=False,
            legacy=False,
        )
        
        self.model = BartForConditionalGeneration.from_pretrained(
            self.config['model']['name'],
            cache_dir=cache_dir,
            local_files_only=cache_dir is not None,
            force_download=False
        )
    
    def generate_prompt(self, formatted_data):
        """Generate a prompt using the template strings."""
        template_data = self.format_template_data(formatted_data)
        templates = {k: v.format(**template_data) for k, v in SUMMARY_TEMPLATES.items()}
        return BART_PROMPT.format(**templates)
    
    def generate_summary(self, input_json):
        """Generate a professional summary using BART model."""
        try:
            # Format input data
            formatted_data = self.format_input_data(input_json)
            
            # Generate prompt
            input_text = self.generate_prompt(formatted_data)
            
            # Tokenize input
            inputs = self.tokenizer.encode(
                input_text, 
                return_tensors="pt", 
                max_length=1024,
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
            raise RuntimeError(f"Error in BART generation: {e}")
