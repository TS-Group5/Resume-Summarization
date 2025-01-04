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
from contextlib import asynccontextmanager

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
        # Only initialize ClearML task once
        if not api_task:
            logger.info("Initializing ClearML task...")
            api_task = init_clearml_task(task_name="api-monitoring", task_type="data_processing")
        
        if not gpt2_model:
            logger.info("Initializing model...")
            gpt2_model = GenericGPT2Model(task=api_task)
            
        if not resource_monitor:
            logger.info("Initializing resource monitor...")
            resource_monitor = ResourceMonitor(task=api_task)
            # Only start monitoring if not already running
            if not getattr(resource_monitor, '_monitoring_thread', None):
                resource_monitor.start_monitoring()
            
        if not quality_monitor:
            logger.info("Initializing quality monitor...")
            quality_monitor = QualityMonitor(task=api_task)
            
        if not pipeline:
            logger.info("Initializing pipeline...")
            pipeline = ResumePipeline(queue="default")
            
            # Configure pipeline steps - do this only once
            pipeline.add_parser_step()
            pipeline.add_generation_step(
                model_config=config["model"],
                requirements={"pip": "requirements.txt"}
            )
            pipeline.add_quality_check_step(
                quality_thresholds={
                    "rouge1_f1": 0.4,
                    "rouge2_f1": 0.2,
                    "rougeL_f1": 0.3
                },
                requirements={"pip": "requirements.txt"}
            )
            
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        raise

def cleanup_components():
    """Cleanup all components."""
    global resource_monitor
    
    try:
        if resource_monitor:
            resource_monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"Error cleaning up components: {e}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    # Startup
    initialize_components()
    yield
    # Shutdown
    cleanup_components()

# Initialize FastAPI app
app = FastAPI(
    title="Resume Video Script Generator API",
    description="API for generating video scripts from resume templates",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScriptResponse(BaseModel):
    script: str
    template_type: str

@app.get("/")
async def root():
    """Root endpoint to check if API is running."""
    return {"status": "ok", "message": "Resume Video Script Generator API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "model": gpt2_model is not None,
            "resource_monitor": resource_monitor is not None,
            "quality_monitor": quality_monitor is not None,
            "pipeline": pipeline is not None
        }
    }

@app.get("/metrics")
async def metrics():
    """Endpoint for Prometheus metrics."""
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

@app.post("/generate", response_model=ScriptResponse)
async def generate_script(
    file: UploadFile = File(...),
    template_type: str = Form(...),
    target_language: Optional[str] = Form(None)
):
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

def get_parser(template_type: str, file_path: str):
    """Get the appropriate parser based on template type."""
    if template_type.lower() == "ats":
        return ATSParser(file_path)
    elif template_type.lower() == "industry":
        return IndustryManagerParser(file_path)
    else:
        raise ValueError(f"Unsupported template type: {template_type}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get host and port from config or use defaults
    host = config.get("api", {}).get("host", "0.0.0.0")
    port = config.get("api", {}).get("port", 8080)
    
    # Start the server
    logger.info(f"Starting FastAPI server on {host}:{port}")
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        workers=1
    )
