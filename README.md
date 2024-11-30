# Resume Summarizer

A Streamlit application that uses Google's Gemini Pro AI to generate structured summaries from resumes.

## Setup Instructions

1. Install Python 3.7 or higher
2. Install the required packages:
   ```bash
   pip install -r req.txt
   ```
3. Run the application:
   ```bash
   streamlit run resume_summary.py
   ```

## Features
- Supports PDF and DOCX resume formats
- Generates structured summaries with sections for:
  - Introduction (Professional overview)
  - Experience (Work history and achievements)
  - Skills (Technical skills and competencies)
  - Contact (Professional background)
- Clean, modern interface with themed sections
- Option to view extracted text from resume

## How to Use
1. Start the application using the command above
2. Upload a resume file (PDF or DOCX format)
3. The application will automatically:
   - Extract text from the resume
   - Generate a structured summary
   - Display the summary in themed sections
4. Use the "View extracted text" option to see the original resume text

## Requirements
See req.txt for the complete list of dependencies.
