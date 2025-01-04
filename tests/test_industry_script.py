from models.generic_gpt2_model import GenericGPT2Model
from parsers.industry_manager_parser import IndustryManagerParser

def main():
    # Initialize the parser with the resume path
    resume_path = "src/templates/Industry manager resume.docx"
    parser = IndustryManagerParser(resume_path)
    
    # Parse the resume
    resume_data = parser.parse()
    
    # Initialize the model
    model = GenericGPT2Model()

    # Generate the script
    script = model.generate_summary(resume_data)
    
    # Print the generated script
    print("\n" + "="*50)
    print("Generated Video Script:")
    print("-"*50)
    print(script)
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
