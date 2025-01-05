"""Quality monitoring utilities using ClearML."""
from typing import Dict, Any, List, Optional
from clearml import Logger, Task
import logging
import time
import pandas as pd
import numpy as np
from rouge_score import rouge_scorer

logger = logging.getLogger(__name__)

class QualityMonitor:
    """Monitor quality metrics for generated scripts."""

    def __init__(self, task: Optional[Task] = None):
        """Initialize the quality monitor."""
        try:
            # Use existing task if provided, otherwise get current task
            self.task = task or Task.current_task()
            if not self.task:
                logger.warning("No ClearML task found. Quality monitoring will be disabled.")
                return

            self.logger = self.task.get_logger()
            self.scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            
            # Initialize metrics
            self.total_generations = 0
            self.total_tokens = 0
            self.generation_times = []
            self.rouge_scores = []
            self.summary_lengths = []
            self.error_counts = 0
            
            # Initialize DataFrames for tracking
            self.metrics_df = pd.DataFrame(columns=[
                'timestamp', 'generation_time', 'summary_length',
                'rouge1', 'rouge2', 'rougeL', 'error'
            ])
            
            # Initialize request tracking metrics
            self.request_count = 0
            self.error_count = 0
            self.start_time = None
            self.iteration = 0
            
            # Initialize latest metrics
            self.latest_metrics = {}
            
            logger.info("Quality monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing quality monitor: {e}")
            raise
    
    def track_generation_quality(
        self,
        generated_text: str,
        reference_text: str,
        generation_time: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """Track quality metrics for a generation.
        
        Args:
            generated_text: Generated script text
            reference_text: Reference text for comparison
            generation_time: Time taken for generation
            metadata: Optional metadata about the generation
            
        Returns:
            Dictionary of quality metrics
        """
        try:
            # Calculate ROUGE scores
            scores = self.scorer.score(reference_text, generated_text)
            rouge_metrics = {
                'rouge1_f1': scores['rouge1'].fmeasure,
                'rouge2_f1': scores['rouge2'].fmeasure,
                'rougeL_f1': scores['rougeL'].fmeasure
            }
            
            # Update metrics
            self.rouge_scores.append(rouge_metrics)
            self.generation_times.append(generation_time)
            self.summary_lengths.append(len(generated_text))
            current_iteration = len(self.rouge_scores)
            
            # Log current metrics
            for metric_name, value in rouge_metrics.items():
                self.logger.report_scalar(
                    "ROUGE Scores",
                    metric_name,
                    value=value,
                    iteration=current_iteration
                )
            
            # Log generation stats
            self.logger.report_scalar(
                "Generation Stats",
                "time_seconds",
                value=generation_time,
                iteration=current_iteration
            )
            
            # Calculate and log moving averages
            if len(self.rouge_scores) >= 10:
                window = 10
                for metric in rouge_metrics.keys():
                    values = [scores[metric] for scores in self.rouge_scores[-window:]]
                    moving_avg = np.mean(values)
                    self.logger.report_scalar(
                        "Moving Averages",
                        f"{metric}_ma{window}",
                        value=moving_avg,
                        iteration=current_iteration
                    )
            
            # Log metadata if provided
            if metadata:
                self.logger.report_table(
                    "Generation Metadata",
                    "latest",
                    table_plot=metadata
                )
            
            # Update DataFrame
            new_row = pd.DataFrame({
                'timestamp': [time.time()],
                'generation_time': [generation_time],
                'summary_length': [len(generated_text)],
                'rouge1': [rouge_metrics['rouge1_f1']],
                'rouge2': [rouge_metrics['rouge2_f1']],
                'rougeL': [rouge_metrics['rougeL_f1']],
                'error': [0]
            })
            self.metrics_df = pd.concat([self.metrics_df, new_row], ignore_index=True)
            
            # Update latest metrics
            self.latest_metrics.update({
                "generation_time": generation_time,
                "rouge1_f1": rouge_metrics['rouge1_f1'],
                "rouge2_f1": rouge_metrics['rouge2_f1'],
                "rougeL_f1": rouge_metrics['rougeL_f1']
            })
            
            return rouge_metrics
            
        except Exception as e:
            logger.error(f"Error tracking quality metrics: {str(e)}")
            self.error_counts += 1
            self.logger.report_scalar(
                "Errors",
                "count",
                value=self.error_counts,
                iteration=len(self.rouge_scores)
            )
            
            # Update DataFrame with error
            new_row = pd.DataFrame({
                'timestamp': [time.time()],
                'generation_time': [0],
                'summary_length': [0],
                'rouge1': [0],
                'rouge2': [0],
                'rougeL': [0],
                'error': [1]
            })
            self.metrics_df = pd.concat([self.metrics_df, new_row], ignore_index=True)
            
            return {}
    
    def track_request(self, template_type: str = None):
        """Track a new request."""
        self.request_count += 1
        self.iteration += 1
        self.start_time = time.time()
        if self.logger:
            self.logger.report_scalar(
                "requests/total",
                "count",
                self.request_count,
                iteration=self.iteration
            )
            if template_type:
                self.logger.report_text(
                    f"Processing request with template: {template_type}",
                    level=logging.INFO
                )
                
    def track_success(self, processing_time: float = None):
        """Track a successful request."""
        if processing_time is None and self.start_time:
            processing_time = time.time() - self.start_time
            
        # Update latest metrics
        self.latest_metrics.update({
            "processing_time": processing_time,
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1)
        })
            
        if self.logger:
            self.logger.report_scalar(
                "requests/processing_time",
                "seconds",
                processing_time,
                iteration=self.iteration
            )
            self.logger.report_scalar(
                "requests/success_rate",
                "rate",
                self.latest_metrics["success_rate"],
                iteration=self.iteration
            )
            
    def track_error(self, error_message: str):
        """Track a request error."""
        self.error_count += 1
        
        # Update latest metrics
        self.latest_metrics.update({
            "error_count": self.error_count,
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1)
        })
        
        if self.logger:
            self.logger.report_scalar(
                "requests/errors",
                "count",
                self.error_count,
                iteration=self.iteration
            )
            self.logger.report_text(
                f"Request Error: {error_message}",
                level=logging.ERROR
            )
            
    def check_quality(self, generated_script: str, thresholds: Dict[str, float]) -> Dict[str, float]:
        """Check quality of generated script."""
        try:
            # Calculate ROUGE scores
            rouge = Rouge()
            scores = rouge.get_scores(generated_script, generated_script)[0]
            
            # Extract metrics
            metrics = {
                'rouge1_f1': scores['rouge-1']['f'],
                'rouge2_f1': scores['rouge-2']['f'],
                'rougeL_f1': scores['rouge-l']['f']
            }
            
            # Log metrics
            if self.task:
                for metric_name, value in metrics.items():
                    self.task.get_logger().report_scalar(
                        "quality_metrics", 
                        metric_name, 
                        value,
                        iteration=self.iteration
                    )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error checking quality: {str(e)}")
            # Return default metrics on error
            return {
                'rouge1_f1': 0.0,
                'rouge2_f1': 0.0,
                'rougeL_f1': 0.0
            }
    
    def log_generation(
        self,
        generated_text: str,
        metrics: Dict[str, float],
        error: Optional[Dict[str, Any]] = None
    ):
        """Log generation metrics and errors.
        
        Args:
            generated_text: The generated script text
            metrics: Dictionary of metrics about the generation
            error: Optional error information if generation failed
        """
        try:
            timestamp = time.time()
            
            # Update counters
            self.total_generations += 1
            if error:
                self.error_count += 1
            
            # Create metrics record
            record = {
                'timestamp': timestamp,
                'generation_time': metrics.get('generation_time', 0),
                'summary_length': metrics.get('summary_length', 0),
                'rouge1': metrics.get('rouge1', 0),
                'rouge2': metrics.get('rouge2', 0),
                'rougeL': metrics.get('rougeL', 0),
                'error': error['type'] if error else None
            }
            
            # Update metrics DataFrame
            self.metrics_df = pd.concat([
                self.metrics_df,
                pd.DataFrame([record])
            ], ignore_index=True)
            
            # Store latest metrics
            self.latest_metrics = metrics
            
            # Log to ClearML
            if not error:
                for name, value in metrics.items():
                    if isinstance(value, (int, float)):
                        self.logger.report_scalar(
                            title="Generation Quality",
                            series=name,
                            value=value,
                            iteration=self.iteration
                        )
                
                # Log sample if text is provided
                if generated_text:
                    self.logger.report_text(
                        "Generation Sample",
                        generated_text[:500]  # First 500 chars
                    )
            else:
                self.logger.report_text(
                    "Generation Error",
                    f"{error['type']}: {error['message']}"
                )
            
            self.iteration += 1
            
        except Exception as e:
            logger.error(f"Error logging generation: {e}")
    
    def log_error(self, error_message: str):
        """Log an error that occurred during processing."""
        try:
            if self.task:
                self.task.get_logger().report_text(error_message, level=logging.ERROR)
                self.error_counts += 1
                self.task.get_logger().report_scalar(
                    title="Errors",
                    series="error_count",
                    value=self.error_counts,
                    iteration=self.task.get_last_iteration() + 1
                )
        except Exception as e:
            logger.error(f"Error logging error: {e}")

    def get_quality_summary(self) -> Dict[str, Any]:
        """Get summary of quality metrics.
        
        Returns:
            Dictionary containing quality metric summaries
        """
        if not self.rouge_scores:
            return {}
            
        rouge_arrays = {
            metric: [scores[metric] for scores in self.rouge_scores]
            for metric in self.rouge_scores[0].keys()
        }
        
        summary = {
            'rouge_metrics': {
                metric: {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values))
                }
                for metric, values in rouge_arrays.items()
            },
            'generation_time': {
                'mean': float(np.mean(self.generation_times)),
                'std': float(np.std(self.generation_times))
            },
            'summary_length': {
                'mean': float(np.mean(self.summary_lengths)),
                'std': float(np.std(self.summary_lengths))
            },
            'error_rate': self.error_counts / len(self.rouge_scores)
        }
        
        # Log summary metrics
        for category, metrics in summary.items():
            if isinstance(metrics, dict):
                for metric_name, values in metrics.items():
                    if isinstance(values, dict):
                        for stat, value in values.items():
                            self.logger.report_scalar(
                                f"{category} Summary",
                                f"{metric_name}_{stat}",
                                value=value,
                                iteration=self.iteration
                            )
                    else:
                        self.logger.report_scalar(
                            "Summary Metrics",
                            f"{category}_{metric_name}",
                            value=values,
                            iteration=self.iteration
                        )
            else:
                self.logger.report_scalar(
                    "Summary Metrics",
                    category,
                    value=metrics,
                    iteration=self.iteration
                )
        
        return summary

    def get_latest_metrics(self) -> Dict[str, float]:
        """Get the most recent generation metrics.
        
        Returns:
            Dictionary of latest metrics
        """
        return self.latest_metrics.copy()
