from models.model_factory import ResumeModelFactory
from datetime import datetime
import sys

from src.parsers.ats_parser import ATSParser as ATSParser
from src.parsers.industry_manager_parser import IndustryManagerParser as IndustryManagerParser

def get_available_models():
    """Return a list of available models and their descriptions."""
    return {
        "t5-base": {
            "description": "T5 model - Good at following structured prompts",
            "strengths": ["Follows templates well", "Good at structured tasks", "Fast generation"],
            "best_for": "Professional, template-based summaries"
        },
        "gpt2-medium": {
            "description": "GPT-2 model - Natural language generation",
            "strengths": ["Natural writing style", "Creative outputs", "Good context understanding"],
            "best_for": "Natural-sounding, creative summaries"
        },
        "bart-large": {
            "description": "BART model - Good at both understanding and generation",
            "strengths": ["Balanced performance", "Good comprehension", "Reliable outputs"],
            "best_for": "Well-balanced, comprehensive summaries"
        }
    }

def display_model_info(model_info):
    """Display detailed information about a model."""
    print(f"\nModel Details:")
    print("-" * 50)
    print(f"Description: {model_info['description']}")
    print("\nStrengths:")
    for strength in model_info['strengths']:
        print(f"  • {strength}")
    print(f"\nBest for: {model_info['best_for']}")

def select_model():
    """Interactive model selection with detailed information."""
    available_models = get_available_models()
    
    while True:
        print("\nAvailable Models:")
        print("-" * 50)
        for i, (model_name, info) in enumerate(available_models.items(), 1):
            print(f"{i}. {model_name}: {info['description']}")
        print("\nOptions:")
        print("  • Enter model number (1-3) to select a model")
        print("  • Enter 'i' followed by model number for more info (e.g., 'i1')")
        print("  • Enter 'a' to try all models")
        print("  • Enter 'q' to quit")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'q':
            print("\nExiting program.")
            sys.exit(0)
        
        if choice == 'a':
            return None
        
        if choice.startswith('i'):
            try:
                model_num = int(choice[1:]) - 1
                if 0 <= model_num < len(available_models):
                    model_info = list(available_models.values())[model_num]
                    display_model_info(model_info)
                    input("\nPress Enter to continue...")
                else:
                    print(f"Please enter a number between 1 and {len(available_models)}")
            except ValueError:
                print("Invalid input. Please try again.")
            continue
        
        try:
            choice = int(choice)
            if 1 <= choice <= len(available_models):
                selected_model = list(available_models.keys())[choice - 1]
                model_type, model_size = selected_model.split('-')
                
                # Display selected model info
                print(f"\nSelected: {selected_model}")
                display_model_info(available_models[selected_model])
                
                confirm = input("\nProceed with this model? (y/n): ").strip().lower()
                if confirm == 'y':
                    return [(model_type, model_size)]
            else:
                print(f"Please enter a number between 1 and {len(available_models)}")
        except ValueError:
            print("Invalid input. Please try again.")

def main():
    # Example input data
    input_data = {
        'name': 'May Riley',
        'current_role': 'Restaurant Manager',
        'years_experience': 5,
        'companies': [
            'Contoso Bar and Grill',
            'Fourth Coffee Bistro'
        ],
        'achievements': [
            'reduced costs by 7% via controls on overtime, operational efficiencies, and reduced waste',
            'consistently exceed monthly sales goals by a least 10% by training FOH staff on upselling techniques via a featured food and beverage program'
        ],
        'skills': [
            'Accounting & Budgeting',
            'Proficient with POS systems',
            'Excellent interpersonal and communication skills'
        ],
        'education': [
            'B.S. in Business Administration',
            'A.A. in Hospitality Management'
        ],
        'recognition': 'one of the top restaurant managers in our area'
    }

    print("\nProfessional Summary Generator")
    print("=" * 50)
    print("This tool helps generate professional summaries using different AI models.")
    print("Each model has its own strengths and characteristics.")
    

    #ats_resume_path = '/Users/anilkumar/Desktop/tv3/src/templates/ATS classic HR resume.docx'
    #input_data = ATSParser(ats_resume_path).parse_docx_to_json()
    
    industry_manager_resume_path = '/Users/anilkumar/Desktop/tv3/src/templates/Industry manager resume.docx'
    input_data = IndustryManagerParser(industry_manager_resume_path).parse_docx_to_json()

    # Initialize model factory
    factory = ResumeModelFactory()

    # Get model selection from user
    model_configs = select_model()
    if model_configs is None:  # Try all models
        model_configs = [
            ("t5", "base"),
            ("gpt2", "medium"),
            ("bart", "large")
        ]
    
    # Generate summaries
    for model_type, model_size in model_configs:
        print(f"\nUsing {model_type.upper()}-{model_size} model:")
        print("-" * 50)
        print("Generating summary (this may take a moment)...")
        
        try:
            model = factory.create_model(model_type, model_size)
            summary = model.generate_summary(input_data)
            print(f"\nGenerated Professional Summary:\n{summary}")
        except Exception as e:
            print(f"Error with {model_type}-{model_size} model: {e}")
        
        if len(model_configs) > 1:
            input("\nPress Enter to continue to the next model...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
        sys.exit(0)
