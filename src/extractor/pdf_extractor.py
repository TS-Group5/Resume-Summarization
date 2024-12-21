import json
from PyPDF2 import PdfReader

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to parse static format resumes
def parse_static_resume(text):
    def extract_section(start_marker, end_marker=None):
        """Helper function to extract text between markers."""
        if not text or not start_marker:
            return ""
        start_index = text.find(start_marker)
        if start_index == -1:
            return ""
        start_pos = start_index + len(start_marker)
        
        if end_marker:
            end_index = text.find(end_marker, start_pos)
            if end_index == -1:
                end_index = len(text)
        else:
            end_index = len(text)
            
        return text[start_pos:end_index].strip()
    
    parsed_resume = {}

    # Personal Details
    parsed_resume["personal_details"] = {
        "name": extract_section("Integration Architect", "MANAGER AND INTEGRATION ARCHITECT") or "Not found",
        "location": "Hyderabad",  # Location can be fixed if static
        "email": extract_section("etagowni@outlook.com", "\n") or "Not found",
        "phone": extract_section("+91", "\n") or "Not found"
    }

    # Summary
    parsed_resume["summary"] = extract_section("Integration Architect", "WORK EXPERIENCE") or "Not found"

    # Work Experience
    work_exp_text = extract_section("WORK EXPERIENCE", "TECHNOLOGIES")
    work_experience = []
    if work_exp_text:
        current_role = None
        for line in work_exp_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.isupper():  # Assume uppercase indicates a new role
                if current_role:
                    work_experience.append(current_role)
                current_role = {"role": line, "responsibilities": []}
            elif "Pvt Ltd" in line or "Ind Pvt Ltd" in line:
                if current_role:
                    current_role["company"] = line
            elif "-" in line:
                if current_role:
                    current_role["duration"] = line
            else:
                if current_role:
                    current_role["responsibilities"].append(line)
        if current_role:
            work_experience.append(current_role)
    parsed_resume["work_experience"] = work_experience

    # Skills
    skills_text = extract_section("TECHNOLOGIES", "CERTIFICATIONS")
    parsed_resume["skills"] = [skill.strip() for skill in skills_text.splitlines() if skill.strip()] if skills_text else []

    # Certifications
    certifications_text = extract_section("CERTIFICATIONS", "PROJECTS")
    parsed_resume["certifications"] = [cert.strip() for cert in certifications_text.splitlines() if cert.strip()] if certifications_text else []

    # Projects
    projects_text = extract_section("PROJECTS")
    projects = []
    if projects_text:
        current_project = None
        for line in projects_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.isupper():  # Assume uppercase indicates a new project
                if current_project:
                    projects.append(current_project)
                current_project = {"name": line, "description": ""}
            else:
                if current_project:
                    current_project["description"] = (current_project["description"] + " " + line).strip()
        if current_project:
            projects.append(current_project)
    parsed_resume["projects"] = projects

    return parsed_resume

# Main execution
if __name__ == "__main__":
    pdf_path = "./data/AnilKumar - CV.pdf"  # Replace with the path to the resume file
    resume_text = extract_text_from_pdf(pdf_path)
    parsed_resume = parse_static_resume(resume_text)

    # Save to JSON
    with open("parsed_resume.json", "w") as json_file:
        json.dump(parsed_resume, json_file, indent=4)

    print("Resume parsed and saved to parsed_resume.json")
