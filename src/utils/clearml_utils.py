"""ClearML utilities for tracking experiments and monitoring."""
from typing import Any, Dict, Optional, List
from clearml import Task, Logger, OutputModel, Dataset
import os
import json
import matplotlib.pyplot as plt
import pandas as pd
import yaml

def init_clearml_task(
    project_name: str = "Resume-Summarization",
    task_name: str = "default",
    task_type: str = Task.TaskTypes.inference,
    tags: Optional[List[str]] = None
) -> Task:
    """Initialize a ClearML task."""
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    clearml_config = config.get('clearml', {})
    
    # Close any existing task
    try:
        current_task = Task.current_task()
        if current_task:
            current_task.close()
    except Exception:
        pass
        
    # Use config values with fallbacks to parameters
    project_name = clearml_config.get('project_name', project_name)
    task_type = clearml_config.get('task_type', task_type)
    queue = clearml_config.get('queue', 'default')
    worker_config = clearml_config.get('worker', {})
    
    # Combine provided tags with worker tags
    all_tags = set(tags or [])
    all_tags.update(worker_config.get('tags', []))
    
    # Initialize new task
    task = Task.init(
        project_name=project_name,
        task_name=task_name,
        task_type=task_type,
        tags=list(all_tags),
        auto_connect_frameworks={'pytorch': False}
    )
    
    # Set worker information and queue as task parameters
    if worker_config:
        task.set_parameters(
            {
                "worker": {
                    "name": worker_config.get('name', 'default-worker'),
                    "queue": queue
                },
                "execution": {
                    "queue": queue
                }
            }
        )
    
    return task

def get_logger() -> Logger:
    """Get the ClearML logger for the current task."""
    return Logger.current_logger()

def log_model_parameters(params: Dict[str, Any]) -> None:
    """Log model parameters to ClearML."""
    task = Task.current_task()
    if task:
        task.connect(params)

def log_metric(
    title: str,
    series: str,
    value: float,
    iteration: Optional[int] = None
) -> None:
    """Log a metric to ClearML."""
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
    """Log text to ClearML."""
    logger = get_logger()
    if logger:
        logger.report_text(value, title=title, series=series, iteration=iteration)

def log_confusion_matrix(
    matrix: List[List[int]],
    labels: List[str],
    title: str = "Confusion Matrix",
    iteration: Optional[int] = None
) -> None:
    """Log a confusion matrix visualization.
    
    Args:
        matrix: Confusion matrix data
        labels: Class labels
        title: Title for the plot
        iteration: Optional iteration number
    """
    logger = get_logger()
    if logger:
        plt.figure(figsize=(10, 8))
        plt.imshow(matrix, interpolation='nearest')
        plt.title(title)
        plt.colorbar()
        tick_marks = range(len(labels))
        plt.xticks(tick_marks, labels, rotation=45)
        plt.yticks(tick_marks, labels)
        plt.tight_layout()
        logger.report_matplotlib_figure(title, "", plt.gcf(), iteration=iteration)
        plt.close()

def save_model_checkpoint(model_path: str, framework_type: str = "pytorch") -> None:
    """Save a model checkpoint with ClearML.
    
    Args:
        model_path: Path to the model checkpoint
        framework_type: Type of the model framework
    """
    task = Task.current_task()
    if task:
        output_model = OutputModel(task=task, framework=framework_type)
        output_model.update_weights(weights_filename=model_path)

def create_dataset(
    dataset_name: str,
    dataset_project: str,
    dataset_path: str,
    dataset_tags: Optional[List[str]] = None,
    parent_datasets: Optional[List[str]] = None
) -> Dataset:
    """Create and upload a dataset to ClearML.
    
    Args:
        dataset_name: Name of the dataset
        dataset_project: Project name for the dataset
        dataset_path: Local path to the dataset
        dataset_tags: Optional tags for the dataset
        parent_datasets: Optional list of parent dataset IDs
    
    Returns:
        ClearML Dataset object
    """
    dataset = Dataset.create(
        dataset_name=dataset_name,
        dataset_project=dataset_project,
        parent_datasets=parent_datasets,
        dataset_tags=dataset_tags
    )
    dataset.add_files(dataset_path)
    dataset.upload()
    dataset.finalize()
    return dataset

def log_histogram(
    title: str,
    series: str,
    values: List[float],
    iteration: Optional[int] = None,
    bins: int = 30
) -> None:
    """Log a histogram of values.
    
    Args:
        title: Title of the plot
        series: Name of the series
        values: List of values to plot
        iteration: Optional iteration number
        bins: Number of histogram bins
    """
    logger = get_logger()
    if logger:
        logger.report_histogram(
            title=title,
            series=series,
            values=values,
            iteration=iteration,
            bins=bins
        )

def log_table(
    title: str,
    series: str,
    table_plot: pd.DataFrame,
    iteration: Optional[int] = None
) -> None:
    """Log a table visualization.
    
    Args:
        title: Title of the table
        series: Name of the series
        table_plot: Pandas DataFrame to visualize
        iteration: Optional iteration number
    """
    logger = get_logger()
    if logger:
        logger.report_table(
            title=title,
            series=series,
            table_plot=table_plot,
            iteration=iteration
        )
