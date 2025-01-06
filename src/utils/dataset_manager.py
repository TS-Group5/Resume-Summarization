"""Dataset management utilities using ClearML."""
import os
from typing import Optional, List
from .clearml_utils import create_dataset
import logging
from utils.clearml_utils import log_metric, log_text
logger = logging.getLogger(__name__)

class DatasetManager:
    """Manage resume templates and datasets using ClearML."""
    
    def __init__(
        self,
        project_name: str = "Resume-Summarization",
        dataset_name: str = "resume-templates"
    ):
        """Initialize dataset manager.
        
        Args:
            project_name: Name of the project
            dataset_name: Base name for the dataset
        """
        self.project_name = project_name
        self.dataset_name = dataset_name
    
    def version_templates(
        self,
        template_dir: str,
        version: str,
        tags: Optional[List[str]] = None
    ) -> str:
        """Version control the resume templates.
        
        Args:
            template_dir: Directory containing templates
            version: Version string for this template set
            tags: Optional tags for the dataset
        
        Returns:
            Dataset ID
        """
        dataset_name = f"{self.dataset_name}-v{version}"
        try:
            dataset = create_dataset(
                dataset_name=dataset_name,
                dataset_project=self.project_name,
                dataset_path=template_dir,
                dataset_tags=tags or []
            )
            logger.info(f"Created dataset version {version} with ID: {dataset.id}")
            return dataset.id
        except Exception as e:
            logger.error(f"Error versioning templates: {str(e)}")
            raise
    
    def track_template_usage(
        self,
        template_type: str,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Track template usage statistics.
        
        Args:
            template_type: Type of template used
            success: Whether the template was used successfully
            error: Optional error message if failed
        """

        
        # Track usage count
        metric_title = "Template Usage"
        log_metric(
            title=metric_title,
            series=f"{template_type}_total",
            value=1,
            iteration=None
        )
        log_metric(
            title=metric_title,
            series=f"{template_type}_success" if success else f"{template_type}_failure",
            value=1,
            iteration=None
        )
        
        # Log errors if any
        if error:
            log_text(
                title="Template Errors",
                series=template_type,
                value=error
            )
