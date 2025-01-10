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
          # Image from Docker Hub, configured via DOCKER_USER secret
          image: ${DOCKER_USER}/resume-summarization:latest
          ports:
            - containerPort: 8080  # API port
              name: api
            - containerPort: 8502  # UI port
              name: ui
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          env:
            # ClearML credentials from secrets
            - name: CLEARML_API_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: clearml-credentials
                  key: access_key
            - name: CLEARML_API_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: clearml-credentials
                  key: secret_key
            # ClearML host configurations from secrets
            - name: CLEARML_API_HOST
              valueFrom:
                secretKeyRef:
                  name: clearml-config
                  key: api_host
            - name: CLEARML_WEB_HOST
              valueFrom:
                secretKeyRef:
                  name: clearml-config
                  key: web_host
            - name: CLEARML_FILES_HOST
              valueFrom:
                secretKeyRef:
                  name: clearml-config
                  key: files_host
```

### 2. Service Configuration
```yaml
apiVersion: v1
kind: Service
metadata:
  name: resume-summarization
spec:
  type: LoadBalancer
  ports:
    - name: api
      port: 80
      targetPort: 8080
    - name: ui
      port: 8502
      targetPort: 8502
```

### 3. Auto-scaling (HPA)
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

### 4. ClearML Integration
```python
from clearml import Task
import os

# Initialize ClearML task
task = Task.init(
    project_name="Resume-Summarization",
    task_name="resume-processing"
)

# ClearML configuration from environment variables
clearml_config = {
    "api_server": os.getenv("CLEARML_API_HOST"),
    "web_server": os.getenv("CLEARML_WEB_HOST"),
    "files_server": os.getenv("CLEARML_FILES_HOST"),
    "credentials": {
        "access_key": os.getenv("CLEARML_API_ACCESS_KEY"),
        "secret_key": os.getenv("CLEARML_API_SECRET_KEY")
    }
}
```

## Monitoring Systems

### 1. ResourceMonitor
Tracks system-level metrics:
- CPU usage (target: 80%)
- Memory utilization (target: 80%)
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
- API: http://localhost:80 (forwards to 8080)
- UI: http://localhost:8502
- Health: http://localhost/health (forwards to 8080/health)

### 2. Monitoring Dashboards
- ClearML Web Interface: ${CLEARML_WEB_HOST}
- Kubernetes Dashboard

## Required Secrets

### 1. Docker Configuration
- `DOCKER_USER`: Docker Hub username for image pulling

### 2. ClearML Credentials
- `CLEARML_API_ACCESS_KEY`: ClearML API access key
- `CLEARML_API_SECRET_KEY`: ClearML API secret key

### 3. ClearML Host Configuration
- `CLEARML_API_HOST`: ClearML API server URL
- `CLEARML_WEB_HOST`: ClearML web interface URL
- `CLEARML_FILES_HOST`: ClearML file server URL

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
- Set appropriate resource limits (CPU: 500m-1000m, Memory: 1Gi-2Gi)
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

### 5. Security
- Rotate secrets regularly
- Use Kubernetes secrets for sensitive data
- Monitor access patterns
- Regular security audits
