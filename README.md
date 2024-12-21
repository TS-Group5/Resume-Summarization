# Resume Summary Generator

A modern AI-powered application that generates professional summaries from resumes using various AI models.

## Features

- 📄 Multiple resume template options
- 🤖 Support for different AI models (T5, GPT-2, BART)
- 🎨 Modern dark-themed UI
- 📊 Detailed resume parsing and analysis
- 💡 Professional summary generation
- ⚡ Real-time processing

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tv3
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run src/app.py
```

2. Access the application in your web browser (typically http://localhost:8501)

3. Follow the steps in the application:
   - Choose a resume template
   - Download and fill out the template
   - Upload your completed resume
   - Select an AI model
   - Generate your professional summary

## Available Models

- **T5**: Fast and efficient, good for concise summaries
- **GPT-2**: More detailed and natural language generation
- **BART**: Balanced approach with good comprehension

## Project Structure

```
tv3/
├── src/
│   ├── app.py              # Main Streamlit application
│   ├── generate_summary.py # Summary generation logic
│   └── templates/          # Resume templates
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
```

## Troubleshooting

- If you encounter any model loading issues, ensure you have sufficient disk space and RAM
- For template download issues, verify your internet connection
- If the UI appears broken, try clearing your browser cache

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
