from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from fastapi.responses import Response
from clearml import Task, Logger, OutputModel

from models.generic_gpt2_model import GenericGPT2Model
from parsers.ats_parser import ATSParser
from parsers.industry_manager_parser import IndustryManagerParser

# Initialize ClearML Task
task = Task.init(
    project_name="Resume Script Generator",
    task_name="API Deployment Task",
    task_type=Task.TaskTypes.inference,
)
logger = task.get_logger()

# Initialize model
gpt2_model = GenericGPT2Model()

# Initialize Prometheus metrics
try:
    REQUESTS_TOTAL = Counter('resume_video_requests_total', 'Total requests processed', ['template_type'])
except ValueError:
    REQUESTS_TOTAL = REGISTRY.get_sample_value('resume_video_requests_total')

try:
    PROCESSING_TIME = Histogram('resume_video_processing_seconds', 'Processing time', ['template_type'])
except ValueError:
    PROCESSING_TIME = REGISTRY.get_sample_value('resume_video_processing_seconds')

try:
    ERROR_COUNT = Counter('resume_video_errors_total', 'Total errors encountered', ['template_type', 'error_type'])
except ValueError:
    ERROR_COUNT = REGISTRY.get_sample_value('resume_video_errors_total')

# FastAPI app
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

@app.get("/metrics")
async def metrics():
    """Endpoint for Prometheus metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/generate-script", response_model=ScriptResponse)
async def generate_script(file: UploadFile = File(...), template_type: str = Form(...)):
    start_time = time.time()
    temp_path = None

    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Log uploaded file name as a parameter
        task.connect({"file_name": file.filename, "template_type": template_type})

        # Use parser based on template type
        if template_type.lower() == "ats":
            parser = ATSParser(temp_path)
            template_label = "ATS/HR"
        elif template_type.lower() == "industry":
            parser = IndustryManagerParser(temp_path)
            template_label = "Industry Manager"
        else:
            if ERROR_COUNT:
                ERROR_COUNT.labels(template_type="unknown", error_type="invalid_template").inc()
            raise HTTPException(status_code=400, detail="Invalid template type. Must be either 'ats' or 'industry'")

        # Parse resume and generate script
        resume_data = parser.parse()
        script = gpt2_model.generate_summary(resume_data)

        # Log generated script to ClearML
        logger.report_text(f"Generated script: {script}")

        # Upload processed resume as an artifact
        OutputModel.upload(filename=temp_path, name="Processed Resume Data")

        # Record metrics if they exist
        if REQUESTS_TOTAL:
            REQUESTS_TOTAL.labels(template_type=template_label).inc()
        if PROCESSING_TIME:
            PROCESSING_TIME.labels(template_type=template_label).observe(time.time() - start_time)

        # Log processing time as a ClearML metric
        logger.report_scalar("Processing Time", template_label, time.time() - start_time)

        return ScriptResponse(script=script, template_type=template_label)

    except Exception as e:
        # Log errors with ClearML
        logger.report_text(f"Error occurred: {str(e)}")

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
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

# Close the ClearML task to ensure all logs and artifacts are saved
task.close()