# API Documentation

## Overview

The Resume Video Script Generator API is built using FastAPI and provides endpoints for generating video scripts from resumes. The API supports different template types and includes monitoring endpoints.

## Base URL

```
http://localhost:8000
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

### Metrics

```http
GET /metrics
```

Returns Prometheus metrics in plain text format.

#### Response

```
# HELP resume_video_requests_total Total number of resume video script requests
# TYPE resume_video_requests_total counter
resume_video_requests_total{template_type="ats"} 24
resume_video_requests_total{template_type="industry"} 18

# HELP resume_video_processing_seconds Time spent processing resume video script requests
# TYPE resume_video_processing_seconds histogram
...
```

## Using the API

### cURL Examples

1. Generate Script (ATS Template):
```bash
curl -X POST "http://localhost:8000/generate-script" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@resume.docx" \
     -F "template_type=ats"
```

2. Get Metrics:
```bash
curl -X GET "http://localhost:8000/metrics"
```

### Python Example

```python
import requests

def generate_script(file_path, template_type):
    url = "http://localhost:8000/generate-script"
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"template_type": template_type}
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            return response.json()["script"]
        else:
            raise Exception(f"Error: {response.json()['detail']}")

# Usage
script = generate_script("resume.docx", "ats")
print(script)
```

## Rate Limiting

- Default rate limit: 100 requests per minute per IP
- Burst limit: 200 requests

## Error Handling

The API uses standard HTTP status codes:

| Status Code | Description                                   |
|------------|-----------------------------------------------|
| 200        | Successful request                            |
| 400        | Bad request (invalid parameters)              |
| 413        | File too large                                |
| 422        | Validation error                              |
| 429        | Too many requests                             |
| 500        | Internal server error                         |

## Best Practices

1. **File Size**
   - Maximum file size: 10MB
   - Supported format: .docx only

2. **Template Types**
   - Use "ats" for ATS/HR template
   - Use "industry" for Industry Manager template

3. **Error Handling**
   - Always check response status codes
   - Implement proper retry logic
   - Handle rate limiting gracefully

4. **Monitoring**
   - Monitor /metrics endpoint
   - Track error rates and processing times
   - Set up alerts for high error rates
