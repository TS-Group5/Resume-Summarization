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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only the necessary files for package installation
COPY setup.py README.md ./
COPY requirements*.txt ./
COPY config.yaml ./

# Create src directory and copy source files
RUN mkdir -p src
COPY src/api src/api/
COPY src/models src/models/
COPY src/parsers src/parsers/
COPY src/templates src/templates/
COPY src/ui src/ui/
COPY src/utils src/utils/

# Install requirements and the package
RUN pip install -r requirements.txt \
    && pip install -r requirements-dev.txt \
    && pip install -e .

# Create start script with proper signal handling
COPY <<-'EOF' /app/start.sh
#!/bin/bash
trap 'kill $(jobs -p)' SIGTERM SIGINT

# Create ClearML config if credentials are provided
if [ ! -z "$CLEARML_API_ACCESS_KEY" ] && [ ! -z "$CLEARML_API_SECRET_KEY" ]; then
    cat > /app/.clearml.conf << EOL
api {
    api_server: "https://api.clear.ml"
    web_server: "https://app.clear.ml/"
    files_server: "https://files.clear.ml"
    credentials {
        "access_key": "$CLEARML_API_ACCESS_KEY"
        "secret_key": "$CLEARML_API_SECRET_KEY"
    }
}
EOL
fi

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

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the start script
CMD ["/app/start.sh"]
