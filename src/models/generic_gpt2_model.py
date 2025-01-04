from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
from typing import List, Dict, Any, Optional
import numpy as np
from .base_model import BaseModel
import re
import torch
import logging
import os
import time
import yaml
from clearml import Task
from utils.clearml_utils import (
    init_clearml_task, log_model_parameters, log_metric, log_text,
    save_model_checkpoint
)

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class GenericGPT2Model(BaseModel):
    """A GPT-Neo model that can generate video scripts from resume data."""
    
    def __init__(self, task: Optional[Task] = None):
        """Initialize the model."""
        super().__init__()
        self.task = task
        try:
            # Load config
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            # Get model configuration
            model_config = config['model']
            self.GENERATION_CONFIG = model_config['parameters']
            
            # Use base GPT2 for more stable generation
            logger.info("Loading model and tokenizer...")
            model_name = model_config['name']
            cache_dir = model_config['cache_dir']
            
            # Determine device (GPU/CPU)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Load tokenizer and model with caching
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_name, cache_dir=cache_dir)
            self.model = GPT2LMHeadModel.from_pretrained(model_name, cache_dir=cache_dir)
            
            # Move model to appropriate device
            self.model = self.model.to(device)
            
            # Initialize the generator pipeline with the configuration
            self.pipeline = pipeline(
                'text-generation',
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                **self.GENERATION_CONFIG
            )
            
            # Log model parameters if task exists
            if self.task:
                log_model_parameters({
                    "model_name": model_name,
                    "device": device,
                    **self.GENERATION_CONFIG
                })
            
            logger.info("Model initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            raise

    def _prepare_input_text(self, resume_data: Dict[str, Any]) -> str:
        """Prepare input text from resume data."""
        name = resume_data.get('name', '')
        current_role = resume_data.get('current_role', '')
        companies = resume_data.get('companies', [])
        years_experience = resume_data.get('years_experience', 0)
        skills = resume_data.get('skills', [])
        achievements = resume_data.get('achievements', [])
        education = resume_data.get('education', [])
        contact_info = resume_data.get('contact_info', {})
        
        # Create the base template
        base_script = f"""Create a professional video script for {name}, a {current_role} with {years_experience} years of experience.

1. Introduction
- Introduce {name} as a {current_role}
- Highlight {years_experience} years of experience
- Mention current/recent company: {', '.join(companies)}

2. Experience
- Detail professional journey
- Focus on role at {companies[0] if companies else 'current company'}
- Emphasize growth and responsibilities

3. Skills
- Technical skills: {', '.join(skills[:5] if len(skills) > 5 else skills)}
- Additional competencies: {', '.join(skills[5:] if len(skills) > 5 else [])}

4. Achievements
- Key accomplishments: {'; '.join(achievements)}

5. Goals
- Career aspirations
- Value proposition
- Future focus areas

6. Contact
For opportunities and connections:
- Email: {contact_info.get('email', '')}
- Phone: {contact_info.get('phone', '')}

Begin the script now:

"""
        return base_script
            
    def _create_section_prompt(self, section_num: int, title: str) -> str:
        """Create a prompt for a specific section."""
        return f"{section_num}. {title}\n- Caption: [Title for {title}]\n- Audio: [Script for {title}]\n- Visual: [Visuals for {title}]\n\n"
            
    def generate_summary(self, resume_data: Dict[str, Any]) -> str:
        """Generate a video script summary from resume data."""
        try:
            logger.info("Resume data received:")
            logger.info("-" * 40)
            logger.info(resume_data)
            logger.info("-" * 40)
            
            # Extract key information
            name = resume_data.get('name', '')
            current_role = resume_data.get('current_role', '')
            years = resume_data.get('years_experience', 0)
            companies = resume_data.get('companies', [])
            company = companies[0] if companies else ''
            skills = resume_data.get('skills', [])
            achievement = resume_data.get('achievements', [''])[0] if resume_data.get('achievements') else ''
            email = resume_data.get('contact_info', {}).get('email', '')
            phone = resume_data.get('contact_info', {}).get('phone', '')
            
            # Determine industry based on role and skills
            is_restaurant = any(keyword in current_role.lower() for keyword in ['restaurant', 'food', 'hospitality', 'chef'])
            is_it = any(keyword in ' '.join(skills).lower() for keyword in [
                'python', 'java', 'javascript', 'react', 'angular', 'node', 'aws', 'cloud',
                'devops', 'developer', 'software', 'engineering', 'programming', 'fullstack',
                'backend', 'frontend', 'web', 'mobile', 'app', 'development'
            ])
            
            industry = 'restaurant' if is_restaurant else 'it' if is_it else 'healthcare'
            
            # Create industry-specific templates
            templates = {
                'restaurant': {
                    'intro_audio': f"Meet {name}, an experienced {current_role} with {years} years in the restaurant industry.",
                    'experience_audio': f"At {company}, I have demonstrated expertise in restaurant operations, staff management, and customer service excellence.",
                    'skills_audio': f"My core competencies include {', '.join(skills[:3])}, enabling me to deliver exceptional dining experiences.",
                    'achievement_audio': achievement or "Led successful initiatives that improved efficiency and customer satisfaction.",
                    'goals_audio': "I am passionate about creating exceptional dining experiences and developing high-performing restaurant teams.",
                    'visuals': {
                        'intro': "Professional headshot transitioning to dynamic restaurant environment scenes",
                        'experience': "Animated timeline showcasing restaurant management achievements",
                        'skills': "Interactive display of restaurant management skills and expertise",
                        'achievement': "Data visualization of operational improvements and metrics",
                        'goals': "Forward-looking imagery of modern restaurant operations"
                    }
                },
                'healthcare': {
                    'intro_audio': f"Meet {name}, a seasoned {current_role} with {years} years of experience in healthcare.",
                    'experience_audio': f"At {company}, I have demonstrated expertise in HR operations, recruitment, and process improvement.",
                    'skills_audio': f"My core competencies include {', '.join(skills[:3])}, enabling me to drive organizational excellence.",
                    'achievement_audio': achievement or "Successfully implemented initiatives that improved efficiency and compliance.",
                    'goals_audio': "I am passionate about leveraging modern HR practices to transform healthcare talent acquisition.",
                    'visuals': {
                        'intro': "Professional headshot transitioning to modern healthcare workplace scenes",
                        'experience': "Animated timeline showcasing healthcare HR achievements",
                        'skills': "Interactive display of healthcare HR competencies",
                        'achievement': "Data visualization of recruitment and HR metrics",
                        'goals': "Forward-looking imagery of healthcare innovation"
                    }
                },
                'it': {
                    'intro_audio': f"Meet {name}, an innovative {current_role} with {years} years of experience in software development.",
                    'experience_audio': f"At {company}, I have demonstrated expertise in building scalable solutions, leading technical teams, and delivering high-impact projects.",
                    'skills_audio': f"My technical stack includes {', '.join(skills[:3])}, enabling me to architect and deliver robust solutions.",
                    'achievement_audio': achievement or "Successfully delivered multiple high-impact projects that improved system performance and user experience.",
                    'goals_audio': "I am passionate about leveraging cutting-edge technologies to solve complex problems and drive innovation.",
                    'visuals': {
                        'intro': "Professional headshot transitioning to modern tech workspace with code displays",
                        'experience': "Dynamic timeline showcasing technical projects and achievements",
                        'skills': "Interactive visualization of tech stack and programming languages",
                        'achievement': "Data visualization of project metrics and system improvements",
                        'goals': "Forward-looking imagery of emerging technologies and innovation"
                    }
                }
            }
            
            # Get industry-specific template
            template = templates[industry]
            
            # Create the base script template
            base_script = f"""1. Introduction
- Caption: {name} | {current_role}
- Audio: {template['intro_audio']}
- Visual: {template['visuals']['intro']}

2. Experience
- Caption: Professional Excellence
- Audio: {template['experience_audio']}
- Visual: {template['visuals']['experience']}

3. Skills
- Caption: Core Competencies
- Audio: {template['skills_audio']}
- Visual: {template['visuals']['skills']}

4. Achievement
- Caption: Key Impact
- Audio: {template['achievement_audio']}
- Visual: {template['visuals']['achievement']}

5. Goals
- Caption: Future Vision
- Audio: {template['goals_audio']}
- Visual: {template['visuals']['goals']}

6. Contact
- Caption: Let's Connect
- Audio: Contact me at {email}{f' or {phone}' if phone else ''}
- Visual: Professional contact display with modern industry-themed background"""

            # Create the generation prompt
            prompt = (
                f"Create a professional video script for a {industry} industry professional that effectively presents their qualifications and experience.\n\n"
                "RESUME INFORMATION:\n"
                f"Name: {name}\n"
                f"Current Role: {current_role}\n"
                f"Years of Experience: {years}\n"
                f"Company: {', '.join(companies)}\n"
                f"Skills: {', '.join(skills)}\n"
                f"Key Achievement: {achievement}\n"
                f"Contact: {email}{f', {phone}' if phone else ''}\n\n"
                "SCRIPT REQUIREMENTS:\n"
                "1. Create a 6-section script following this exact structure:\n"
                f"{base_script}\n\n"
                "GUIDELINES:\n"
                f"- Focus on {industry}-specific experience and achievements\n"
                "- Keep each section concise and impactful\n"
                "- Maintain professional tone throughout\n"
                "- Focus on measurable achievements\n"
                "- Make each section flow naturally\n\n"
                "Begin the script now:\n\n"
            )
            
            # Generate script
            logger.info("Generating script with prompt...")
            start_time = time.time()
            generated_script = self.pipeline(
                prompt,
                **self.GENERATION_CONFIG
            )[0]['generated_text']
            generation_time = time.time() - start_time
            
            # Extract the script portion
            script_start = generated_script.find("1. Introduction")
            if script_start == -1:
                logger.warning("Generated script missing sections, using base template")
                return base_script
                
            script = generated_script[script_start:]
            
            # Validate script sections
            required_sections = ["1. Introduction", "2. Experience", "3. Skills", 
                               "4. Achievement", "5. Goals", "6. Contact"]
            
            if not all(section in script for section in required_sections):
                logger.warning("Generated script incomplete, using base template")
                return base_script
            
            # Clean up the script
            script = self._post_process_script(script, name, email, phone)
            
            # Log metrics if task exists
            if self.task:
                log_metric("generation", "generation_time", generation_time)
                log_metric("generation", "output_length", len(script))
                log_text("generation", "sample_output", script[:500])
            
            return script
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            logger.warning("Using base template due to error")
            return base_script

    def _post_process_script(self, script: str, name: str, email: str, phone: str) -> str:
        """Post-process the generated script."""
        # Replace placeholder text with actual information
        script = script.replace("[Name]", name)
        script = script.replace("[Email]", email)
        script = script.replace("[Phone]", phone)
        
        # Remove any unnecessary characters
        script = script.strip()
        
        return script

    def _get_section_title(self, section_num: str) -> str:
        """Get the title for a section."""
        titles = {
            '1': 'Introduction',
            '2': 'Experience',
            '3': 'Skills',
            '4': 'Achievement',
            '5': 'Goals',
            '6': 'Contact'
        }
        return titles.get(section_num, 'Section')
        
    def _clean_components(self, components: Dict[str, str], section_num: str, name: str, email: str) -> Dict[str, str]:
        """Clean and validate section components."""
        try:
            section_num = int(section_num)
            cleaned = {}
            
            # Clean caption
            if 'caption' in components:
                caption = components['caption'].strip()
                if len(caption) < 5:  # Too short, use default
                    caption = self._get_default_caption(section_num, name)
                cleaned['caption'] = caption
                
            # Clean audio
            if 'audio' in components:
                audio = components['audio'].strip()
                if len(audio) < 10:  # Too short, use default
                    audio = self._get_default_audio(section_num, name, email)
                # Ensure first-person perspective
                if not any(pronoun in audio.lower() for pronoun in ['i ', "i'm", "my", "me", "we"]):
                    audio = f"I {audio}" if not audio.lower().startswith('i ') else audio
                cleaned['audio'] = audio
                
            # Clean visual
            if 'visual' in components:
                visual = components['visual'].strip()
                if len(visual) < 5:  # Too short, use default
                    visual = self._get_default_visual(section_num)
                cleaned['visual'] = visual
                
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning components: {str(e)}")
            return components
            
    def _get_default_caption(self, section_num: int, name: str) -> str:
        """Get default caption for a section."""
        captions = {
            1: f"{name} | Professional Overview",
            2: "Proven Track Record",
            3: "Expert Skill Set",
            4: "Key Achievement Spotlight",
            5: "Vision & Aspirations",
            6: "Let's Connect"
        }
        return captions.get(section_num, "Professional Profile")
        
    def _get_default_audio(self, section_num: int, name: str, email: str) -> str:
        """Get default audio for a section."""
        audio = {
            1: f"Hello, I'm {name}. I bring expertise and innovation to every project I undertake.",
            2: "My career journey has been marked by continuous growth and impactful contributions.",
            3: "I've developed a diverse skill set that enables me to tackle complex challenges effectively.",
            4: "One of my proudest achievements demonstrates my ability to drive results.",
            5: "Looking ahead, I'm excited to take on new challenges and contribute to innovative projects.",
            6: f"I'm always open to discussing new opportunities. Feel free to reach out at {email}."
        }
        return audio.get(section_num, "")
        
    def _get_default_visual(self, section_num: int) -> str:
        """Get default visual for a section."""
        visuals = {
            1: "Professional headshot with modern office background",
            2: "Animated timeline showcasing career progression",
            3: "Interactive 3D visualization of interconnected skills",
            4: "Dynamic infographic highlighting key achievements",
            5: "Inspiring imagery of innovation and growth",
            6: "Clean, modern contact information display with social media icons"
        }
        return visuals.get(section_num, "Professional imagery")
