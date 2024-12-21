import json
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
from datetime import datetime
import re

# Configuration
CONFIG = {
    'model': {
        'name': 't5-base',  # Model name for loading
        'generation_params': {  # Parameters for model.generate()
            'max_length': 150,
            'min_length': 50,
            'num_beams': 4,
            'length_penalty': 1.0,
            'no_repeat_ngram_size': 2,
            'early_stopping': True
        }
    },
    'formatting': {
        'max_achievements': 2,
        'max_skills': 3,
        'max_responsibilities': 2,
        'skill_exclusions': ['fun', 'energetic'],
        'cleanup_words': [
            "Generate", "Write", "Create", "Summary:", "Profile:", "Experience:",
            "Achievement 1:", "Achievement 2:", "Education:", "Skills:",
            "first person", "starting with", "name", "write", "create",
            "summary", "profile", "resume", "background", "expertise",
            '"', "'", "says", "she says", "he says", "they say"
        ],
        'word_replacements': {
            "successfully ": "",
            "through ": "via ",
            "minimum of ": "least ",
            "and by creating": "through",
            " i ": " I ",
            "i am": "I am",
            "i have": "I have",
            "my ": "My ",
            "b.s.": "B.S.",
            "a.a.": "A.A.",
            "..": ".",
            "  ": " ",
            " .": ".",
            " ,": ",",
            "foh": "FOH",
            "pos": "POS"
        }
    }
}

def calculate_experience(positions):
    """Calculate total years of experience based on position durations."""
    total_months = 0
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    months_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    for position in positions:
        duration = position['duration']
        # Split duration into start and end dates
        dates = duration.split('–')
        if len(dates) != 2:
            continue
            
        start_date, end_date = dates[0].strip(), dates[1].strip()
        
        # Extract years using a more robust pattern
        year_pattern = r'(?:19|20)\d{2}'
        start_match = re.search(year_pattern, start_date)
        if not start_match:
            continue  # Skip this position if no valid year found
        start_year = int(start_match.group())
        
        # Handle end date - use current year/month if "Present"
        if 'Present' in end_date:
            end_year = current_year
            end_month = current_month
        else:
            end_match = re.search(year_pattern, end_date)
            if not end_match:
                continue  # Skip this position if no valid year found
            end_year = int(end_match.group())
            # Default to December for past positions unless month is specified
            end_month = 12
            for month in months_map:
                if month in end_date:
                    end_month = months_map[month]
                    break
        
        if start_year and end_year:
            # Get start month
            start_month = 1  # Default to January
            for month in months_map:
                if month in start_date:
                    start_month = months_map[month]
                    break
            
            # Calculate months of experience
            months = (end_year - start_year) * 12 + (end_month - start_month)
            if months > 0:  # Only add positive durations
                total_months += months
    
    # Convert total months to years and months
    years = total_months // 12
    remaining_months = total_months % 12
    
    # Format the experience string
    if years > 0:
        if remaining_months >= 6:  # Round up if 6 or more months
            return f"{years + 1}+ years"
        elif remaining_months > 0:
            return f"{years}+ years"  # Add '+' to indicate additional months
        else:
            return f"{years} years"
    else:
        return f"{remaining_months} months"

def format_input_text(input_json):
    """Format the resume data into a structured text for the model."""
    
    # Extract achievements and responsibilities
    achievements = []
    responsibilities = []
    companies = []
    
    for position in input_json['positions']:
        companies.append(f"{position['role']} at {position['company']}")
        for achievement in position['key_achievements']:
            if any(char.isdigit() for char in achievement):
                achievements.append(achievement)
            else:
                responsibilities.append(achievement)
    
    # Get professional skills
    professional_skills = [skill for skill in input_json['skills'] 
                         if not any(word in skill.lower() for word in CONFIG['formatting']['skill_exclusions'])]
    
    # Calculate total experience
    experience = calculate_experience(input_json['positions'])
    
    # Get name and current role
    name = input_json['personal_information']['name']
    current_role = input_json['positions'][0]['role']
    
    # Format achievements and responsibilities
    formatted_achievements = []
    for metric in achievements[:CONFIG['formatting']['max_achievements']]:
        achievement = metric.lower()
        for old, new in CONFIG['formatting']['word_replacements'].items():
            achievement = achievement.replace(old.lower(), new)
        formatted_achievements.append(achievement)
    
    formatted_responsibilities = []
    for resp in responsibilities[:CONFIG['formatting']['max_responsibilities']]:
        resp_text = resp.lower()
        for old, new in CONFIG['formatting']['word_replacements'].items():
            resp_text = resp_text.replace(old.lower(), new)
        formatted_responsibilities.append(resp_text)
    
    # Format education more concisely
    education = [degree.split('|')[0].strip() for degree in input_json['education']]
    
    # Format text for better T5 understanding - simpler prompt
    text = f"""Write a professional summary for {name}, a {current_role} with {experience} experience. Include these details:

Work History: {', '.join(companies)}

Key Achievements:
{chr(10).join('- ' + achievement for achievement in formatted_achievements)}

Core Responsibilities:
{chr(10).join('- ' + resp for resp in formatted_responsibilities)}

Education: {education[0]}, {education[1]}
Skills: {', '.join(professional_skills[:CONFIG['formatting']['max_skills']])}

Write in first person, starting with name and experience. Mention achievements, responsibilities, and skills."""

    return text

