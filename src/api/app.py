from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import yaml
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from fastapi.responses import Response
import time
import logging
import utils.clearml_utils as clearml_utils
from utils.report_manager import ReportManager
from utils.resource_monitor import ResourceMonitor
from utils.quality_monitor import QualityMonitor
from rouge_score import rouge_scorer
import warnings
from models.generic_gpt2_model import GenericGPT2Model
from parsers.ats_parser import ATSParser
from parsers.industry_manager_parser import IndustryManagerParser

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Set up Python logging
logging.basicConfig(level=logging.INFO)
app_logger = logging.getLogger(__name__)

# Initialize ClearML task
app_logger.info("Initializing ClearML task...")
task = clearml_utils.init_clearml_task(
    project_name="Resume-Summarization",
    task_name="API-Service",
    task_type="inference",
    tags=["api"]
)

# Initialize QualityMonitor with the task
quality_monitor = QualityMonitor(task)

clearml_logger = clearml_utils.get_logger()

# Initialize managers and monitors
report_manager = ReportManager(task)
resource_monitor = ResourceMonitor(task)
resource_monitor.start_monitoring()

# Log initial configuration
report_manager.log_pipeline_start(config)
# Initialize model with warning suppression

warnings.filterwarnings("ignore", category=FutureWarning)

# Initialize model
app_logger.info("Initializing model...")
gpt2_model = GenericGPT2Model()
app_logger.info("Model initialized successfully")

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

class ScriptResponse(BaseModel):
    script: str
    template_type: str

@app.get("/health")
async def health():
    return {"status": "ok"}   

@app.get("/metrics")
async def metrics():
    """Endpoint for Prometheus metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/generate-script", response_model=ScriptResponse)
async def generate_script(
    file: UploadFile = File(...),
    template_type: str = Form(...),
):
    start_time = time.time()
    temp_path = None
    
    try:
        # Log request
        clearml_logger.report_text(
            "API Request",
            f"Template Type: {template_type}, File: {file.filename}"
        )
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        # Upload resume artifact
        task.upload_artifact(
            name="Uploaded Resume",
            artifact_object=temp_path,
            metadata={"template_type": template_type, "filename": file.filename}
        )
        # Use parser based on user's template selection
        if template_type.lower() == "ats":
            parser = ATSParser(temp_path)
            template_label = "ATS/HR"
        elif template_type.lower() == "industry":
            parser = IndustryManagerParser(temp_path)
            template_label = "Industry Manager"
        else:
            if ERROR_COUNT:
                ERROR_COUNT.labels(template_type="unknown", error_type="invalid_template").inc()
            raise HTTPException(
                status_code=400,
                detail="Invalid template type. Must be either 'ats' or 'industry'"
            )
        
        # Parse resume and generate script
        resume_data = parser.parse()
        print('==========================================',resume_data)
        script = gpt2_model.generate_summary(resume_data)
        generation_time = time.time() - start_time
        # Reference text for quality comparison (e.g., stored templates)
        reference_text = gpt2_model.reference_scripts.get(template_type.lower(), "")

        # Track quality
        quality_metrics = quality_monitor.track_generation_quality(
            generated_text= script,
            reference_text=reference_text,
            generation_time=generation_time,
            metadata={"template_type": template_type, "resume_name": file.filename}
        )

        # Upload generated script
        task.upload_artifact(
            name="Generated Script",
            artifact_object=script,
            metadata={"template_type": template_type}
        )
        
        # Log quality metrics
        quality_metrics = gpt2_model.quality_monitor.track_generation_quality(
            script,
            gpt2_model.reference_scripts.get(template_type.lower(), ""),
            generation_time=time.time() - start_time
        )
        
         # Log metrics
        processing_time = time.time() - start_time
        clearml_logger.report_scalar(
            title="API Metrics",
            series="Processing Time",
            value=processing_time,
            iteration=0
        )
        clearml_logger.report_scalar(
            title="API Metrics",
            series=f"Requests_{template_type}",
            value=1,
            iteration=0
        )
        
        # Log generated script
        clearml_logger.report_text(
            "Generated Script",
            script[:1000]  # Log first 1000 chars
        )
        # Record metrics if they exist
        if REQUESTS_TOTAL:
            REQUESTS_TOTAL.labels(template_type=template_label).inc()
        if PROCESSING_TIME:
            PROCESSING_TIME.labels(template_type=template_label).observe(time.time() - start_time)
        
        # Generate reports
        performance_metrics = {
            "processing_time": processing_time,
            "input_length": len(resume_data),
            "output_length": len(script),
            "template_type": template_type
        }
        report_manager.publish_performance_report(performance_metrics)
        
        # Generate quality report if metrics available
        if hasattr(gpt2_model, 'quality_monitor'):
            quality_metrics = gpt2_model.quality_monitor.get_latest_metrics()
            thresholds = {
                "rouge1": 0.4,
                "rouge2": 0.2,
                "rougeL": 0.3,
                "summary_length": 200
            }
            report_manager.publish_quality_report(quality_metrics, thresholds)
        
        # Generate summary report
        report_manager.publish_summary_report()

        return ScriptResponse(script=script, template_type=template_label)
    
    except Exception as e:
        # Log error and publish error report
        error_message = str(e)
        quality_monitor.track_error(error_message)
        app_logger.error(f"Error generating script: {str(e)}")
        report_manager.publish_error_report([{
            "type": type(e).__name__,
            "message": str(e),
            "timestamp": time.time(),
            "template_type": template_type
        }])
        # Record error metrics if they exist
        if ERROR_COUNT:
            error_type = type(e).__name__
            ERROR_COUNT.labels(
                template_type=template_type.lower(),
                error_type=error_type
            ).inc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    server_config = config["server"]["fastapi"]
    uvicorn.run(
        "app:app",
        host=server_config["host"],
        port=server_config["port"],
        reload=server_config["reload"]
    )
