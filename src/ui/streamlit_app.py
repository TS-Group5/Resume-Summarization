import streamlit as st
import requests
import os
import yaml
from tempfile import NamedTemporaryFile
import time
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ..utils.clearml_utils import init_clearml_task, log_metric, log_text
from ..utils.resource_monitor import ResourceMonitor
from ..utils.quality_monitor import QualityMonitor

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize monitoring
resource_monitor = ResourceMonitor(task_name="streamlit-monitoring")
quality_monitor = QualityMonitor(task_name="streamlit-quality")

# Start resource monitoring
resource_monitor.start_monitoring()

# Configure page
st.set_page_config(
    page_title="Resume Video Script Generator",
    page_icon="🎥",
    layout="wide"
)

def main():
    st.title("Resume Video Script Generator 🎥")
    
    try:
        # Template selection
        template_type = st.selectbox(
            "Select Resume Template Type",
            ["ATS/HR Resume", "Industry Manager Resume"]
        )
        
        st.sidebar.header("About")
        st.sidebar.info(
            "This application generates video scripts from resume templates. "
            "Select your template type and upload your resume to get started."
        )
        
        # Main content
        st.header("Generate Video Script")
        
        # Convert selection to API parameter
        template_param = "ats" if template_type == "ATS/HR Resume" else "industry"
        
        # File uploader
        uploaded_file = st.file_uploader(
            f"Upload your {template_type}",
            type=config["file"]["allowed_extensions"],
            help="Upload your resume in PDF or DOCX format"
        )
        
        if uploaded_file is not None:
            with st.spinner('Generating video script...'):
                start_time = time.time()
                
                try:
                    # Prepare the files and data for the API request
                    files = {"file": uploaded_file}
                    data = {"template_type": template_param}
                    
                    # Make API request
                    response = requests.post(
                        f"{config['server']['fastapi']['url']}/generate",
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        script = result["script"]
                        
                        # Track UI metrics
                        processing_time = time.time() - start_time
                        log_metric("UI", "processing_time", processing_time)
                        log_metric("UI", "file_size", len(uploaded_file.getvalue()))
                        
                        # Display the generated script
                        st.success("Script generated successfully!")
                        st.text_area("Generated Video Script", script, height=300)
                        
                        # Track quality metrics
                        quality_monitor.track_generation_quality(
                            generated_text=script,
                            reference_text="",  # No reference text for now
                            generation_time=processing_time,
                            metadata={
                                "template_type": template_type,
                                "file_size": len(uploaded_file.getvalue()),
                                "ui_source": "streamlit"
                            }
                        )
                        
                    else:
                        error_msg = response.json().get("detail", "Unknown error occurred")
                        st.error(f"Error: {error_msg}")
                        log_text("UI", "error", error_msg)
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    log_text("UI", "error", str(e))
                    
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        log_text("UI", "error", str(e))

if __name__ == "__main__":
    try:
        main()
    finally:
        # Stop resource monitoring when the app stops
        resource_monitor.stop_monitoring()
