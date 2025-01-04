"""Report generation and publishing utilities for ClearML."""
from clearml import Task, Logger
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ReportManager:
    """Manage report generation and publishing to ClearML."""
    
    def __init__(self, task: Task):
        """Initialize report manager with ClearML task."""
        self.task = task
        self.logger = Logger.current_logger()
    
    def log_metrics(self, metrics: Dict[str, float], title: str = "Metrics"):
        """Log metrics to ClearML."""
        try:
            for name, value in metrics.items():
                self.logger.report_scalar(
                    title=title,
                    series=name,
                    value=value,
                    iteration=0
                )
        except Exception as e:
            logger.error(f"Error logging metrics: {str(e)}")
    
    def log_confusion_matrix(
        self,
        matrix: List[List[float]],
        labels: List[str],
        title: str = "Confusion Matrix"
    ):
        """Log confusion matrix as a heatmap."""
        try:
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                x=labels,
                y=labels,
                colorscale='Viridis'
            ))
            fig.update_layout(title=title)
            self.logger.report_plotly(
                title=title,
                series="confusion_matrix",
                figure=fig
            )
        except Exception as e:
            logger.error(f"Error logging confusion matrix: {str(e)}")
    
    def log_table(
        self,
        data: pd.DataFrame,
        title: str,
        series: str = "table"
    ):
        """Log pandas DataFrame as a table."""
        try:
            self.logger.report_table(
                title=title,
                series=series,
                table_plot=data
            )
        except Exception as e:
            logger.error(f"Error logging table: {str(e)}")
    
    def log_quality_metrics(
        self,
        metrics: Dict[str, float],
        thresholds: Dict[str, float]
    ):
        """Log quality metrics with thresholds."""
        try:
            # Create comparison DataFrame
            df = pd.DataFrame({
                'Metric': list(metrics.keys()),
                'Value': list(metrics.values()),
                'Threshold': [thresholds.get(k, 0.0) for k in metrics.keys()]
            })
            
            # Create bar chart comparing metrics to thresholds
            fig = go.Figure(data=[
                go.Bar(name='Actual', x=df['Metric'], y=df['Value']),
                go.Bar(name='Threshold', x=df['Metric'], y=df['Threshold'])
            ])
            fig.update_layout(
                title='Quality Metrics vs Thresholds',
                barmode='group'
            )
            
            # Log both table and plot
            self.log_table(df, "Quality Metrics")
            self.logger.report_plotly(
                title="Quality Metrics",
                series="metrics_vs_thresholds",
                figure=fig
            )
        except Exception as e:
            logger.error(f"Error logging quality metrics: {str(e)}")
    
    def log_pipeline_summary(
        self,
        parsed_data: Dict[str, Any],
        generated_script: str,
        quality_metrics: Dict[str, float]
    ):
        """Log comprehensive pipeline summary."""
        try:
            # Log parsed resume data
            if isinstance(parsed_data, dict):
                df_parsed = pd.DataFrame.from_dict(parsed_data, orient='index')
                self.log_table(df_parsed, "Parsed Resume Data")
            
            # Log generated script
            self.logger.report_text(
                "Generated Script",
                generated_script
            )
            
            # Log quality metrics
            self.log_metrics(quality_metrics, "Final Quality Metrics")
            
            # Create summary table
            summary = pd.DataFrame({
                'Component': ['Parser', 'Generator', 'Quality Check'],
                'Status': ['Completed'] * 3,
                'Output': [
                    'Resume parsed successfully',
                    'Script generated successfully',
                    f'Quality score: {quality_metrics.get("overall_score", 0.0):.2f}'
                ]
            })
            self.log_table(summary, "Pipeline Summary", "execution_summary")
            
        except Exception as e:
            logger.error(f"Error creating pipeline summary: {str(e)}")
