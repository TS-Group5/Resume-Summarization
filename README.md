# Resume Video Script Generator

A powerful tool that generates engaging video scripts from resume templates using GPT-2 and modern web technologies. The system supports multiple industries including IT, Restaurant Management, and Healthcare.

## Features

- **Multi-Industry Support**
  - IT/Software Development: Optimized for technical roles and skills
  - Restaurant Management: Tailored for hospitality and food service
  - Healthcare: Specialized for healthcare professionals

- **Intelligent Script Generation**
  - Industry-specific templates and prompts
  - Dynamic content adaptation based on skills and experience
  - Professional tone and structure

- **Modern Web Interface**
  - Streamlit-based UI for easy interaction
  - Real-time script generation
  - User-friendly file upload

- **Robust Backend**
  - FastAPI for high-performance API
  - GPT-2 model with custom prompt engineering
  - Specialized resume parsers

## Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tv3.git
cd tv3
```

2. Create and activate virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: .\env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the FastAPI backend:
```bash
# Terminal 1
cd /path/to/tv3
./env/bin/python src/api/app.py
```

2. Start the Streamlit frontend:
```bash
# Terminal 2
cd /path/to/tv3
./env/bin/streamlit run src/ui/streamlit_app.py
```

3. Access the application:
- Frontend UI: http://localhost:8501
- API Documentation: http://localhost:8000/docs

### Using the Application

1. Open the Streamlit UI in your browser
2. Upload a resume file (supported format: .docx, .txt)
3. Select the industry type:
   - IT/Software
   - Restaurant Management
   - Healthcare
4. Click "Generate Script" to create the video script
5. View and use the generated script

## Project Structure

```
tv3/
├── src/
│   ├── api/                 # FastAPI backend
│   │   └── app.py          # Main API endpoints
│   ├── models/             # ML models
│   │   └── generic_gpt2_model.py  # GPT-2 implementation
│   ├── parsers/            # Resume parsers
│   │   ├── resume_parser.py
│   │   ├── ats_parser.py
│   │   └── industry_manager_parser.py
│   ├── templates/          # Resume templates
│   └── ui/                 # Streamlit frontend
│       └── streamlit_app.py
├── docs/                   # Documentation
└── requirements.txt        # Python dependencies
```

## Implementation Details

### GPT-2 Model Configuration
- Base model: GPT-2
- Custom prompt engineering for industry-specific content
- Parameters:
  - Max length: 800
  - Min length: 300
  - Temperature: 0.7
  - Top-p: 0.9
  - Top-k: 50
  - Repetition penalty: 1.2

### Script Generation Process
1. Resume parsing and data extraction
2. Industry detection based on role and skills
3. Template selection and prompt construction
4. GPT-2 text generation
5. Post-processing and validation

### Supported Industries
Each industry has specialized templates for:
- Introduction and background
- Professional experience
- Skills and expertise
- Achievements
- Goals and aspirations
- Contact information

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
