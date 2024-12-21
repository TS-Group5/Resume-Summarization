"""
Tests for the model implementations.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.models.t5_model import T5ResumeModel
from src.models.gpt2_model import GPT2ResumeModel
from src.models.bart_model import BartResumeModel

MODEL_MOCKS = {
    T5ResumeModel: ('transformers.T5Tokenizer', 'transformers.T5ForConditionalGeneration'),
    GPT2ResumeModel: ('transformers.GPT2Tokenizer', 'transformers.GPT2LMHeadModel'),
    BartResumeModel: ('transformers.BartTokenizer', 'transformers.BartForConditionalGeneration')
}

@pytest.mark.parametrize("model_class,model_name", [
    (T5ResumeModel, "t5-base"),
    (GPT2ResumeModel, "gpt2"),
    (BartResumeModel, "facebook/bart-base"),
])
def test_model_initialization(model_class, model_name, temp_cache_dir):
    """Test that models initialize correctly with cache."""
    tokenizer_path, model_path = MODEL_MOCKS[model_class]

    with patch(tokenizer_path) as mock_tokenizer_cls, \
         patch(model_path) as mock_model_cls, \
         patch('transformers.PreTrainedTokenizer.from_pretrained') as mock_base_tokenizer, \
         patch('transformers.PreTrainedModel.from_pretrained') as mock_base_model:

        # Setup mocks
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_config = MagicMock()
        
        # Configure mocks
        mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
        mock_model_cls.from_pretrained.return_value = mock_model
        mock_base_tokenizer.return_value = mock_tokenizer
        mock_base_model.return_value = mock_model
        
        # Initialize model
        model = model_class(model_name, cache_dir=temp_cache_dir)

        # Verify model was initialized correctly
        assert model.model == mock_model
        assert model.tokenizer == mock_tokenizer
        assert model.config['model']['name'] == model_name

@pytest.mark.parametrize("model_class", [
    T5ResumeModel,
    GPT2ResumeModel,
    BartResumeModel,
])
def test_generate_prompt(model_class, sample_input_data):
    """Test prompt generation for each model."""
    tokenizer_path, model_path = MODEL_MOCKS[model_class]
    
    with patch(tokenizer_path) as mock_tokenizer_cls, \
         patch(model_path) as mock_model_cls:
        
        # Setup mocks
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
        mock_model_cls.from_pretrained.return_value = mock_model
        
        model = model_class()
        prompt = model.generate_prompt(sample_input_data)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        
        # Check if key information is included in the prompt
        assert sample_input_data['name'] in prompt
        assert sample_input_data['current_role'] in prompt

@pytest.mark.parametrize("model_class", [
    T5ResumeModel,
    GPT2ResumeModel,
    BartResumeModel,
])
def test_format_template_data(model_class, sample_input_data):
    """Test template data formatting for each model."""
    tokenizer_path, model_path = MODEL_MOCKS[model_class]
    
    with patch(tokenizer_path) as mock_tokenizer_cls, \
         patch(model_path) as mock_model_cls:
        
        # Setup mocks
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
        mock_model_cls.from_pretrained.return_value = mock_model
        
        model = model_class()
        formatted = model.format_template_data(sample_input_data)
        assert isinstance(formatted, dict)
        
        # Check that lists are properly formatted
        assert isinstance(formatted['achievements'], str)
        assert isinstance(formatted['skills'], str)
        assert formatted['achievements'].startswith(sample_input_data['achievements'][0])

@pytest.mark.parametrize("model_class", [
    T5ResumeModel,
    GPT2ResumeModel,
    BartResumeModel,
])
def test_clean_output(model_class):
    """Test output cleaning for each model."""
    tokenizer_path, model_path = MODEL_MOCKS[model_class]

    with patch(tokenizer_path) as mock_tokenizer_cls, \
         patch(model_path) as mock_model_cls, \
         patch('transformers.PreTrainedTokenizer.from_pretrained') as mock_base_tokenizer, \
         patch('transformers.PreTrainedModel.from_pretrained') as mock_base_model:

        # Setup mocks
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
        mock_model_cls.from_pretrained.return_value = mock_model
        mock_base_tokenizer.return_value = mock_tokenizer
        mock_base_model.return_value = mock_model

        model = model_class()

        # Test empty string
        assert model.clean_output("") == ""
        assert model.clean_output(None) == ""

        # Test actual text cleaning
        test_output = "this is a test summary. it needs cleaning. THis has bad capitalization."
        cleaned = model.clean_output(test_output)
        assert isinstance(cleaned, str)
        assert cleaned != test_output  # Should be different after cleaning
        assert cleaned == "This is a test summary. It needs cleaning. This has bad capitalization."

        # Test edge cases
        assert model.clean_output("hello") == "Hello."
        assert model.clean_output("hello.") == "Hello."
        assert model.clean_output("hello..") == "Hello."
        assert model.clean_output("hello. . .") == "Hello."
