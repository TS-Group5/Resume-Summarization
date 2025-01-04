"""Quality monitoring utilities using ClearML."""
from typing import Dict, Any, List, Optional
from clearml import Logger, Task
import numpy as np
from rouge_score import rouge_scorer
import logging
import time

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
            return {}
    
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
                                value=value
                            )
                    else:
                        self.logger.report_scalar(
                            "Summary Metrics",
                            f"{category}_{metric_name}",
                            value=values
                        )
            else:
                self.logger.report_scalar(
                    "Summary Metrics",
                    category,
                    value=metrics
                )
        
        return summary
