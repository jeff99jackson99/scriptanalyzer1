# Interactive Script Questionnaire

A complete interactive PDF script questionnaire application with building analogy for non-believers and all exceptions from script v4.1.

## Features

- **89 total questions** including all exceptions and variations
- **Building analogy for non-believers** (Q2b) as specified in the script
- **All special handling** from script v4.1 implemented
- **Complete conversation flow** with proper branching logic
- **Streamlit web interface** for easy interaction

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jeff99jackson99/scriptanalyzer1.git
cd scriptanalyzer1
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run script_analyzer_complete.py
```

## Usage

1. Open your browser to `http://localhost:8501`
2. Follow the interactive questionnaire
3. Answer questions as prompted
4. The app will guide you through the complete script flow

## Key Features

- **Non-believer flow** with building analogy
- **Believer flow** for those who believe in God
- **Heaven believer flow** for those who think they'll go to heaven
- **All exception handling** from the original script
- **Complete conversation tracking**

## Files

- `script_analyzer_complete.py` - Main Streamlit application
- `script.pdf` - Original PDF script
- `requirements.txt` - Python dependencies
- `test_every_question.py` - Comprehensive test suite

## Testing

Run the test suite to verify all flows work correctly:
```bash
python3 test_every_question.py
```