import json
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
from src.parsers.ats_parser import ATSParser
from src.parsers.industry_manager_parser import IndustryManagerParser

def format_input_text(input_json):
    """Format the resume data into a structured text for the model."""
    
    # Extract key metrics and achievements
    metrics = []
    for position in input_json['positions']:
        for achievement in position['key_achievements']:
            if any(char.isdigit() for char in achievement):
                metrics.append(achievement)
    
    # Get professional skills
    professional_skills = [skill for skill in input_json['skills'] 
                         if not any(word in skill.lower() for word in ['fun', 'energetic'])]
    
    # Calculate total experience
    total_experience = len(input_json['positions'])
    
    # Format text for better T5 understanding
    text = f"""summarize this professional profile:
Experienced Restaurant Manager with {total_experience}+ years of expertise in restaurant operations and team leadership.

Current Position: {input_json['positions'][0]['role']} at {input_json['positions'][0]['company']}

Key Achievements:
{'; '.join(metrics[:4])}

Education:
- {input_json['education'][0].split('|')[0].strip()}
- {input_json['education'][1].split('|')[0].strip()}

Core Skills:
{', '.join(professional_skills[:4])}

Write a professional first-person summary highlighting experience, achievements, and skills."""
    
    return text

def generate_summary(input_json):
    """Generate a professional summary using T5 model."""
    
    # Initialize model and tokenizer
    model_name = "t5-base"
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
            max_length=200,
            min_length=100,
            num_beams=5,
            length_penalty=1.5,
            no_repeat_ngram_size=2,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            early_stopping=True
        )
    
    # Decode and clean up the generated text
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Post-process to ensure first-person perspective and professional tone
    replacements = {
        "The professional": "I am a",
        "This professional": "I am a",
        "They have": "I have",
        "Their": "My",
        "They are": "I am",
        "The candidate": "I",
        "This candidate": "I",
        "The manager": "I",
        "This manager": "I"
    }
    
    for old, new in replacements.items():
        summary = summary.replace(old, new)
    
    # Ensure it starts with a professional opener if needed
    if not any(summary.startswith(starter) for starter in ["I am", "I have", "Experienced", "Seasoned", "Results-driven"]):
        summary = "I am an experienced " + summary
    
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
                "duration": "September 20XX – Present",
                "key_achievements": [
                    "Reduced costs by 7% through controls on overtime, operational efficiencies, and reduced waste.",
                    "Consistently exceed monthly sales goals by a minimum of 10% by training FOH staff on upselling techniques and by creating a featured food and beverage program."
                ]
            },
            {
                "role": "Restaurant Manager",
                "company": "Fourth Coffee Bistro",
                "duration": "June 20XX – August 20XX",
                "key_achievements": [
                    "Created a cross-training program ensuring FOH staff members were able to perform confidently and effectively in all positions.",
                    "Grew customer base and increased restaurant social media accounts by 19% through interactive promotions, engaging postings, and contests.",
                    "Created and implemented staff health and safety standards compliance training program, achieving a score of 99% from the Board of Health.",
                    "Successfully redesigned existing inventory system, ordering and food storage practices, resulting in a 6% decrease in food waste and higher net profits."
                ]
            }
        ],
        "education": [
            "B.S. in Business Administration | June 20XX | Bigtown College, Chicago, Illinois",
            "A.A. in Hospitality Management | June 20XX | Bigtown College, Chicago, Illinois"
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
    
    #input_json  = ATSParser('src/templates/ATS classic HR resume.docx').parse_docx_to_json()
    # Generate and print summary
    print("Generating professional summary (this may take a moment)...")
    summary = generate_summary(input_json)
    print("\nGenerated Professional Summary:")
    print(summary)
    
    # Save the summary to a file
    with open('professional_summary.txt', 'w') as f:
        f.write(summary)
