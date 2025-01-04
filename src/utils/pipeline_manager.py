"""Pipeline orchestration using ClearML."""
from clearml import PipelineController
from typing import Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

class ResumePipeline:
    """Orchestrate the resume processing pipeline using ClearML."""
    
    def __init__(
        self,
        project_name: str = "Resume-Summarization",
        pipeline_name: str = "resume-processing",
        version: str = "1.0"
    ):
        """Initialize the pipeline controller.
        
        Args:
            project_name: Name of the project
            pipeline_name: Name of the pipeline
            version: Pipeline version
        """
        self.pipeline = PipelineController(
            name=f"{pipeline_name}-v{version}",
            project=project_name,
            version=version
        )
        self.pipeline.set_default_execution_queue("default")
    
    def add_parser_step(
        self,
        parser_type: str,
        input_file: str,
        requirements: Optional[Dict[str, str]] = None
    ):
        """Add resume parsing step to the pipeline.
        
        Args:
            parser_type: Type of parser to use
            input_file: Input resume file
            requirements: Optional package requirements
        """
        self.pipeline.add_step(
            name="parse_resume",
            base_task_project="Resume-Summarization",
            base_task_name="resume_parsing",
            parameter_override={
                "parser_type": parser_type,
                "input_file": input_file
            },
            requirements=requirements or {"pip": "requirements.txt"}
        )
    
    def add_generation_step(
        self,
        model_config: Dict[str, Any],
        requirements: Optional[Dict[str, str]] = None
    ):
        """Add script generation step to the pipeline.
        
        Args:
            model_config: Model configuration parameters
            requirements: Optional package requirements
        """
        self.pipeline.add_step(
            name="generate_script",
            base_task_project="Resume-Summarization",
            base_task_name="script_generation",
            parameter_override={
                "model_config": model_config
            },
            parents=["parse_resume"],
            requirements=requirements or {"pip": "requirements.txt"}
        )
    
    def add_quality_check_step(
        self,
        quality_thresholds: Dict[str, float],
        requirements: Optional[Dict[str, str]] = None
    ):
        """Add quality check step to the pipeline.
        
        Args:
            quality_thresholds: Quality metric thresholds
            requirements: Optional package requirements
        """
        self.pipeline.add_step(
            name="quality_check",
            base_task_project="Resume-Summarization",
            base_task_name="quality_check",
            parameter_override={
                "thresholds": quality_thresholds
            },
            parents=["generate_script"],
            requirements=requirements or {"pip": "requirements.txt"}
        )
    
    def start(
        self,
        queue: str = "default",
        clean_after_run: bool = True
    ) -> bool:
        """Start the pipeline execution.
        
        Args:
            queue: Execution queue name
            clean_after_run: Whether to clean up after execution
            
        Returns:
            True if pipeline completed successfully
        """
        try:
            self.pipeline.start_locally(run_pipeline_steps_locally=True)
            start_time = time.time()
            
            # Wait for pipeline completion
            while not self.pipeline.wait(timeout=60):
                logger.info("Pipeline still running...")
            
            execution_time = time.time() - start_time
            logger.info(f"Pipeline completed in {execution_time:.2f} seconds")
            
            if clean_after_run:
                self.pipeline.stop(mark_failed=False)
            
            return True
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            self.pipeline.stop(mark_failed=True)
            return False
