# Evaluation Documentation

## Overview

The Resume Summarization system uses a comprehensive evaluation framework that combines automated metrics, resource monitoring, and ClearML integration for experiment tracking.

## Evaluation Components

### 1. QualityMonitor

The `QualityMonitor` class handles quality metrics and generation tracking:

```python
class QualityMonitor:
    def __init__(self, task: Optional[Task] = None):
        """Initialize quality monitoring with ClearML."""
        
    def track_generation_quality(
        self,
        generated_text: str,
        reference_text: str,
        generation_time: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """Track quality metrics for a generation."""
        
    def check_quality(self, generated_script: str, reference_text: str) -> bool:
        """Check if generated script meets quality standards."""
```

### 2. ResourceMonitor

The `ResourceMonitor` class tracks system resource usage:

```python
class ResourceMonitor:
    def __init__(self, task: Optional[Task] = None):
        """Initialize resource monitoring."""
        # Tracks:
        # - CPU usage
        # - Memory usage
        # - Disk usage
        # - Network I/O
```

### 3. ReportManager

The `ReportManager` class handles metric reporting and visualization:

```python
class ReportManager:
    def __init__(self, task: Task):
        """Initialize reporting with ClearML task."""
        
    def publish_quality_report(
        self,
        quality_metrics: Dict[str, float],
        thresholds: Dict[str, float]
    ):
        """Publish quality metrics report."""
        
    def publish_performance_report(
        self,
        performance_metrics: Dict[str, Any]
    ):
        """Publish performance metrics report."""
```

## Metrics Tracked

### 1. Quality Metrics
- ROUGE scores (rouge1, rouge2, rougeL)
- Generation time
- Summary length
- Error rates

### 2. Resource Metrics
- CPU utilization
- Memory usage
- Disk usage
- Network I/O

### 3. Performance Metrics
- Request processing time
- Success/failure rates
- Generation throughput
- Error counts

## ClearML Integration

### 1. Experiment Tracking
```python
task = Task.init(
    project_name="Resume-Summarization",
    task_name="resume-processing"
)
```

### 2. Metric Logging
```python
# Log quality metrics
quality_monitor = QualityMonitor(task)
metrics = quality_monitor.track_generation_quality(
    generated_text=generated,
    reference_text=reference,
    generation_time=time_taken
)

# Log resource usage
resource_monitor = ResourceMonitor(task)
resource_monitor.track_resources()

# Generate reports
report_manager = ReportManager(task)
report_manager.publish_quality_report(metrics, thresholds)
```

## Monitoring Dashboard

Access monitoring data through:
1. ClearML Web Interface: https://app.clear.ml
2. Kubernetes Dashboard
3. Application Health Endpoint: http://localhost/health

## Best Practices

1. **Quality Monitoring**
   - Track all generations
   - Set quality thresholds
   - Monitor error rates
   - Regular quality checks

2. **Resource Monitoring**
   - Monitor system resources
   - Track resource trends
   - Set resource limits
   - Alert on high usage

3. **Reporting**
   - Regular metric reports
   - Performance summaries
   - Error analysis
   - Quality trends

4. **Maintenance**
   - Regular metric review
   - Update thresholds
   - Clean old reports
   - Optimize resource usage
