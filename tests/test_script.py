import logging

from src.models.generic_gpt2_model import GenericGPT2Model

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Sample resume data
resume_data = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "current_role": "Senior Software Engineer",
    "years_experience": 8,
    "skills": [
        "Python Development",
        "Machine Learning",
        "AWS Cloud Architecture",
        "Team Leadership",
        "System Design",
        "Project Management",
        "Strategic Planning",
        "Data Analysis",
        "CI/CD",
        "Agile Methodologies",
    ],
    "companies": ["Tech Solutions Inc.", "Innovation Labs"],
    "achievements": [
        "Led a team of 5 engineers to deliver a cloud-native platform that reduced operational costs by 40% through automated scaling",
        "Implemented ML pipeline that improved prediction accuracy by 25% and reduced processing time by 60%",
        "Architected and deployed microservices that handle 1M+ daily requests with 99.9% uptime",
    ],
    "education": [
        {"degree": "Master's in Computer Science", "institution": "Stanford University"}
    ],
    "contact_info": {"email": "john.doe@example.com", "phone": "(123) 456-7890"},
}


def print_section(title, content):
    print("\n" + "=" * 50)
    print(f"{title}:")
    print("-" * 50)
    print(content)
    print("=" * 50)


# Initialize and run the model
logger.info("Initializing model (this may take a few minutes the first time)...")
model = GenericGPT2Model()
logger.info("Model initialized successfully")

logger.info("Generating video script...")
script = model.generate_summary(resume_data)
logger.info("Script generation completed")

print_section("Generated Video Script", script)
