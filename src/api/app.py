from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import yaml
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from fastapi.responses import Response
import time
import logging
from clearml import Task

from utils.clearml_utils import init_clearml_task, log_metric, log_text
from utils.resource_monitor import ResourceMonitor
from utils.quality_monitor import QualityMonitor
from utils.pipeline_manager import ResumePipeline
from models.generic_gpt2_model import GenericGPT2Model
from parsers.ats_parser import ATSParser
from parsers.industry_manager_parser import IndustryManagerParser

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Global variables for components
api_task = None
gpt2_model = None
resource_monitor = None
quality_monitor = None
pipeline = None

def initialize_components():
    """Initialize all components if not already initialized."""
    global api_task, gpt2_model, resource_monitor, quality_monitor, pipeline
    
    try:
        # Check if we already have a task
        api_task = Task.current_task()
        if not api_task:
            logger.info("Initializing ClearML task...")
            api_task = init_clearml_task(task_name="api-monitoring", task_type="data_processing")
        
        if not gpt2_model:
            logger.info("Initializing model...")
            gpt2_model = GenericGPT2Model(task=api_task)
            
        if not resource_monitor:
            logger.info("Initializing resource monitor...")
            resource_monitor = ResourceMonitor(task=api_task)
            resource_monitor.start_monitoring()
            
        if not quality_monitor:
            logger.info("Initializing quality monitor...")
            quality_monitor = QualityMonitor(task=api_task)
            
        if not pipeline:
            logger.info("Initializing pipeline...")
            pipeline = ResumePipeline()
            
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        raise

# Initialize FastAPI app
app = FastAPI(
    title="Resume Video Script Generator API",
    description="API for generating video scripts from resume templates",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components on startup
@app.on_event("startup")
async def startup_event():
    initialize_components()

@app.on_event("shutdown")
async def shutdown_event():
    if resource_monitor:
        resource_monitor.stop_monitoring()

class ScriptResponse(BaseModel):
    script: str
    template_type: str

@app.get("/metrics")
async def metrics():
    """Endpoint for Prometheus metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

def get_parser(template_type: str, file_path: str):
    """Get the appropriate parser based on template type."""
    if template_type.lower() == "ats":
        return ATSParser(file_path)
    elif template_type.lower() == "industry":
        return IndustryManagerParser(file_path)
    else:
        raise ValueError(f"Unsupported template type: {template_type}")

@app.post("/generate-script")
async def generate_script(
    file: UploadFile = File(...),
    template_type: str = Form(...),
    target_language: Optional[str] = Form(None)
):
    """Generate a script from a resume file."""
    try:
        # Read the file content
        content = await file.read()
        temp_file_path = f"temp_{file.filename}"
        
        try:
            # Save the content to a temporary file
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(content)
            
            # Process the resume
            parser = get_parser(template_type, temp_file_path)
            resume_data = parser.parse()
            start_time = time.time()
            script = gpt2_model.generate_summary(resume_data)
            generation_time = time.time() - start_time
            
            # Log metrics
            if quality_monitor:
                quality_monitor.track_generation_quality(
                    generated_text=script,
                    reference_text=gpt2_model._prepare_input_text(resume_data),
                    generation_time=generation_time,
                    metadata={"template_type": template_type}
                )
            
            return {
                "script": script,
                "template_type": template_type,
                "target_language": target_language
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        if quality_monitor:
            quality_monitor.log_error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Prometheus metrics - use a try-except to handle duplicate registration
try:
    REQUESTS_TOTAL = Counter(
        'resume_video_requests_total',
        'Total number of requests processed',
        ['template_type']
    )
except ValueError:
    REQUESTS_TOTAL = REGISTRY.get_sample_value('resume_video_requests_total')

try:
    PROCESSING_TIME = Histogram(
        'resume_video_processing_seconds',
        'Time spent processing resume',
        ['template_type']
    )
except ValueError:
    PROCESSING_TIME = REGISTRY.get_sample_value('resume_video_processing_seconds')

try:
    ERROR_COUNT = Counter(
        'resume_video_errors_total',
        'Total number of errors encountered',
        ['template_type', 'error_type']
    )
except ValueError:
    ERROR_COUNT = REGISTRY.get_sample_value('resume_video_errors_total')

if __name__ == "__main__":
    try:
        # Get server configuration
        server_config = config.get("server", {}).get("fastapi", {})
        host = server_config.get("host", "0.0.0.0")
        port = server_config.get("port", 8000)
        
        # Start the server
        logger.info(f"Starting FastAPI server on {host}:{port}")
        uvicorn.run(
            "api.app:app",
            host=host,
            port=port,
            reload=server_config.get("reload", True)
        )
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise
