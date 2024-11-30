import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
import io

# Configure Google API
GOOGLE_API_KEY = 'AIzaSyAdXJGPVX7_xO9U5R4AZ1HTixxHW4teqk4'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def process_file(uploaded_file):
    """
    Process the uploaded resume file and extract text content.
    
    Parameters:
    uploaded_file (File-like object): The uploaded resume file (PDF or DOCX)
    
    Returns:
    str: Extracted text from the resume
    """
    try:
        # Get the file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            # Process PDF file
            pdf_reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
            
        elif file_extension == 'docx':
            # Process DOCX file
            doc = Document(io.BytesIO(uploaded_file.getvalue()))
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
            return text
            
        else:
            return "Error: Unsupported file format. Please upload a PDF or DOCX file."
            
    except Exception as e:
        return f"Error processing file: {str(e)}"

def get_resume_summary(text):
    """
    Generate a structured summary of the resume using AI with themed sections.
    
    Parameters:
    text (str): The extracted text from the resume
    
    Returns:
    dict: AI-generated summary with themed sections
    """
    prompt = f"""You are a professional resume analyzer. Create a structured summary of the following resume.
    Your response must be a valid JSON object with exactly these four sections and nothing else.
    Do not include any explanations, only output the JSON object.

    The JSON structure must be:
    {{
        "Introduction": "<Brief professional overview focusing on current role and career objective>",
        "Experience": "<Key professional experiences, achievements, and responsibilities>",
        "Skills": "<Technical skills, tools, technologies, and core competencies>",
        "Contact": "<Professional background and key contact information>"
    }}

    Resume text to analyze:
    {text}
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean up the response to ensure valid JSON
        response_text = response.text.strip()
        # Remove any markdown code block indicators if present
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Parse the JSON response
        import json
        summary_dict = json.loads(response_text)
        
        # Verify all required sections are present
        required_sections = ["Introduction", "Experience", "Skills", "Contact"]
        for section in required_sections:
            if section not in summary_dict:
                summary_dict[section] = "Information not found in resume"
        
        return summary_dict
    except Exception as e:
        print(f"Error in get_resume_summary: {str(e)}")  # For debugging
        return {
            "Introduction": "Error processing resume",
            "Experience": "Error processing resume",
            "Skills": "Error processing resume",
            "Contact": "Error processing resume"
        }

# Main Streamlit app
st.set_page_config(
    page_title="Resume Summarizer", 
    page_icon="📄", 
    layout="wide"
)

st.title("Resume Summarizer")
st.write("Upload your resume to get a structured professional summary")

# Custom CSS for better section formatting
st.markdown("""
<style>
    .section-header {
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        color: #1f77b4;
    }
    .section-content {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .theme-text {
        color: #666;
        font-style: italic;
        font-size: 14px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Choose a resume file", type=['pdf', 'docx'])

if uploaded_file is not None:
    with st.spinner('Processing resume...'):
        # Extract text from the resume
        resume_text = process_file(uploaded_file)
        
        if not resume_text.startswith("Error"):
            # Generate summary
            summary_dict = get_resume_summary(resume_text)
            
            # Display each section with custom styling
            sections = {
                "Introduction": "minimalist professional office space, soft lighting, modern design",
                "Experience": "corporate meeting room with city skyline view, professional atmosphere",
                "Skills": "modern tech workspace with multiple screens, clean design",
                "Contact": "contemporary networking space, professional networking event setup"
            }
            
            for section, theme in sections.items():
                st.markdown(f'<div class="section-header">{section}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="section-content">{summary_dict[section]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="theme-text">Theme: {theme}</div>', unsafe_allow_html=True)
                st.markdown("---")
            
            # Option to view original text
            if st.checkbox("View extracted text"):
                st.text_area("Original Resume Text", resume_text, height=300)
        else:
            st.error(resume_text)
