"""
Tests for the summary generation script.
"""

import pytest
from pathlib import Path
from src.generate_summary import ResumeModelFactory

def test_model_factory_creation():
    """Test that the model factory can be created."""
    factory = ResumeModelFactory()
    assert factory is not None
    assert factory.cache is not None

@pytest.mark.parametrize("model_type,model_size", [
    ("t5", "base"),
    ("gpt2", "base"),
    ("bart", "base"),
])
def test_model_generation(model_type, model_size, sample_input_data):
    """Test summary generation with different models."""
    factory = ResumeModelFactory()
    model = factory.create_model(model_type, model_size)
    
    # Test that the model can generate a prompt
    prompt = model.generate_prompt(sample_input_data)
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    
    # Check that key information is in the prompt
    assert sample_input_data['name'] in prompt
    assert sample_input_data['current_role'] in prompt

def test_invalid_model_type():
    """Test that invalid model types raise an error."""
    factory = ResumeModelFactory()
    with pytest.raises(ValueError):
        factory.create_model("invalid_model", "base")
