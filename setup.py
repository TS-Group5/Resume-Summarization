from setuptools import setup, find_packages

setup(
    name="professional-summary-generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "transformers",
        "torch",
        "streamlit>=1.24.0",
        "python-docx>=0.8.11",
    ],
)
