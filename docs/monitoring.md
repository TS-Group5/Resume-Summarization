# Monitoring Documentation

## Overview

The Resume Summarization system uses a comprehensive monitoring setup combining Kubernetes, ClearML, and custom monitoring components.

## Monitoring Components

### 1. Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resume-summarization
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: resume-summarization
          image: tsgroup0555/resume-summarization:latest
          ports:
            - containerPort: 80
            - containerPort: 8502
```

### 2. Auto-scaling (HPA)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: resume-summarization-hpa
spec:
  minReplicas: 1
  maxReplicas: 3
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### 3. ClearML Integration
```python
from clearml import Task

task = Task.init(
    project_name="Resume-Summarization",
    task_name="resume-processing"
)
```

## Monitoring Systems

### 1. ResourceMonitor
Tracks system-level metrics:
- CPU usage
- Memory utilization
- Disk usage
- Network I/O

### 2. QualityMonitor
Tracks generation quality:
- ROUGE scores
- Generation time
- Summary length
- Error rates

### 3. ReportManager
Handles metric visualization:
- Quality reports
- Performance metrics
- Error analysis
- Resource utilization

## Access Points

### 1. Application Endpoints
- API: http://localhost:80
- UI: http://localhost:8502
- Health: http://localhost/health

### 2. Monitoring Dashboards
- ClearML Web Interface: https://app.clear.ml
- Kubernetes Dashboard

## Metrics Tracked

### 1. Performance Metrics
- Request processing time
- Generation throughput
- Success/failure rates
- Error counts

### 2. Quality Metrics
- ROUGE scores (rouge1, rouge2, rougeL)
- Generation time
- Summary length
- Error analysis

### 3. Resource Metrics
- CPU utilization
- Memory usage
- Disk usage
- Network I/O

## Kubernetes Commands

### Deployment Management
```bash
# Check deployment status
kubectl get deployments

# View pods
kubectl get pods

# Check logs
kubectl logs -f <pod-name>
```

### Auto-scaling Management
```bash
# View HPA status
kubectl get hpa

# Check HPA details
kubectl describe hpa resume-summarization-hpa
```

### Service Management
```bash
# Check services
kubectl get services

# Service details
kubectl describe service resume-summarization
```

## Best Practices

### 1. Resource Management
- Monitor resource usage trends
- Adjust HPA thresholds as needed
- Set appropriate resource limits
- Regular resource optimization

### 2. Quality Monitoring
- Track all generations
- Set quality thresholds
- Monitor error patterns
- Regular quality reviews

### 3. Performance Optimization
- Monitor response times
- Track throughput
- Identify bottlenecks
- Optimize critical paths

### 4. Maintenance
- Regular metric review
- Update monitoring rules
- Clean old metrics
- Optimize storage usage
