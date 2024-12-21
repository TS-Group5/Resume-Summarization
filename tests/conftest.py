"""
Pytest configuration and fixtures.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def sample_input_data():
    """Sample input data for testing summary generation."""
    return {
        'name': 'Test User',
        'current_role': 'Software Engineer',
        'years_experience': 5,
        'companies': [
            'Tech Corp',
            'Software Inc'
        ],
        'achievements': [
            'improved system performance by 50%',
            'led team of 5 developers'
        ],
        'skills': [
            'Python',
            'Machine Learning',
            'Cloud Computing'
        ],
        'education': [
            'M.S. in Computer Science',
            'B.S. in Software Engineering'
        ],
        'recognition': 'top performer award'
    }

@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for model caching during tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after tests
    shutil.rmtree(temp_dir)

@pytest.fixture
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture
def mock_model_response():
    """Sample model response for testing."""
    return {
        'summary': 'Experienced Software Engineer with 5 years of experience at Tech Corp and Software Inc. ' \
                  'Led team of 5 developers and improved system performance by 50%. ' \
                  'Skilled in Python, Machine Learning and Cloud Computing.',
        'achievements': 'Key achievements include improving system performance by 50% and leading a team of 5 developers.',
        'skills_summary': 'Expert in Python programming, Machine Learning algorithms and Cloud Computing platforms.'
    }
