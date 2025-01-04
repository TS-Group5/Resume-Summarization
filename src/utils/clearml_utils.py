"""ClearML utilities for tracking experiments and monitoring."""
from typing import Any, Dict, Optional
from clearml import Task, Logger
import os

def init_clearml_task(
    project_name: str = "Resume-Summarization",
    task_name: str = "default",
    task_type: str = Task.TaskTypes.inference,
) -> Task:
    """Initialize a ClearML task.
    
    Args:
        project_name: Name of the project
        task_name: Name of the task
        task_type: Type of task (inference, training, etc.)
    
    Returns:
        ClearML Task object
    """
    task = Task.init(
        project_name=project_name,
        task_name=task_name,
        task_type=task_type,
        auto_connect_frameworks={'pytorch': False}  # Disable automatic framework connecting
    )
    return task

def get_logger() -> Logger:
    """Get the ClearML logger for the current task.
    
    Returns:
        ClearML Logger object
    """
    return Logger.current_logger()

def log_model_parameters(params: Dict[str, Any]) -> None:
    """Log model parameters to ClearML.
    
    Args:
        params: Dictionary of parameters to log
    """
    task = Task.current_task()
    if task:
        task.connect(params)

def log_metric(
    title: str,
    series: str,
    value: float,
    iteration: Optional[int] = None
) -> None:
    """Log a metric to ClearML.
    
    Args:
        title: Title of the plot
        series: Name of the series
        value: Value to log
        iteration: Optional iteration number
    """
    logger = get_logger()
    if logger:
        logger.report_scalar(
            title=title,
            series=series,
            value=value,
            iteration=iteration
        )

def log_text(
    title: str,
    series: str,
    value: str,
    iteration: Optional[int] = None
) -> None:
    """Log text to ClearML.
    
    Args:
        title: Title of the plot
        series: Name of the series
        value: Text to log
        iteration: Optional iteration number
    """
    logger = get_logger()
    if logger:
        logger.report_text(value, title=title, series=series, iteration=iteration)
