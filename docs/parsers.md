# Parsers Documentation

The project includes two specialized parsers for different resume templates:
1. ATSParser for HR/ATS resumes
2. IndustryManagerParser for industry management resumes

## ATSParser

The `ATSParser` class is designed to parse ATS-optimized HR resumes.

### Class Definition
```python
class ATSParser:
    def __init__(self, resume_path: str):
        """Initialize ATS parser with resume file path.
        
        Args:
            resume_path (str): Path to the resume docx file
        """
```

### Key Methods

#### parse
```python
def parse(self) -> Dict[str, Any]:
    """Parse resume content into structured format.
    
    Returns:
        Dict[str, Any]: Structured resume data containing:
            - name (str): Full name
            - email (str): Contact email
            - current_role (str): Current position
            - years_experience (int): Years of experience
            - skills (List[str]): Professional skills
            - companies (List[str]): Previous companies
            - achievements (List[str]): Key achievements
            - education (List[Dict]): Educational background
    
    Raises:
        FileNotFoundError: If resume file doesn't exist
        ValueError: If resume format is invalid
    """
```

#### extract_sections
```python
def extract_sections(self) -> Dict[str, str]:
    """Extract different sections from the resume.
    
    Returns:
        Dict[str, str]: Mapping of section names to content
    """
```

## IndustryManagerParser

The `IndustryManagerParser` class is specialized for parsing industry management resumes.

### Class Definition
```python
class IndustryManagerParser:
    def __init__(self, resume_path: str):
        """Initialize industry manager parser with resume file path.
        
        Args:
            resume_path (str): Path to the resume docx file
        """
```

### Key Methods

#### parse
```python
def parse(self) -> Dict[str, Any]:
    """Parse industry manager resume into structured format.
    
    Returns:
        Dict[str, Any]: Structured resume data containing:
            - name (str): Full name
            - industry (str): Industry sector
            - management_level (str): Management level
            - team_size (int): Size of team managed
            - budget_responsibility (str): Budget management info
            - key_projects (List[Dict]): Major projects led
            - strategic_achievements (List[str]): Strategic wins
            - education (List[Dict]): Educational background
    
    Raises:
        FileNotFoundError: If resume file doesn't exist
        ValueError: If resume format is invalid
    """
```

#### extract_sections
```python
def extract_sections(self) -> Dict[str, str]:
    """Extract different sections from the resume.
    
    Returns:
        Dict[str, str]: Mapping of section names to content
    """
```

## Usage Example

```python
# Parse ATS/HR resume
ats_parser = ATSParser("src/templates/ATS classic HR resume.docx")
hr_data = ats_parser.parse()

# Parse Industry Manager resume
industry_parser = IndustryManagerParser("src/templates/Industry manager resume.docx")
manager_data = industry_parser.parse()
```

## Integration

The parsers are integrated with:
1. FastAPI backend for processing uploaded resumes
2. GenericGPT2Model for providing structured input
3. Streamlit UI for template selection and processing
