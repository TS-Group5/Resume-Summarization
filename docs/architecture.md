# Architecture Documentation

## System Architecture

The Resume Summary Generator is built with a containerized microservices architecture, deployed on Kubernetes:

1. **FastAPI Backend Service**
   - Handles resume processing and summary generation
   - Provides RESTful API endpoints
   - Manages model inference and parsing
   - Integrated with ClearML for experiment tracking

2. **Streamlit Frontend Service**
   - Provides user interface for file upload
   - Handles user interactions and display
   - Communicates with FastAPI backend

## Components

### 1. Model Layer
- **Model Factory**: Creates appropriate model instances
- **Base Model**: Abstract class defining model interface
- **Model Implementations**:
  - GPT-2 Model
  - T5 Model
  - BART Model

### 2. Parser Layer
- **Parser Factory**: Creates parser instances
- **Parser Implementations**:
  - ATS Parser: Optimized for ATS format
  - Industry Parser: Specialized for industry formats

### 3. API Layer
- **FastAPI Application**:
  - `/generate-summary/`: Main endpoint for resume processing
  - `/models`: Lists available models
  - `/parsers`: Lists available parsers
  - `/health`: Health check endpoint

### 4. Frontend Layer
- **Streamlit Interface**:
  - File Upload Component
  - Model Selection
  - Parser Selection
  - Summary Display
  - Download Functionality

## Infrastructure

### 1. Kubernetes Deployment
- **Components**:
  - Deployment managing application pods
  - LoadBalancer Service exposing API and UI
  - Horizontal Pod Autoscaler for scaling
  - Secrets for managing credentials

### 2. Auto-scaling
- **HPA Configuration**:
  - Scale based on CPU and Memory utilization
  - 1-3 replicas based on load
  - Configurable scaling policies

### 3. Service Exposure
- **Endpoints**:
  - API: http://localhost:80
  - UI: http://localhost:8502
  - Health Check: http://localhost/health

## Data Flow

1. **Resume Upload**:
   - User uploads DOCX file via UI
   - File validation and temporary storage

2. **Processing**:
   - Parser extracts relevant information
   - Model generates professional summary
   - Results formatted and returned

3. **Response**:
   - Summary displayed to user
   - Option to edit and download

## Security Considerations

1. **File Handling**:
   - Temporary file storage
   - File type validation
   - Secure file cleanup

2. **API Security**:
   - CORS configuration
   - Input validation
   - Error handling

3. **Kubernetes Security**:
   - Secrets for sensitive data
   - Non-root container execution
   - Resource limits and quotas

## Deployment

The application is containerized using Docker and deployed on Kubernetes:
- Docker image: tsgroup0555/resume-summarization
- Kubernetes deployment with auto-scaling
- LoadBalancer service for external access

## Monitoring

1. **Kubernetes Monitoring**:
   - Pod health and status
   - Resource utilization
   - Auto-scaling metrics

2. **Application Monitoring**:
   - Health check endpoints
   - Request metrics
   - Error tracking

3. **ClearML Integration**:
   - Experiment tracking
   - Model performance monitoring
   - Training metrics
