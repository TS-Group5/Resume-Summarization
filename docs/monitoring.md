# Monitoring Documentation

## Overview

The Resume Video Script Generator includes comprehensive monitoring using Prometheus and Grafana. This setup provides real-time insights into system performance, usage patterns, and error rates.

## Metrics

### Application Metrics

1. **Request Metrics**
   - `resume_video_requests_total`: Total number of script generation requests
   - Labels:
     - `template_type`: "ATS/HR" or "Industry Manager"

2. **Processing Time**
   - `resume_video_processing_seconds`: Histogram of script generation processing times
   - Labels:
     - `template_type`: "ATS/HR" or "Industry Manager"

3. **Error Metrics**
   - `resume_video_errors_total`: Count of errors during script generation
   - Labels:
     - `template_type`: Template type when error occurred
     - `error_type`: Python exception name

## Prometheus

### Configuration

Prometheus is configured to:
- Scrape metrics every 15 seconds
- Retain data for 15 days
- Auto-discover Kubernetes pods
- Store data in a 10GB persistent volume

### Access

```bash
# Port-forward Prometheus UI
kubectl port-forward svc/prometheus-service 9090:9090
```

Access the Prometheus UI at: http://localhost:9090

## Grafana

### Default Dashboard

The system comes with a pre-configured dashboard showing:
1. Request Rate (5-minute window)
2. Average Processing Time
3. Error Count by Type

### Access

```bash
# Get Grafana service URL
kubectl get svc grafana-service

# Default credentials
Username: admin
Password: admin
```

### Dashboard Sections

1. **Request Overview**
   ```promql
   rate(resume_video_requests_total[5m])
   ```
   Shows the rate of requests over time, broken down by template type.

2. **Performance Metrics**
   ```promql
   rate(resume_video_processing_seconds_sum[5m]) / rate(resume_video_processing_seconds_count[5m])
   ```
   Displays average processing time for script generation.

3. **Error Tracking**
   ```promql
   resume_video_errors_total
   ```
   Shows error count broken down by type and template.

## Alerting

### Default Alert Rules

1. High Error Rate
   ```yaml
   - alert: HighErrorRate
     expr: rate(resume_video_errors_total[5m]) > 0.1
     for: 5m
     labels:
       severity: warning
     annotations:
       description: "High error rate detected in script generation"
   ```

2. Slow Processing
   ```yaml
   - alert: SlowProcessing
     expr: rate(resume_video_processing_seconds_sum[5m]) / rate(resume_video_processing_seconds_count[5m]) > 10
     for: 5m
     labels:
       severity: warning
     annotations:
       description: "Script generation is taking longer than expected"
   ```

## Kubernetes Integration

All monitoring components are deployed as Kubernetes resources:
- Prometheus Deployment and Service
- Grafana Deployment and Service
- Persistent Volume Claims for data storage
- ConfigMaps for configuration

## Adding Custom Metrics

To add new metrics to the application:

1. Define the metric in FastAPI:
```python
from prometheus_client import Counter, Histogram

NEW_METRIC = Counter(
    'metric_name_total',
    'Metric description',
    ['label1', 'label2']
)
```

2. Update the Grafana dashboard:
   - Add new panel
   - Use PromQL to query the new metric
   - Configure visualization options
