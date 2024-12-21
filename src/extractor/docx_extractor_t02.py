from docx import Document
import json
import re
from base_resume_parser import BaseResumeParser

class DocxResumeParser_T2(BaseResumeParser):
    """Implementation of resume parser for DOCX files"""
    
    def __init__(self):
        self.resume_data = {
            "personal_information": {
                "name": "",
                "contact": {
                    "address": "",
                    "phone": "",
                    "email": ""
                }
            },
            "positions": [],
            "education": [],
            "skills": [],
            "interests": []
        }
        self.current_section = None
        self.current_position = None

    @staticmethod
    def clean_text(text):
        """Clean and normalize text"""
        return text.strip().rstrip(".")

    def parse_personal_info(self, text, is_first_line):
        """Parse personal information from the line"""
        if is_first_line:
            self.resume_data["personal_information"]["name"] = text
        elif "•" in text and ("@" in text or "example.com" in text):
            # Parse contact information
            contact_parts = [part.strip() for part in text.split("•")]
            self.resume_data["personal_information"]["contact"].update({
                "address": contact_parts[0],
                "phone": contact_parts[1],
                "email": contact_parts[2]
            })

    def parse_position(self, text):
        """Parse position/experience information from the line"""
        if "|" in text:
            parts = [p.strip() for p in text.split("|")]
            if len(parts) >= 2:
                # If we find a position with location, it's likely part of the previous position
                if "Boomtown" in text or "Ohio" in text:
                    if self.current_position and len(parts) >= 3:
                        self.current_position = {
                            "role": parts[0],
                            "company": parts[1],
                            "duration": "",
                            "key_achievements": []
                        }
                        self.resume_data["positions"].append(self.current_position)
                else:
                    self.current_position = {
                        "role": parts[0],
                        "company": parts[1],
                        "duration": "",
                        "key_achievements": []
                    }
                    self.resume_data["positions"].append(self.current_position)
        elif self.current_position is not None:
            # Check if it's a duration (contains year or date range)
            if any(x in text for x in ["20XX", "–", "-"]) and len(text.split()) <= 8:
                self.current_position["duration"] = text
            # Otherwise it's likely an achievement
            elif len(text) > 0 and not text.lower().startswith(("skills", "education", "activities")):
                # Split into separate achievements if the line contains multiple sentences
                sentences = [s.strip() for s in text.split(".") if s.strip()]
                for sentence in sentences:
                    if len(sentence.split()) > 3:  # Only add if it's a substantial achievement
                        self.current_position["key_achievements"].append(self.clean_text(sentence))

    def parse_education(self, text):
        """Parse education information from the line"""
        if "|" in text and not any(x in text.lower() for x in ["skills", "activities", "gpa"]):
            self.resume_data["education"].append(text)

    def parse_skills(self, text):
        """Parse skills from the line"""
        if "•" in text and "education" not in text.lower():
            skills = [self.clean_text(skill) for skill in text.split("•") if skill.strip() and 
                     not any(x in skill.lower() for x in ["education", "gpa", "university", "college", "activities"])]
            self.resume_data["skills"].extend(skills)

    def parse_interests(self, text):
        """Parse interests/activities from the line"""
        if "•" in text:
            interests = [self.clean_text(interest) for interest in text.split("•") if interest.strip()]
            self.resume_data["interests"].extend(interests)

    def clean_up_data(self):
        """Clean and validate the parsed data"""
        # Clean up positions
        for position in self.resume_data["positions"]:
            # Remove achievements that look like durations or section headers
            position["key_achievements"] = [
                ach for ach in position["key_achievements"] 
                if not any(x in ach for x in ["20XX", "JUNE", "AUGUST"]) and 
                not any(ach.lower().startswith(x) for x in ["skills", "education", "activities"])
            ]
            
            # Remove duplicates while preserving order
            seen = set()
            position["key_achievements"] = [
                x for x in position["key_achievements"] 
                if not (x.lower() in seen or seen.add(x.lower()))
            ]

        # Remove duplicates from other sections while preserving order
        for section in ["education", "skills", "interests"]:
            seen = set()
            self.resume_data[section] = [
                x for x in self.resume_data[section] 
                if not (x.lower() in seen or seen.add(x.lower()))
            ]

    def parse_resume(self, file_path):
        """Parse the resume and return structured data"""
        # Load the document
        doc = Document(file_path)

        # Extract text lines
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip() != ""]

        # Parsing the document lines
        for i, line in enumerate(lines):
            # Personal Information
            self.parse_personal_info(line, i == 0)
            
            # Detect sections
            if line.lower() == "experience":
                self.current_section = "experience"
            elif line.lower() == "education":
                self.current_section = "education"
                self.current_position = None
            elif line.lower() == "skills":
                self.current_section = "skills"
                self.current_position = None
            elif line.lower() == "activities":
                self.current_section = "activities"
                self.current_position = None
            # Process sections
            elif self.current_section == "experience":
                self.parse_position(line)
            elif self.current_section == "education":
                self.parse_education(line)
            elif self.current_section == "skills":
                self.parse_skills(line)
            elif self.current_section == "activities":
                self.parse_interests(line)

        # Clean up the data
        self.clean_up_data()
        
        return json.dumps(self.resume_data, indent=4)

def extract_resume_to_json(doc_path):
    """Convenience function to parse a resume from a DOCX file"""
    
    return parser.parse_resume(doc_path)

# Usage
if __name__ == "__main__":
    parser = DocxResumeParser_T2()
    file_path = "data/ATS classic HR resume.docx"
    json_output = extract_resume_to_json(file_path)
    print(json_output)
