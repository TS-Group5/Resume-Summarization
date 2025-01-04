"""Test suite for Industry Manager Parser."""
import unittest
import os
import sys
import logging
from docx import Document

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.parsers.industry_manager_parser import IndustryManagerParser

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class TestIndustryManagerParser(unittest.TestCase):
    """Test cases for Industry Manager Parser."""

    def setUp(self):
        """Set up test environment."""
        self.test_file = os.path.join(project_root, "src", "templates", "Industry manager resume.docx")
        self.parser = IndustryManagerParser(self.test_file)

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
            'name', 'current_role', 'companies', 'years_experience',
            'skills', 'achievements', 'contact_info'
        ]
        for field in required_fields:
            self.assertIn(field, result)

    def test_contact_info_structure(self):
        """Test if contact info has the correct structure."""
        result = self.parser.parse()
        contact_info = result.get('contact_info', {})
        self.assertIsInstance(contact_info, dict)
        self.assertIn('email', contact_info)
        self.assertIn('phone', contact_info)

    def test_companies_structure(self):
        """Test if companies section has the correct structure."""
        result = self.parser.parse()
        companies = result.get('companies', [])
        self.assertIsInstance(companies, list)
        if companies:  # If there are companies listed
            self.assertIsInstance(companies[0], str)
            self.assertTrue(all(isinstance(c, str) for c in companies))

    def test_skills_structure(self):
        """Test if skills section has the correct structure."""
        result = self.parser.parse()
        skills = result.get('skills', [])
        self.assertIsInstance(skills, list)
        if skills:  # If there are skills listed
            self.assertIsInstance(skills[0], str)
            self.assertTrue(all(isinstance(s, str) for s in skills))

    def test_achievements_structure(self):
        """Test if achievements section has the correct structure."""
        result = self.parser.parse()
        achievements = result.get('achievements', [])
        self.assertIsInstance(achievements, list)
        if achievements:  # If there are achievements listed
            self.assertIsInstance(achievements[0], str)
            self.assertTrue(all(isinstance(a, str) for a in achievements))

    def test_role_extraction(self):
        """Test if role extraction works with various formats."""
        result = self.parser.parse()
        role = result.get('current_role', '')
        self.assertIsInstance(role, str)
        # The role should be non-empty for a valid resume
        self.assertTrue(role)

    def test_industry_skills_detection(self):
        """Test if industry-specific skills are properly detected."""
        result = self.parser.parse()
        skills = result.get('skills', [])
        # Check for some common industry manager skills
        industry_skills = {
            'Team Management', 'Staff Training', 'Operations Management',
            'Inventory Control', 'Quality Assurance', 'Budget Management',
            'Leadership', 'Customer Service'
        }
        # At least some industry-specific skills should be present
        self.assertTrue(any(skill in industry_skills for skill in skills))

    def test_parse_with_nonexistent_file(self):
        """Test parser behavior with nonexistent file."""
        parser = IndustryManagerParser("nonexistent_file.docx")
        with self.assertRaises(Exception):
            parser.parse()

if __name__ == '__main__':
    unittest.main()
