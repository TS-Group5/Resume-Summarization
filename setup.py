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
    ],
    
    python_requires=">=3.8",

    # Add entry points for command line scripts
    entry_points={
        "console_scripts": [
            "generate-summary=generate_summary:main",
        ],
    },
)
