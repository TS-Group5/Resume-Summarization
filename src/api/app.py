import os
import time
from typing import Optional

import uvicorn
import yaml
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel

from models.generic_gpt2_model import GenericGPT2Model
from parsers.ats_parser import ATSParser
from parsers.industry_manager_parser import IndustryManagerParser

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize model
gpt2_model = GenericGPT2Model()

# Prometheus metrics - use a try-except to handle duplicate registration
try:
    REQUESTS_TOTAL = Counter(
        "resume_video_requests_total",
        "Total number of requests processed",
        ["template_type"],
    )
except ValueError:
    REQUESTS_TOTAL = REGISTRY.get_sample_value("resume_video_requests_total")

try:
    PROCESSING_TIME = Histogram(
        "resume_video_processing_seconds",
        "Time spent processing resume",
        ["template_type"],
    )
except ValueError:
    PROCESSING_TIME = REGISTRY.get_sample_value("resume_video_processing_seconds")

try:
    ERROR_COUNT = Counter(
        "resume_video_errors_total",
        "Total number of errors encountered",
        ["template_type", "error_type"],
    )
except ValueError:
    ERROR_COUNT = REGISTRY.get_sample_value("resume_video_errors_total")

app = FastAPI(
    title="Resume Video Script Generator API",
    description="API for generating video scripts from resume templates",
    version="1.0.0",
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
async def generate_script(
    file: UploadFile = File(...),
    template_type: str = Form(...),
):
    start_time = time.time()
    temp_path = None

    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Use parser based on user's template selection
        if template_type.lower() == "ats":
            parser = ATSParser(temp_path)
            template_label = "ATS/HR"
        elif template_type.lower() == "industry":
            parser = IndustryManagerParser(temp_path)
            template_label = "Industry Manager"
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid template type. Must be 'ats' or 'industry'",
            )

        # Parse resume and generate script
        parsed_data = parser.parse()
        script = gpt2_model.generate_script(parsed_data, template_type)

        # Update metrics
        REQUESTS_TOTAL.labels(template_type=template_label).inc()
        PROCESSING_TIME.labels(template_type=template_label).observe(
            time.time() - start_time
        )

        return {"script": script, "template_type": template_label}

    except Exception as e:
        # Update error metrics
        ERROR_COUNT.labels(
            template_type=template_type, error_type=type(e).__name__
        ).inc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    server_config = config["server"]["fastapi"]
    uvicorn.run(
        "app:app",
        host=server_config["host"],
        port=server_config["port"],
        reload=True,
    )
