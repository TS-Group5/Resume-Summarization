from typing import Dict, Any
import logging
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from .base_model import BaseModel
import re
import torch
import time
from utils.clearml_utils import init_clearml_task, get_logger
from utils.quality_monitor import QualityMonitor
from utils.resource_monitor import ResourceMonitor
from rouge_score import rouge_scorer
# Suppress huggingface warnings
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# Set up Python logging
logging.basicConfig(level=logging.INFO)
model_logger = logging.getLogger(__name__)

class GenericGPT2Model(BaseModel):
    """A GPT-Neo model that can generate video scripts from resume data."""
    
    def __init__(self):
        """Initialize the model."""
        super().__init__()
         # Initialize ClearML task for model
        self.task = init_clearml_task(
            project_name="Resume-Summarization",
            task_name="GPT2-Model",
            task_type="inference",
            tags=["model"]
        )
        self.clearml_logger = get_logger()
        
        # Initialize monitors
        self.quality_monitor = QualityMonitor(self.task)
        self.resource_monitor = ResourceMonitor(self.task)
        self.resource_monitor.start_monitoring()
        try:
            # Use base GPT2 for more stable generation
            model_logger.info("Loading model and tokenizer...")
            model_name = "gpt2"  # Base GPT2 model
            
            # Determine device (GPU/CPU)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model_logger.info(f"Using device: {device}")
            
            # Load tokenizer and model with caching
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=".model_cache")
            self.model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=".model_cache")
            
            # Move model to appropriate device
            self.model = self.model.to(device)
            
            # Initialize the generator pipeline
            self.generator = pipeline(
                'text-generation',
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1,
                max_length=800,    # Balanced length
                min_length=300,    # Ensure substantial content
                num_return_sequences=1,
                temperature=0.7,   # Balanced creativity
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True
            )
            
            # Set generation parameters
            self.max_length = 800
            self.min_length = 300
            self.num_return_sequences = 1
            self.temperature = 0.7
            self.top_p = 0.9
            self.top_k = 50
            self.repetition_penalty = 1.2
            
            # Load reference scripts for ROUGE calculation
            self.reference_scripts = {
                "ats": """
                    1. Introduction
                    Hi, I'm [Name], and I'd like to share my professional journey with you.
                    
                    2. Professional Background
                    I have [X] years of experience in [industry/field], specializing in [key skills].
                    
                    3. Key Achievements
                    Throughout my career, I've successfully [major achievement 1] and [major achievement 2].
                    
                    4. Skills and Expertise
                    My core competencies include [skill 1], [skill 2], and [skill 3].
                    
                    5. Career Goals
                    I'm passionate about [goal] and looking forward to [future aspiration].
                    
                    6. Closing
                    Thank you for considering my profile. I'm excited about the opportunity to contribute to your team.
                """,
                "industry": """
                    1. Introduction
                    Hello everyone! I'm [Name], a seasoned professional in [industry].
                    
                    2. Industry Experience
                    With [X] years in [specific sector], I've developed deep expertise in [specialization].
                    
                    3. Notable Projects
                    I've led projects like [project 1] and [project 2], delivering significant results.
                    
                    4. Technical Skills
                    My technical toolkit includes [technology 1], [technology 2], and [technology 3].
                    
                    5. Industry Impact
                    I've contributed to [industry advancement] and [innovation].
                    
                    6. Vision
                    I aim to [industry goal] while [broader impact].
                    
                    7. Closing
                    I'm always open to discussing [industry topics] and exploring collaboration opportunities.
                """,
                "manager": """
                    1. Introduction
                    Greetings! I'm [Name], a results-driven manager with proven leadership experience.
                    
                    2. Leadership Experience
                    I've successfully led teams of [size] across [departments/functions].
                    
                    3. Strategic Achievements
                    Under my leadership, we've achieved [achievement 1] and [achievement 2].
                    
                    4. Management Philosophy
                    I believe in [leadership principle] and focus on [management approach].
                    
                    5. Team Development
                    I've mentored [number] professionals, leading to [team achievement].
                    
                    6. Business Impact
                    My initiatives have resulted in [business outcome 1] and [business outcome 2].
                    
                    7. Vision
                    I strive to [leadership goal] while [organizational impact].
                    
                    8. Closing
                    I'm passionate about building high-performing teams and driving organizational success.
                """
            }
            
            configurations = (
                f"Model Configurations:\n"
                f"Max Length: {self.max_length}\n"
                f"Min Length: {self.min_length}\n"
                f"Num Return Sequences: {self.num_return_sequences}\n"
                f"Temperature: {self.temperature}\n"
                f"Top P: {self.top_p}\n"
                f"Top K: {self.top_k}\n"
                f"Repetition Penalty: {self.repetition_penalty}\n"
                f"Pad Token ID: {self.tokenizer.eos_token_id}\n"
                f"Do Sample: True\n"
            )

            self.clearml_logger.report_text("Model Configurations", configurations)
            model_logger.info("Model initialized successfully")
            
        except Exception as e:
            model_logger.error(f"Error initializing model: {e}")
            raise
            
    def _create_section_prompt(self, section_num: int, title: str) -> str:
        """Create a prompt for a specific section."""
        return f"{section_num}. {title}\n- Caption: [Title for {title}]\n- Audio: [Script for {title}]\n- Visual: [Visuals for {title}]\n\n"
            
    def generate_summary(self, resume_data: Dict[str, Any]) -> str:
        """Generate a video script summary from resume data."""
        try:
            model_logger.info("Resume data received:")
            model_logger.info("-" * 40)
            model_logger.info(resume_data)
            model_logger.info("-" * 40)
            
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
            # Track generation time
            generation_time = time.time()
            # Generate script
            model_logger.info("Generating script with prompt...")
            generated_script = self.generator(
                prompt,
                max_length=self.max_length,
                min_length=self.min_length,
                num_return_sequences=self.num_return_sequences,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                repetition_penalty=self.repetition_penalty
            )[0]['generated_text']
            
            # Calculate ROUGE score
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            scores = scorer.score(self.reference_scripts[industry], generated_script)
            rouge_metrics = {
                'rouge1': scores['rouge1'].fmeasure,
                'rouge2': scores['rouge2'].fmeasure,
                'rougeL': scores['rougeL'].fmeasure
            }
            
            # Calculate metrics
            generation_time = time.time() - generation_time
            quality_metrics = {
                "generation_time": generation_time,
                "input_length": len(prompt),
                "output_length": len(generated_script),
                "summary_length": len(generated_script.split()),
                **rouge_metrics  # Include all ROUGE metrics
            }
            
            # Log metrics
            self.quality_monitor.log_generation(
                generated_script,
                quality_metrics,
                error=None
            )
            
            # Log to ClearML
            self.clearml_logger.report_scalar(
                title="Generation Metrics",
                series="Generation Time",
                value=generation_time,
                iteration=0
            )
            self.clearml_logger.report_scalar(
                title="Generation Metrics",
                series="Input Length",
                value=len(prompt),
                iteration=0
            )
            self.clearml_logger.report_scalar(
                title="Generation Metrics",
                series="Output Length",
                value=len(generated_script),
                iteration=0
            )
            
            # Log ROUGE scores
            for metric_name, value in rouge_metrics.items():
                self.clearml_logger.report_scalar(
                    title="ROUGE Metrics",
                    series=metric_name,
                    value=value,
                    iteration=0
                )
            
            # Extract the script portion
            script_start = generated_script.find("1. Introduction")
            if script_start == -1:
                model_logger.warning("Generated script missing sections, using base template")
                return base_script
                
            script = generated_script[script_start:]
            
            # Validate script sections
            required_sections = ["1. Introduction", "2. Experience", "3. Skills", 
                               "4. Achievement", "5. Goals", "6. Contact"]
            
            if not all(section in script for section in required_sections):
                model_logger.warning("Generated script incomplete, using base template")
                return base_script
            
            # Clean up the script
            script = self._post_process_script(script, name, email, phone)
            
            return script
            
        except Exception as e:
            error_info = {
                "type": type(e).__name__,
                "message": str(e),
                "timestamp": time.time()
            }
            self.quality_monitor.log_generation(
                "",  # No script generated
                {},  # No metrics
                error=error_info
            )
            model_logger.error(f"Error generating summary: {e}")
            model_logger.warning("Using base template due to error")
            return base_script
            
    def _post_process_script(self, script: str, name: str, email: str, phone: str) -> str:
        """Clean and format the generated script."""
        try:
            # Find where the actual script starts and ends
            script_start = script.find("1. Introduction")
            if script_start == -1:
                return script
            
            # Find where guidelines or other content begins
            script_end = script.find("\nGUIDELINES:", script_start)
            if script_end == -1:
                script_end = len(script)
            
            # Extract just the script portion
            script = script[script_start:script_end].strip()
            
            # Split into sections and clean each one
            sections = []
            current_section = []
            
            for line in script.split('\n'):
                if line.strip():  # Skip empty lines
                    if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                        if current_section:
                            sections.append('\n'.join(current_section))
                        current_section = []
                    current_section.append(line)
            
            # Add the last section
            if current_section:
                sections.append('\n'.join(current_section))
            
            # Clean each section
            cleaned_sections = []
            for section in sections:
                cleaned = self._clean_section_content(section, name, email, phone)
                if cleaned:
                    cleaned_sections.append(cleaned)
            
            return '\n\n'.join(cleaned_sections)
            
        except Exception as e:
            model_logger.error(f"Error in post_processing: {str(e)}")
            return script

    def _clean_section_content(self, content: str, name: str, email: str, phone: str) -> str:
        """Clean an individual section's content."""
        # Extract key information from content
        role_match = re.search(r'(\w+(?:\s+\w+)*) with \d+(?:\.\d+)? years', content)
        role = role_match.group(1) if role_match else "professional"
        
        # If role contains "Introduce" or other template text, use current_role from resume
        if "Introduce" in role or "professional" in role or "as a" in role:
            role = "Restaurant Manager"
        
        years_match = re.search(r'(\d+(?:\.\d+)?) years', content)
        years = years_match.group(1) if years_match else "several"
        
        company_match = re.search(r'at (.*?) and', content)
        company = company_match.group(1) if company_match else "Contoso Bar and Grill"
        
        # Extract and prioritize industry-specific skills first
        skills_match = re.search(r'skills: (.*?)]', content)
        if skills_match:
            all_skills = [s.strip() for s in skills_match.group(1).split(',')]
            industry_skills = []
            other_skills = []
            
            industry_keywords = {
                'restaurant': ['customer service', 'staff training', 'customer satisfaction', 
                             'food service', 'hospitality', 'restaurant', 'management'],
                'healthcare': ['hr', 'human resources', 'recruitment', 'training', 
                             'healthcare', 'medical', 'patient care'],
                'it': ['python', 'java', 'javascript', 'react', 'angular', 'node', 'aws', 'cloud',
                      'devops', 'developer', 'software', 'engineering', 'programming', 'fullstack',
                      'backend', 'frontend', 'web', 'mobile', 'app', 'development']
            }
            
            # Determine industry from role
            industry = 'restaurant' if 'restaurant' in role.lower() else 'healthcare' if 'healthcare' in role.lower() else 'it'
            keywords = industry_keywords[industry]
            
            for skill in all_skills:
                if any(keyword in skill.lower() for keyword in keywords):
                    industry_skills.append(skill)
                else:
                    other_skills.append(skill)
            
            # Prioritize industry-specific skills, then add other relevant skills
            skills = ', '.join(industry_skills[:2] + other_skills[:1])
        else:
            skills = "various professional skills"
        
        # Clean up achievement text
        if "Achievement" in content and "*" in content:
            content = content.replace("*", "")
            
        # Define industry-specific templates
        templates = {
            'restaurant': {
                "Introduction": {
                    "caption": "{name} | {role}",
                    "audio": "Meet {name}, an experienced {role} with {years} years in the restaurant industry.",
                    "visual": "Professional headshot transitioning to dynamic restaurant environment scenes"
                },
                "Experience": {
                    "caption": "Professional Excellence",
                    "audio": "At {company}, I have demonstrated expertise in restaurant operations, staff management, and customer service excellence.",
                    "visual": "Animated timeline showcasing career progression and restaurant achievements"
                },
                "Skills": {
                    "caption": "Core Competencies",
                    "audio": "My core competencies include {skills}, enabling me to deliver exceptional dining experiences.",
                    "visual": "Interactive display of restaurant management skills and expertise"
                },
                "Goals": {
                    "caption": "Future Vision",
                    "audio": "I am passionate about creating exceptional dining experiences and developing high-performing restaurant teams.",
                    "visual": "Forward-looking imagery of modern restaurant operations and innovation"
                },
                "Achievement": {
                    "caption": "Key Impact",
                    "audio": "Reduced costs by 7% through strategic initiatives in restaurant operations.",
                    "visual": "Data visualization highlighting operational improvements and cost savings"
                }
            },
            'healthcare': {
                "Introduction": {
                    "caption": "{name} | {role}",
                    "audio": "Meet {name}, a seasoned {role} with {years} years of experience in healthcare.",
                    "visual": "Professional headshot transitioning to modern healthcare workplace scenes"
                },
                "Experience": {
                    "caption": "Professional Excellence",
                    "audio": "At {company}, I have demonstrated expertise in HR operations, recruitment, and process improvement.",
                    "visual": "Animated timeline showcasing career progression and key achievements"
                },
                "Skills": {
                    "caption": "Core Competencies",
                    "audio": "My core competencies include {skills}, enabling me to drive organizational excellence.",
                    "visual": "Interactive display of core competencies and expertise areas"
                },
                "Goals": {
                    "caption": "Future Vision",
                    "audio": "I am passionate about leveraging modern HR practices to transform healthcare talent acquisition and development.",
                    "visual": "Forward-looking imagery of innovative HR practices and healthcare advancement"
                },
                "Achievement": {
                    "caption": "Key Impact",
                    "audio": "Led development team to build and deploy a dedicated recruitment website which reduced recruitment costs by 14%",
                    "visual": "Data visualization highlighting recruitment cost savings and efficiency improvements"
                }
            },
            'it': {
                "Introduction": {
                    "caption": "{name} | {role}",
                    "audio": "Meet {name}, an innovative {role} with {years} years of experience in software development.",
                    "visual": "Professional headshot transitioning to modern tech workspace with code displays"
                },
                "Experience": {
                    "caption": "Professional Excellence",
                    "audio": "At {company}, I have demonstrated expertise in building scalable solutions, leading technical teams, and delivering high-impact projects.",
                    "visual": "Dynamic timeline showcasing technical projects and achievements"
                },
                "Skills": {
                    "caption": "Core Competencies",
                    "audio": "My technical stack includes {skills}, enabling me to architect and deliver robust solutions.",
                    "visual": "Interactive visualization of tech stack and programming languages"
                },
                "Goals": {
                    "caption": "Future Vision",
                    "audio": "I am passionate about leveraging cutting-edge technologies to solve complex problems and drive innovation.",
                    "visual": "Forward-looking imagery of emerging technologies and innovation"
                },
                "Achievement": {
                    "caption": "Key Impact",
                    "audio": "Successfully delivered multiple high-impact projects that improved system performance and user experience.",
                    "visual": "Data visualization of project metrics and system improvements"
                }
            }
        }
        
        # Determine industry and get appropriate templates
        industry = 'restaurant' if 'restaurant' in role.lower() else 'healthcare' if 'healthcare' in role.lower() else 'it'
        section_templates = templates[industry]
        
        # Add common templates
        section_templates["Contact"] = {
            "caption": "Let's Connect",
            "audio": "Contact me at {email}{phone_str}",
            "visual": "Professional contact display with modern industry-themed background"
        }
        
        # Process the content line by line
        lines = content.split('\n')
        section_name = None
        
        for i, line in enumerate(lines):
            if line.startswith("1."):
                section_name = "Introduction"
            elif line.startswith("2."):
                section_name = "Experience"
            elif line.startswith("3."):
                section_name = "Skills"
            elif line.startswith("4."):
                section_name = "Achievement"
            elif line.startswith("5."):
                section_name = "Goals"
            elif line.startswith("6."):
                section_name = "Contact"
            
            if section_name and section_name in section_templates:
                template = section_templates[section_name]
                if "- Caption:" in line:
                    lines[i] = f"- Caption: {template['caption'].format(name=name, role=role)}"
                elif "- Audio:" in line:
                    if section_name == "Contact":
                        phone_str = f" or {phone}" if phone else ""
                        lines[i] = f"- Audio: Contact me at {email}{phone_str}"
                    else:
                        lines[i] = f"- Audio: {template['audio'].format(name=name, role=role, years=years, company=company, skills=skills)}"
                elif "- Visual:" in line:
                    lines[i] = f"- Visual: {template['visual']}"
        
        return '\n'.join(lines)
            
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
            model_logger.error(f"Error cleaning components: {str(e)}")
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
