from models.generic_gpt2_model import GenericGPT2Model

def main():
    # Create sample HR resume data
    hr_resume_data = {
        'name': 'Emily Johnson',
        'email': 'emily.johnson@email.com',
        'current_role': 'Senior HR Manager',
        'years_experience': 8,
        'contact_info': {
            'email': 'emily.johnson@email.com',
            'phone': '555-123-4567'
        },
        'skills': [
            'Talent Acquisition',
            'Employee Relations',
            'Performance Management',
            'Training & Development',
            'HR Policy Development',
            'HRIS Systems'
        ],
        'companies': [
            'Global Enterprises Inc.',
            'TalentFirst Solutions'
        ],
        'achievements': [
            'Reduced employee turnover by 25% through implementation of comprehensive employee engagement program and structured exit interviews',
        ],
        'education': [
            {
                'degree': "Master's in Human Resource Management",
                'institution': 'State University'
            }
        ]
    }

    # Initialize the model
    model = GenericGPT2Model()

    # Generate the script
    script = model.generate_summary(hr_resume_data)
    
    # Print the generated script
    print("\n" + "="*50)
    print("Generated Video Script:")
    print("-"*50)
    print(script)
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
