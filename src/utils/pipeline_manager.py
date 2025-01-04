"""Pipeline orchestration using ClearML."""
from clearml import PipelineController, Task
from typing import Dict, Any, Optional
import logging
import time
from .report_manager import ReportManager
import pandas as pd

logger = logging.getLogger(__name__)

class ResumePipeline:
    """Pipeline controller for resume processing."""
    
    def __init__(
        self,
        project_name: str = "Resume-Summarization",
        pipeline_name: str = "resume-processing",
        version: str = "1.0",
        queue: str = "default"
    ):
        """Initialize the pipeline controller."""
        self.project_name = project_name
        self.pipeline_name = pipeline_name
        self.version = version
        self.queue = queue
        
        # Initialize the pipeline only if not already running
        self._initialize_pipeline()
        
        # Initialize report manager
        self.report_manager = ReportManager(Task.current_task())
        
        # Set default queue
        self.pipeline.set_default_execution_queue(queue)
        
        # Add pipeline metadata
        self.pipeline.add_parameter("Args/pipeline_name", pipeline_name)
        self.pipeline.add_parameter("Args/version", version)
        self.pipeline.add_parameter("Args/project", project_name)
        self.pipeline.add_parameter("Args/description", "Resume Processing Pipeline")
        
        # Add pipeline input parameters
        self.pipeline.add_parameter("Args/resume_file", "")
        self.pipeline.add_parameter("Args/parser_type", "ats")
        
        # Create base tasks
        self._create_base_tasks()
    
    def _initialize_pipeline(self):
        """Initialize pipeline with optimized settings."""
        self.pipeline = PipelineController(
            name=f"{self.pipeline_name}-v{self.version}",
            project=self.project_name,
            version=self.version,
            abort_on_failure=False  # Don't abort entire pipeline on single step failure
        )
        
        # Set default queue
        self.pipeline.set_default_execution_queue(self.queue)
        
        # Add pipeline metadata
        self.pipeline.add_parameter("Args/pipeline_name", self.pipeline_name)
        self.pipeline.add_parameter("Args/version", self.version)
        self.pipeline.add_parameter("Args/project", self.project_name)
        self.pipeline.add_parameter("Args/description", "Resume Processing Pipeline")
        
        # Add pipeline input parameters
        self.pipeline.add_parameter("Args/resume_file", "")
        self.pipeline.add_parameter("Args/parser_type", "ats")
        
    def _create_task(self, name: str, task_type: str, tags: list) -> Task:
        """Create a base task with common configuration."""
        task = Task.create(
            project_name=self.project_name,
            task_name=name,
            task_type=task_type
        )
        task.add_tags(["pipeline"] + tags)
        task.set_base_docker("python:3.9")
        task.set_user_properties(
            name=name,
            version=self.version,
            pipeline=self.pipeline_name
        )
        task.set_parameter("execution/queue", self.queue)
        task.close()
        return task
    
    def _create_base_tasks(self):
        """Create base tasks for the pipeline."""
        try:
            # Parse Resume Task
            self._create_task(
                name="parse_resume",
                task_type="data_processing",
                tags=["parse"]
            )
            
            # Generate Script Task
            self._create_task(
                name="generate_script",
                task_type="inference",
                tags=["generate"]
            )
            
            # Quality Check Task
            self._create_task(
                name="quality_check",
                task_type="qc",
                tags=["quality"]
            )
            
        except Exception as e:
            logger.error(f"Error creating base tasks: {str(e)}")
            raise
    
    def add_parser_step(
        self,
        parser_type: str = None,
        input_file: str = None,
        requirements: Optional[Dict[str, str]] = None
    ):
        """Add resume parsing step."""
        parser_type = parser_type or "${pipeline.Args/parser_type}"
        input_file = input_file or "${pipeline.Args/resume_file}"
        
        return self.pipeline.add_step(
            name="Step 1: Parse Resume",
            base_task_name="parse_resume",
            base_task_project=self.project_name,
            parameter_override={
                "Args/parser_type": parser_type,
                "Args/input_file": input_file
            },
            execution_queue=self.queue,
            cache_executed_step=True
        )
    
    def add_generation_step(
        self,
        model_config: Dict[str, Any],
        requirements: Optional[Dict[str, str]] = None
    ):
        """Add script generation step."""
        return self.pipeline.add_step(
            name="Step 2: Generate Script",
            base_task_name="generate_script",
            base_task_project=self.project_name,
            parameter_override={
                "Args/model_config": model_config,
                "Args/parsed_data": "${Step 1: Parse Resume.artifacts.parsed_data}"
            },
            parents=["Step 1: Parse Resume"],
            execution_queue=self.queue,
            cache_executed_step=True
        )
    
    def add_quality_check_step(
        self,
        quality_thresholds: Dict[str, float],
        requirements: Optional[Dict[str, str]] = None
    ):
        """Add quality check step."""
        return self.pipeline.add_step(
            name="Step 3: Quality Check",
            base_task_name="quality_check",
            base_task_project=self.project_name,
            parameter_override={
                "Args/thresholds": quality_thresholds,
                "Args/generated_script": "${Step 2: Generate Script.artifacts.generated_script}"
            },
            parents=["Step 2: Generate Script"],
            execution_queue=self.queue,
            cache_executed_step=True
        )
    
    def _parse_resume_step(self, parser_type: str, input_file: str) -> Dict[str, Any]:
        """Execute resume parsing step."""
        try:
            # Parsing logic here
            parsed_data = {"example": "data"}  # Replace with actual parsing
            
            # Log parsing results
            self.report_manager.log_table(
                pd.DataFrame.from_dict(parsed_data, orient='index'),
                "Parsed Resume Data"
            )
            
            # Store output in task
            task = Task.current_task()
            task.upload_artifact("parsed_data", parsed_data)
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error in parse step: {str(e)}")
            raise
    
    def _generate_script_step(self, model_config: Dict[str, Any], parsed_data: Dict[str, Any]) -> str:
        """Execute script generation step."""
        try:
            # Generation logic here
            generated_script = "Example script"  # Replace with actual generation
            
            # Log generated script
            self.report_manager.logger.report_text(
                "Generated Script",
                generated_script
            )
            
            # Store output in task
            task = Task.current_task()
            task.upload_artifact("generated_script", generated_script)
            
            return generated_script
            
        except Exception as e:
            logger.error(f"Error in generation step: {str(e)}")
            raise
    
    def _quality_check_step(self, thresholds: Dict[str, float], generated_script: str) -> Dict[str, float]:
        """Execute quality check step."""
        try:
            # Quality check logic here
            metrics = {
                "coherence": 0.8,
                "relevance": 0.9,
                "overall_score": 0.85
            }  # Replace with actual metrics
            
            # Log quality metrics
            self.report_manager.log_quality_metrics(metrics, thresholds)
            
            # Store output in task
            task = Task.current_task()
            task.upload_artifact("quality_metrics", metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error in quality check step: {str(e)}")
            raise
    
    def start(self, queue: str = None, clean_after_run: bool = True) -> bool:
        """Start the pipeline execution."""
        try:
            # Use instance queue if none provided
            if queue is None:
                queue = self.queue
            
            # Start the pipeline
            self.pipeline.start(queue=queue)
            start_time = time.time()
            
            # Wait for pipeline completion
            while not self.pipeline.wait(timeout=60):
                logger.info("Pipeline still running...")
            
            # Log pipeline summary
            execution_time = time.time() - start_time
            logger.info(f"Pipeline completed in {execution_time:.2f} seconds")
            
            # Create final report
            try:
                parsed_data = self.pipeline.get_step_output("Step 1: Parse Resume", "artifacts.parsed_data")
                generated_script = self.pipeline.get_step_output("Step 2: Generate Script", "artifacts.generated_script")
                quality_metrics = self.pipeline.get_step_output("Step 3: Quality Check", "artifacts.quality_metrics")
                
                self.report_manager.log_pipeline_summary(
                    parsed_data,
                    generated_script,
                    quality_metrics
                )
            except Exception as e:
                logger.error(f"Error creating final report: {str(e)}")
            
            if clean_after_run:
                self.pipeline.stop()
            
            return True
        except Exception as e:
            logger.error(f"Error running pipeline: {str(e)}")
            return False
