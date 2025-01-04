"""Test suite for ATS Parser."""
import unittest
import os
import sys
import logging
from docx import Document

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.parsers.ats_parser import ATSParser

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class TestATSParser(unittest.TestCase):
    """Test cases for ATS Parser."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_file = "src/templates/ATS classic HR resume.docx"
        cls.parser = ATSParser(cls.test_file)
    
    def test_file_exists(self):
        """Test if the test file exists."""
        self.assertTrue(os.path.exists(self.test_file))
    
    def test_parse_returns_dict(self):
        """Test if parse method returns a dictionary."""
        result = self.parser.parse()
        self.assertIsInstance(result, dict)
    
    def test_parse_has_required_fields(self):
        """Test if parsed data has all required fields."""
        result = self.parser.parse()
        required_fields = [
            'name',
            'contact_info',
            'skills',
            'education',
            'companies',
            'achievements'
        ]
        for field in required_fields:
            self.assertIn(field, result)
    
    def test_contact_info_structure(self):
        """Test if contact info has the correct structure."""
        result = self.parser.parse()
        contact_info = result['contact_info']
        required_contact_fields = ['email', 'phone']
        for field in required_contact_fields:
            self.assertIn(field, contact_info)
    
    def test_skills_structure(self):
        """Test if skills section has the correct structure."""
        result = self.parser.parse()
        skills = result['skills']
        self.assertIsInstance(skills, list)
        self.assertGreater(len(skills), 0)
        # Check if skills are strings
        for skill in skills:
            self.assertIsInstance(skill, str)
    
    def test_companies_structure(self):
        """Test if companies section has the correct structure."""
        result = self.parser.parse()
        companies = result['companies']
        self.assertIsInstance(companies, list)
        # Check if companies are strings
        for company in companies:
            self.assertIsInstance(company, str)
    
    def test_achievements_structure(self):
        """Test if achievements section has the correct structure."""
        result = self.parser.parse()
        achievements = result['achievements']
        self.assertIsInstance(achievements, list)
        # Check if achievements are strings
        for achievement in achievements:
            self.assertIsInstance(achievement, str)
    
    def test_education_structure(self):
        """Test if education section has the correct structure."""
        result = self.parser.parse()
        education = result['education']
        self.assertIsInstance(education, list)
    
    def test_parse_with_nonexistent_file(self):
        """Test parser behavior with nonexistent file."""
        with self.assertRaises(Exception):
            parser = ATSParser("nonexistent_file.docx")
            parser.parse()
    
    def test_technical_skills_detection(self):
        """Test if technical skills are properly detected."""
        result = self.parser.parse()
        skills = result['skills']
        # Convert skills to lowercase for case-insensitive comparison
        skills_lower = [skill.lower() for skill in skills]
        
        # Check if any common technical skills are detected
        technical_indicators = ['project management', 'data analytics', 'aws', 'r']
        found_technical = any(tech in skills_lower for tech in technical_indicators)
        self.assertTrue(found_technical)

    def test_role_extraction(self):
        """Test if role extraction works with various formats."""
        test_texts = [
            # Format 1: Direct role statement
            "Senior HR Manager\nLamna Healthcare Company",
            # Format 2: Role with company
            "Currently working as HR Manager at Lamna Healthcare",
            # Format 3: Role in summary
            "Experienced HR Manager with 6+ years in healthcare",
            # Format 4: Role with achievements
            "As an HR Manager, led recruitment initiatives",
            # Format 5: Role in contact section
            "Title: Senior HR Manager\nEmail: test@example.com",
        ]
        
        for text in test_texts:
            role = self.parser._extract_role(text)
            self.assertTrue(role, f"Failed to extract role from: {text}")
            self.assertIn("HR Manager", role, f"Incorrect role extracted from: {text}")

def print_parse_results():
    """Print parse results for manual inspection."""
    parser = ATSParser("src/templates/ATS classic HR resume.docx")
    result = parser.parse()
    print("\nParsed Resume Data:")
    print("=" * 50)
    for key, value in result.items():
        print(f"\n{key.upper()}:")
        print("-" * 30)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for k, v in item.items():
                        print(f"{k}: {v}")
                    print("-" * 20)
                else:
                    print(item)
        elif isinstance(value, dict):
            for k, v in value.items():
                print(f"{k}: {v}")
        else:
            print(value)

if __name__ == '__main__':
    # First print the parse results
    print("\nParsing Resume Data...")
    print("=" * 80)
    parser = ATSParser("src/templates/ATS classic HR resume.docx")
    result = parser.parse()
    
    # Print each section with formatting
    print("\n📋 BASIC INFORMATION:")
    print("-" * 40)
    print(f"Name: {result.get('name', 'N/A')}")
    print(f"Current Role: {result.get('current_role', 'N/A')}")
    print(f"Years of Experience: {result.get('years_experience', 'N/A')}")
    
    print("\n📞 CONTACT INFORMATION:")
    print("-" * 40)
    contact_info = result.get('contact_info', {})
    for key, value in contact_info.items():
        print(f"{key.title()}: {value}")
    
    print("\n💼 COMPANIES:")
    print("-" * 40)
    for company in result.get('companies', []):
        print(f"• {company}")
    
    print("\n🎯 ACHIEVEMENTS:")
    print("-" * 40)
    for achievement in result.get('achievements', []):
        print(f"• {achievement}")
    
    print("\n🔧 SKILLS:")
    print("-" * 40)
    for skill in result.get('skills', []):
        print(f"• {skill}")
    
    print("\n📚 EDUCATION:")
    print("-" * 40)
    for edu in result.get('education', []):
        print(f"• {edu}")
    
    print("\n" + "=" * 80)
    
    # Then run the tests
    unittest.main(verbosity=2)
