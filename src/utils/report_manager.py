"""Report generation and publishing utilities for ClearML."""
from clearml import Task, Logger
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional
import logging
import os
import numpy as np

logger = logging.getLogger(__name__)

class ReportManager:
    """Manages reporting and visualization in ClearML."""
    
    def __init__(self, task: Task):
        """Initialize report manager with ClearML task."""
        self.task = task
        self.logger = task.get_logger() if task else None
        self.metrics = {}
        self.reports_path = "reports"
        self.current_iteration = 0
        
        # Create reports directory if it doesn't exist
        os.makedirs(self.reports_path, exist_ok=True)
        
    def log_pipeline_start(self, config: Dict[str, Any]):
        """Log pipeline start with configuration."""
        if not self.logger:
            return
            
        self.logger.report_text(
            "Pipeline Execution Started",
            level=logging.INFO
        )
        
        # Log configuration as a table
        if config:
            df = pd.DataFrame(
                [(k, str(v)) for k, v in config.items()],
                columns=['Parameter', 'Value']
            )
            self.logger.report_table(
                "Pipeline Configuration",
                "configuration",
                table_plot=df
            )
    
    def log_step_metrics(self, step_name: str, metrics: Dict[str, float]):
        """Log step metrics with visualization."""
        if not self.logger:
            return
            
        # Store metrics for trending
        if step_name not in self.metrics:
            self.metrics[step_name] = []
        self.metrics[step_name].append(metrics)
        
        # Log individual metrics
        for metric_name, value in metrics.items():
            self.logger.report_scalar(
                f"{step_name}/metrics",
                metric_name,
                value
            )
        
        # Create and log metrics summary table
        df = pd.DataFrame(
            [(k, v) for k, v in metrics.items()],
            columns=['Metric', 'Value']
        )
        self.logger.report_table(
            f"{step_name} Metrics",
            "metrics_summary",
            table_plot=df
        )
    
    def log_step_completion(self, step_name: str, status: str, output: Any = None):
        """Log step completion with detailed status."""
        if not self.logger:
            return
            
        # Log completion status
        self.logger.report_text(
            f"Step '{step_name}' completed with status: {status}",
            level=logging.INFO
        )
        
        # Log output if available
        if output:
            if isinstance(output, dict):
                df = pd.DataFrame(
                    [(k, str(v)) for k, v in output.items()],
                    columns=['Output', 'Value']
                )
                self.logger.report_table(
                    f"{step_name} Output",
                    "step_output",
                    table_plot=df
                )
            else:
                self.logger.report_text(
                    f"{step_name} Output: {str(output)}",
                    level=logging.INFO
                )
    
    def log_pipeline_completion(self, status: str, summary: Dict[str, Any] = None):
        """Log pipeline completion with summary."""
        if not self.logger:
            return
            
        # Log completion status
        self.logger.report_text(
            f"Pipeline completed with status: {status}",
            level=logging.INFO
        )
        
        # Log summary if available
        if summary:
            df = pd.DataFrame(
                [(k, str(v)) for k, v in summary.items()],
                columns=['Metric', 'Value']
            )
            self.logger.report_table(
                "Pipeline Execution Summary",
                "execution_summary",
                table_plot=df
            )
        
        # Log overall metrics trend if available
        for step_name, step_metrics in self.metrics.items():
            if step_metrics:
                df = pd.DataFrame(step_metrics)
                for column in df.columns:
                    self.logger.report_line_plot(
                        title=f"{step_name} Metrics Trend",
                        series=column,
                        xaxis="Iteration",
                        yaxis="Value",
                        mode='lines+markers',
                        iteration=list(range(len(step_metrics))),
                        values=df[column].tolist()
                    )
    
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

    def generate_html_report(self, title: str, content: Dict[str, Any]) -> str:
        """Generate an HTML report from content."""
        html_content = f"<h1>{title}</h1>\n"
        
        for section, data in content.items():
            html_content += f"<h2>{section}</h2>\n"
            
            if isinstance(data, dict):
                html_content += "<table border='1'>\n"
                html_content += "<tr><th>Metric</th><th>Value</th></tr>\n"
                for key, value in data.items():
                    html_content += f"<tr><td>{key}</td><td>{value}</td></tr>\n"
                html_content += "</table>\n"
            elif isinstance(data, pd.DataFrame):
                html_content += data.to_html()
            else:
                html_content += f"<p>{str(data)}</p>\n"
                
        return html_content
        
    def publish_report(self, title: str, content: Dict[str, Any], report_type: str = "general"):
        """Publish a report to ClearML."""
        if not self.logger:
            return
            
        try:
            # Generate HTML report
            html_content = self.generate_html_report(title, content)
            report_path = os.path.join(self.reports_path, f"{report_type}_report.html")
            
            # Save HTML report locally
            with open(report_path, "w") as f:
                f.write(html_content)
            
            # Upload report to ClearML
            self.task.upload_artifact(
                name=f"{report_type}_report",
                artifact_object=report_path,
                metadata={'type': 'html_report'}
            )
            
            # Log report preview
            self.logger.report_text(
                f"Generated {report_type} report: {title}",
                level=logging.INFO
            )
            
        except Exception as e:
            logger.error(f"Error publishing report: {e}")
            
    def publish_quality_report(self, quality_metrics: Dict[str, float], thresholds: Dict[str, float]):
        """Publish quality metrics report."""
        if not self.logger:
            return
            
        try:
            # Create quality metrics DataFrame
            metrics_df = pd.DataFrame([
                {"Metric": k, "Value": v, "Threshold": thresholds.get(k, "N/A")}
                for k, v in quality_metrics.items()
            ])
            
            # Generate plots
            for metric, value in quality_metrics.items():
                if metric in thresholds:
                    self.logger.report_scalar(
                        "Quality Metrics",
                        metric,
                        value,
                        iteration=self.current_iteration
                    )
            
            content = {
                "Summary": {
                    "Total Metrics": len(quality_metrics),
                    "Metrics Meeting Threshold": sum(
                        1 for k, v in quality_metrics.items()
                        if k in thresholds and v >= thresholds[k]
                    )
                },
                "Detailed Metrics": metrics_df
            }
            
            self.publish_report("Quality Metrics Report", content, "quality")
            
        except Exception as e:
            logger.error(f"Error publishing quality report: {e}")
            
    def publish_performance_report(self, performance_metrics: Dict[str, Any]):
        """Publish performance metrics report."""
        if not self.logger:
            return
            
        try:
            # Create performance DataFrame
            perf_df = pd.DataFrame([
                {"Metric": k, "Value": v}
                for k, v in performance_metrics.items()
            ])
            
            # Log performance metrics
            for metric, value in performance_metrics.items():
                if isinstance(value, (int, float)):
                    self.logger.report_scalar(
                        "Performance Metrics",
                        metric,
                        value,
                        iteration=self.current_iteration
                    )
            
            content = {
                "Performance Summary": performance_metrics,
                "Detailed Metrics": perf_df
            }
            
            self.publish_report("Performance Metrics Report", content, "performance")
            
        except Exception as e:
            logger.error(f"Error publishing performance report: {e}")
            
    def publish_error_report(self, errors: List[Dict[str, Any]]):
        """Publish error report."""
        if not self.logger:
            return
            
        try:
            # Create error DataFrame
            error_df = pd.DataFrame(errors)
            
            # Calculate error statistics
            error_stats = {
                "Total Errors": len(errors),
                "Error Types": len(set(e.get('type', 'unknown') for e in errors)),
                "Most Common Error": max(
                    set(e.get('type', 'unknown') for e in errors),
                    key=lambda x: sum(1 for e in errors if e.get('type') == x),
                    default="None"
                )
            }
            
            content = {
                "Error Statistics": error_stats,
                "Detailed Errors": error_df
            }
            
            self.publish_report("Error Report", content, "error")
            
        except Exception as e:
            logger.error(f"Error publishing error report: {e}")
            
    def publish_summary_report(self):
        """Publish summary report combining all metrics."""
        if not self.logger:
            return
            
        try:
            # Gather all metrics
            all_metrics = {
                metric_type: metrics
                for metric_type, metrics in self.metrics.items()
            }
            
            # Create summary statistics
            summary_stats = {
                "Total Requests": sum(
                    len(metrics) for metrics in all_metrics.values()
                ),
                "Average Processing Time": np.mean([
                    m.get('processing_time', 0)
                    for metrics in all_metrics.values()
                    for m in metrics
                    if isinstance(m, dict)
                ]),
                "Success Rate": np.mean([
                    m.get('success', 0)
                    for metrics in all_metrics.values()
                    for m in metrics
                    if isinstance(m, dict)
                ])
            }
            
            content = {
                "Summary Statistics": summary_stats,
                "Detailed Metrics": all_metrics
            }
            
            self.publish_report("Summary Report", content, "summary")
            
        except Exception as e:
            logger.error(f"Error publishing summary report: {e}")
