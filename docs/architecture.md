# Architecture Documentation

## System Architecture

The Resume Summary Generator is built with a microservices architecture pattern, consisting of two main services:

1. **FastAPI Backend Service**
   - Handles resume processing and summary generation
   - Provides RESTful API endpoints
   - Manages model inference and parsing

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

## Data Flow

1. **Resume Upload**:
   - User uploads DOCX file
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

## Deployment

The application is containerized using Docker and can be deployed to various cloud platforms:
- AWS ECS/EKS
- Google Cloud Run
- Azure Container Apps

## Monitoring and Logging

- Structured logging throughout the application
- Health check endpoints
- Error tracking and reporting
