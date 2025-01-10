# API Documentation

## Overview

The Resume Video Script Generator API is built using FastAPI and provides endpoints for generating video scripts from resumes. The API is deployed on Kubernetes with auto-scaling capabilities.

## Base URLs

When deployed on Kubernetes:
```
http://localhost:80 (API)
http://localhost:8502 (UI)
```

## Endpoints

### Generate Video Script

```http
POST /generate-script
```

Generates a video script from an uploaded resume.

#### Request

**Content-Type:** `multipart/form-data`

| Parameter     | Type   | Required | Description                           |
|--------------|--------|----------|---------------------------------------|
| file         | File   | Yes      | Resume file in .docx format          |
| template_type| String | Yes      | Template type ("ats" or "industry")  |

#### Response

```json
{
    "script": "Generated video script content",
    "template_type": "ATS/HR or Industry Manager"
}
```

#### Error Responses

```json
{
    "detail": "Error message"
}
```

Common error codes:
- `400`: Invalid template type or file format
- `500`: Internal server error

### Health Check

```http
GET /health
```

Returns the health status of the API.

#### Response

```json
{
    "status": "healthy",
    "timestamp": "2025-01-10T09:18:58+05:30"
}
```

## Using the API

### cURL Examples

1. Generate Script (ATS Template):
```bash
curl -X POST "http://localhost/generate-script" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@resume.docx" \
     -F "template_type=ats"
```

2. Check Health:
```bash
curl -X GET "http://localhost/health"
```

### Python Example

```python
import requests

def generate_script(file_path, template_type):
    url = "http://localhost/generate-script"
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"template_type": template_type}
        response = requests.post(url, files=files, data=data)
    
    return response.json()

# Example usage
result = generate_script("resume.docx", "ats")
print(result["script"])
```

## Deployment Notes

The API is deployed on Kubernetes with:
- Auto-scaling based on CPU and Memory utilization
- LoadBalancer service for external access
- Health checks for monitoring
- ClearML integration for experiment tracking

For Kubernetes-specific commands, refer to the monitoring documentation.
