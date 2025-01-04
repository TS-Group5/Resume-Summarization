# Enhancers Documentation

## FewShotEnhancer

The `FewShotEnhancer` class implements few-shot learning capabilities.

### Class Definition
```python
class FewShotEnhancer:
    def __init__(self, examples: List[Dict[str, str]], template: str):
        """Initialize few-shot enhancer.
        
        Args:
            examples (List[Dict[str, str]]): List of few-shot examples
            template (str): Template for formatting examples
        """
```

### Key Methods

#### enhance_prompt
```python
def enhance_prompt(self, text: str) -> str:
    """Add few-shot examples to input text.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Enhanced prompt with few-shot examples
    """
```

#### update_examples
```python
def update_examples(self, new_examples: List[Dict[str, str]]):
    """Update few-shot example set.
    
    Args:
        new_examples (List[Dict[str, str]]): New examples to use
    """
```

## ChainOfThoughtEnhancer

The `ChainOfThoughtEnhancer` class implements chain-of-thought reasoning.

### Class Definition
```python
class ChainOfThoughtEnhancer:
    def __init__(self, reasoning_template: str):
        """Initialize chain-of-thought enhancer.
        
        Args:
            reasoning_template (str): Template for reasoning steps
        """
```

### Key Methods

#### add_reasoning_steps
```python
def add_reasoning_steps(self, prompt: str) -> str:
    """Add reasoning steps to generation prompt.
    
    Args:
        prompt (str): Input prompt
        
    Returns:
        str: Enhanced prompt with reasoning steps
    """
```

#### analyze_experience
```python
def analyze_experience(self, text: str) -> List[str]:
    """Break down experience into logical steps.
    
    Args:
        text (str): Input experience text
        
    Returns:
        List[str]: List of analyzed experience steps
    """
```
