"""
Tests for the model factory.
"""

import pytest
from src.models.model_factory import ResumeModelFactory
from src.models.t5_model import T5ResumeModel
from src.models.gpt2_model import GPT2ResumeModel
from src.models.bart_model import BartResumeModel

def test_model_factory_initialization():
    """Test that ResumeModelFactory initializes correctly."""
    factory = ResumeModelFactory()
    assert factory.cache is not None

@pytest.mark.parametrize("model_type,model_size,expected_class", [
    ("t5", "base", T5ResumeModel),
    ("gpt2", "base", GPT2ResumeModel),
    ("bart", "base", BartResumeModel),
])
def test_create_model(model_type, model_size, expected_class):
    """Test model creation for different types."""
    factory = ResumeModelFactory()
    model = factory.create_model(model_type, model_size)
    assert isinstance(model, expected_class)

def test_invalid_model_type():
    """Test that creating an invalid model type raises an error."""
    factory = ResumeModelFactory()
    with pytest.raises(ValueError):
        factory.create_model("invalid_model", "base")