def generate_summary(input_json):
    """Generate a professional summary using T5 model."""
    
    # Initialize model and tokenizer
    model_name = CONFIG['model']['name']
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    if isinstance(model, tuple):
        model = model[0]  # Get the model from the tuple if it's returned as one
    assert isinstance(model, T5ForConditionalGeneration)
    
    # Format input text
    input_text = format_input_text(input_json)
    
    # Tokenize input
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    
    # Generate summary
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            **CONFIG['model']['generation_params']
        )
    
    # Decode and clean up the generated text
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Get name and role for proper case preservation
    name = input_json['personal_information']['name']
    current_role = input_json['positions'][0]['role']
    
    # Clean up the text using configured cleanup words
    for word in CONFIG['formatting']['cleanup_words']:
        summary = summary.replace(word, "")
    
    # Apply configured word replacements
    for old, new in CONFIG['formatting']['word_replacements'].items():
        summary = summary.replace(old, new)
    
    # Ensure proper name and role capitalization
    summary = summary.replace(name.lower(), name)
    summary = summary.replace(name.upper(), name)
    summary = summary.replace(current_role.lower(), current_role)
    
    # Clean up any double spaces and trim
    summary = " ".join(summary.split())
    summary = summary.strip()
    
    # Ensure proper first-person perspective and experience mention
    if not summary.lower().startswith("my name"):
        summary = f"My name is {name}. I am a {current_role} with {calculate_experience(input_json['positions'])} experience at {input_json['positions'][0]['company']}. " + summary
    
    return summary

if __name__ == "__main__":
    # Read input data
    input_json = {
        "personal_information": {
            "name": "May Riley",
            "contact": {
                "address": "4567 Main Street, Buffalo, New York 98052",
                "phone": "(716) 555-0100",
                "email": "m.riley@live.com",
                "linkedin": "www.linkedin.com/in/m.riley"
            }
        },
        "positions": [
            {
                "role": "Restaurant Manager",
                "company": "Contoso Bar and Grill",
                "duration": "September 2022 – Present",
                "key_achievements": [
                    "Reduced costs by 7% through controls on overtime, operational efficiencies, and reduced waste.",
                    "Consistently exceed monthly sales goals by a minimum of 10% by training FOH staff on upselling techniques and by creating a featured food and beverage program."
                ]
            },
            {
                "role": "Restaurant Manager",
                "company": "Fourth Coffee Bistro",
                "duration": "June 2000 – August 2022",
                "key_achievements": [
                    "Created a cross-training program ensuring FOH staff members were able to perform confidently and effectively in all positions.",
                    "Grew customer base and increased restaurant social media accounts by 19% through interactive promotions, engaging postings, and contests.",
                    "Created and implemented staff health and safety standards compliance training program, achieving a score of 99% from the Board of Health.",
                    "Successfully redesigned existing inventory system, ordering and food storage practices, resulting in a 6% decrease in food waste and higher net profits."
                ]
            }
        ],
        "education": [
            "B.S. in Business Administration | June 2020 | Bigtown College, Chicago, Illinois",
            "A.A. in Hospitality Management | June 2018 | Bigtown College, Chicago, Illinois"
        ],
        "skills": [
            "Accounting & Budgeting",
            "Proficient with POS systems",
            "Excellent interpersonal and communication skills",
            "Poised under pressure",
            "Experienced in most restaurant positions",
            "Fun and energetic"
        ],
        "interests": [
            "Theater",
            "environmental conservation",
            "art",
            "hiking",
            "skiing",
            "travel"
        ]
    }
    
    # Generate and print summary
    print("Generating professional summary (this may take a moment)...")
    summary = generate_summary(input_json)
    print("\nGenerated Professional Summary:")
    print(summary)
    
    # Save the summary to a file
    with open('professional_summary.txt', 'w') as f:
        f.write(summary)
