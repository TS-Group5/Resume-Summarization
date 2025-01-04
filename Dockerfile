# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the project code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p src/templates src/models src/parsers

# Create start script
COPY <<-'EOF' /app/start.sh
#!/bin/bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8080 & \
streamlit run src/ui/streamlit_app.py --server.port 8502 --server.address 0.0.0.0
wait
EOF

# Set permissions before user switch
RUN chmod +x /app/start.sh && \
    useradd -m appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Add src to Python path
ENV PYTHONPATH=/app

# Expose ports for FastAPI and Streamlit
EXPOSE 8080 8502

# Set the entrypoint
ENTRYPOINT ["/app/start.sh"]
