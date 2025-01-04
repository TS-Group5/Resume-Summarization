from setuptools import setup, find_packages

setup(
    name="resume-summarization",
    version="0.1.0",
    package_dir={"": "src"},  # Tell setuptools packages are under src
    packages=find_packages(where="src"),  # List all packages under src
    install_requires=[
        "transformers",
        "torch",
        "streamlit>=1.24.0",
        "python-docx>=0.8.11",
        "rouge_score",
        "pyyaml",
        "pipeline",
        "fastapi",  # For API endpoints
        "uvicorn",  # For running the FastAPI server
        "prometheus_client",  # For Prometheus metrics
        "python-multipart",  # For handling form data in FastAPI
        "clearml>=1.11.0",  # For ClearML
        "psutil>=5.9.0",  # For system resource monitoring
        "numpy>=1.21.0",  # For numerical operations
        "pandas>=1.3.0",  # For data manipulation
        "matplotlib>=3.4.0",  # For data visualization
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",  # For coverage reporting
            "pytest-asyncio>=0.21.0",  # For testing async functions
            "httpx>=0.24.0",  # For testing FastAPI
            "black>=23.0.0",  # For code formatting
            "isort>=5.12.0",  # For import sorting
            "flake8>=6.0.0",  # For linting
        ],
    },
    python_requires=">=3.8",

    # Add entry points for command line scripts
    entry_points={
        "console_scripts": [
            "generate-summary=generate_summary:main",
        ],
    },
)
