#!/usr/bin/env python3
"""
Script generator for video resumes.
Usage: python3 generate_video_script.py [resume_path]
"""

import sys
import os
from docx import Document
from models.generic_gpt2_model import GenericGPT2Model
from parsers.ats_parser import ATSParser
from parsers.industry_manager_parser import IndustryManagerParser
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_resume_content(file_path):
    """Analyze resume content to determine its type."""
    doc = Document(file_path)
    content = "\n".join([p.text for p in doc.paragraphs]).lower()
    
    # Technical indicators
    tech_keywords = {
        'programming': ['python', 'java', 'javascript', 'c++', 'ruby', 'golang', 'rust',
                       'react', 'angular', 'vue', 'node.js', 'django', 'flask',
                       'aws', 'azure', 'docker', 'kubernetes', 'git', 'ci/cd',
                       'machine learning', 'ai', 'data science', 'algorithms'],
        'database': ['sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch'],
        'tools': ['jenkins', 'jira', 'github', 'gitlab', 'bitbucket', 'terraform',
                 'ansible', 'maven', 'gradle', 'npm', 'webpack']
    }
    
    # Industry/Management indicators
    industry_keywords = {
        'management': ['operations manager', 'restaurant manager', 'retail manager',
                      'store manager', 'hospitality', 'customer service',
                      'inventory management', 'staff training', 'team leadership'],
        'operations': ['inventory', 'scheduling', 'budget', 'forecasting',
                      'quality control', 'safety compliance', 'vendor relations'],
        'service': ['customer satisfaction', 'guest services', 'food service',
                   'retail operations', 'guest experience', 'service standards']
    }
    
    # Count matches
    tech_count = sum(1 for category in tech_keywords.values() 
                    for keyword in category 
                    if keyword in content)
    
    industry_count = sum(1 for category in industry_keywords.values() 
                        for keyword in category 
                        if keyword in content)
    
    # Log the analysis
    logger.info(f"Technical keywords found: {tech_count}")
    logger.info(f"Industry keywords found: {industry_count}")
    
    # Determine resume type
    if tech_count > industry_count:
        logger.info("Detected: Technical Resume")
        return "technical"
    elif industry_count > tech_count:
        logger.info("Detected: Industry Management Resume")
        return "industry"
    else:
        # Default to ATS parser if unclear
        logger.info("Detected: General Resume (using ATS parser)")
        return "general"

def determine_parser(parser_type, file_path):
    """Determine which parser to use based on content analysis."""
    #resume_type = analyze_resume_content(file_path)
    
    if parser_type == "industry":
        return IndustryManagerParser(file_path)
    else:  # technical or general
        return ATSParser(file_path)

def main():
    # Get resume path from command line or use default
    if len(sys.argv) > 1:
        resume_path = sys.argv[1]
        logger.info(f"Resume path provided: {resume_path}")
        parser_type = sys.argv[2]
        logger.info(f"Resume type provided: {parser_type}")
    else:
        # Default to industry manager resume if no path provided
        resume_path = "src/templates/ATS classic HR resume.docx"
        parser_type = "ats"
        #resume_path = "src/templates/Industry manager resume.docx"
    
    # Ensure the file exists
    if not os.path.exists(resume_path):
        logger.error(f"Resume file not found: {resume_path}")
        sys.exit(1)
    
    try:
        # Initialize parser and model
        parser = determine_parser(parser_type, resume_path)
        model = GenericGPT2Model()
        
        # Parse resume
        logger.info(f"Parsing resume: {resume_path}")
        resume_data = parser.parse()
        
        # Generate script
        logger.info("Generating video script...")
        script = model.generate_summary(resume_data)
        
        # Print the result
        print("\n" + "="*50)
        print("Generated Video Script:")
        print("-"*50)
        print(script)
        print("="*50 + "\n")
        
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
