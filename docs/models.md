# Models Documentation

## GenericGPT2Model

The `GenericGPT2Model` class is responsible for generating video scripts from parsed resume data using GPT-2.

### Class Definition
```python
class GenericGPT2Model:
    def __init__(self, model_name="gpt2", device="cpu"):
        """Initialize GPT2 model with specified configuration.
        
        Args:
            model_name (str): Name of the pretrained model to use
            device (str): Device to run the model on ('cpu' or 'cuda')
        """
```

### Key Methods

#### generate_summary
```python
def generate_summary(self, resume_data: Dict) -> str:
    """Generate a video script from parsed resume data.
    
    Args:
        resume_data (Dict): Parsed resume data containing sections like:
            - name (str): Full name
            - current_role (str): Current job title
            - skills (List[str]): List of skills
            - experience (List[Dict]): Work experience
            - education (List[Dict]): Educational background
            - achievements (List[str]): Notable achievements
        
    Returns:
        str: Generated video script
        
    Raises:
        ModelError: If generation fails
    """
```

#### preprocess_text
```python
def preprocess_text(self, text: str) -> str:
    """Clean and format input text for the model.
    
    Args:
        text (str): Raw input text
        
    Returns:
        str: Preprocessed text ready for model input
    """
```

#### postprocess_output
```python
def postprocess_output(self, output: str) -> str:
    """Clean and format model output into a well-structured video script.
    
    Args:
        output (str): Raw model output
        
    Returns:
        str: Formatted video script
    """
```

### GPT-2 Model Implementation

The system uses a fine-tuned GPT-2 model for generating video scripts from resume data. The implementation is designed to be industry-aware and produces highly relevant content based on the candidate's background.

### Model Configuration

```python
model_name = "gpt2"  # Base GPT2 model
generator = pipeline(
    'text-generation',
    model=model,
    tokenizer=tokenizer,
    max_length=800,    # Balanced length
    min_length=300,    # Ensure substantial content
    num_return_sequences=1,
    temperature=0.7,   # Balanced creativity
    top_p=0.9,
    top_k=50,
    repetition_penalty=1.2
)
```

### Industry-Specific Templates

The model uses specialized templates for different industries:

1. **IT/Software Development**
   - Focus on technical skills and projects
   - Emphasis on technologies and frameworks
   - Project-centric achievements

2. **Restaurant Management**
   - Emphasis on operations and service
   - Customer satisfaction metrics
   - Team management achievements

3. **Healthcare**
   - Patient care and compliance focus
   - Healthcare regulations knowledge
   - Process improvement metrics

### Prompt Engineering

The prompt structure includes:

1. **Resume Information**
   ```
   Name: [name]
   Current Role: [role]
   Years of Experience: [years]
   Company: [company]
   Skills: [skills]
   Key Achievement: [achievement]
   Contact: [email, phone]
   ```

2. **Industry Context**
   - Industry-specific terminology
   - Relevant metrics and achievements
   - Professional tone guidelines

3. **Script Structure**
   - Introduction
   - Experience
   - Skills
   - Achievement
   - Goals
   - Contact

### Post-Processing

The generated content goes through several validation steps:

1. **Section Validation**
   - Ensures all required sections are present
   - Checks for proper formatting
   - Validates contact information

2. **Content Enhancement**
   - Industry-specific terminology check
   - Professional tone verification
   - Formatting standardization

3. **Fallback Mechanism**
   - Default templates if generation fails
   - Industry-specific backup content
   - Standard formatting templates

### Usage Example

```python
# Initialize model
model = GenericGPT2Model()

# Example resume data
resume_data = {
    'name': 'John Doe',
    'current_role': 'Senior Software Engineer',
    'skills': ['Python', 'Machine Learning', 'Leadership'],
    'achievements': ['Led team of 5 engineers', 'Reduced costs by 40%']
}

# Generate video script
script = model.generate_summary(resume_data)
```

### Integration

The model is integrated with:
1. FastAPI backend for HTTP API access
2. Streamlit UI for interactive usage
3. ATSParser and IndustryManagerParser for resume data extraction

### Performance Considerations

- **Memory Usage**: The model is optimized for reasonable memory consumption
- **Generation Speed**: Typically 2-3 seconds per script
- **Quality vs Speed**: Parameters balanced for optimal output quality
- **Error Handling**: Robust fallback mechanisms for edge cases

### Future Improvements

1. **Model Enhancements**
   - Fine-tuning on industry-specific data
   - Improved prompt templates
   - Additional industry support

2. **Performance Optimization**
   - Caching frequently used prompts
   - Batch processing support
   - Memory optimization

3. **Quality Improvements**
   - Enhanced validation rules
   - More diverse templates
   - Better error handling
