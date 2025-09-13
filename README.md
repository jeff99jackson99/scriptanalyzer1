# 📋 Script Analyzer

An interactive PDF script questionnaire application built with Streamlit that intelligently parses PDF scripts and creates dynamic question flows based on user responses.

## 🌟 Features

- **Smart PDF Parsing**: Automatically extracts questions and flow logic from PDF scripts
- **Interactive Flow**: Navigate through questions based on your answers
- **Suggested Answers**: Click on pre-defined answers for quick navigation
- **Manual Input**: Type custom answers when needed
- **Robust Navigation**: Handles various script formats and question numbering
- **Debug Mode**: View parsed content and troubleshoot issues
- **Fallback System**: Works even if complex parsing fails

## 🚀 Quick Start

### Option 1: Easy Setup (Recommended)
```bash
python setup.py
```

### Option 2: Manual Setup
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Place your PDF script as `script.pdf` in this directory**

3. **Run the app:**
   ```bash
   streamlit run script_analyzer.py
   ```

## 📖 How to Use

1. **Load Script**: Click "🔄 Load Script" in the sidebar
2. **Read Question**: Review the current question displayed
3. **Choose Answer**: 
   - Click on suggested answers for quick selection
   - Or type your own answer in the text box
4. **Auto-Navigation**: The app automatically moves to the next question based on your answer

## 🔧 How It Works

The application intelligently parses PDF files looking for:

### Question Patterns
- **Numbered Questions**: `1. What is your name?`
- **Alternative Formats**: `Question 1. Text` or `1 Text`

### Flow Indicators
- **Parentheses**: `Yes (go to 5)` or `No (2)`
- **Arrows**: `Continue -> 3` or `Maybe → 4`

### Answer Options
- **Bullet Points**: `• Option A` or `- Option B`
- **Lettered Choices**: `a) Choice` or `A. Choice`
- **Simple Lists**: Plain text answers

### Fallback Logic
If complex parsing fails, the app creates a basic structure that still allows interaction with the script content.

## 📁 File Structure

```
Script1/
├── script.pdf              # Your PDF script (required)
├── script_analyzer.py       # Main application
├── requirements.txt         # Dependencies
├── setup.py                # Setup and run script
└── README.md               # This file
```

## 🎯 Supported Script Formats

The parser handles various formats:

### Question Formats
- `1. Question text`
- `Question 1. Text`
- `1 Question text`

### Answer Flow Formats
- `Answer (5)` - Go to question 5
- `Answer (go to 5)` - Go to question 5
- `Answer -> 5` - Go to question 5
- `Answer → 5` - Go to question 5

### Answer Option Formats
- `• Option A` - Bullet points
- `- Option B` - Dashes
- `a) Choice` - Lettered choices
- `A. Choice` - Lettered with periods

## 🛠️ Troubleshooting

### Common Issues

**PDF not loading**
- Ensure `script.pdf` is in the same directory as the script
- Check that the PDF is not password-protected
- Verify the PDF contains extractable text (not just images)

**Questions not parsed correctly**
- Enable debug mode to see raw PDF content
- Check if your script follows supported formats
- Try the fallback mode if available

**Navigation issues**
- Use suggested answers when possible
- Try typing similar text to the suggestions
- Check debug info to see available question flow

**Missing dependencies**
- Run `pip install -r requirements.txt`
- Ensure you have Python 3.7+ installed

### Debug Mode

Enable debug mode by expanding the "🔍 Debug Information" section at the bottom of the app. This shows:
- Current question ID
- Total number of questions found
- Available question IDs
- Current question data
- Raw PDF content (if requested)

## 🚀 GitHub Repository

This code is designed to be uploaded to: https://github.com/jeff99jackson99/scriptanalyzer

## 🔮 Future Enhancements

- Support for more PDF formats and languages
- Export conversation history
- Custom question numbering schemes
- Multi-language support
- Voice input/output capabilities
- Advanced script templates

## 📝 Example Usage

1. **Prepare your script**: Create a PDF with numbered questions and answer flows
2. **Load the app**: Run `streamlit run script_analyzer.py`
3. **Load script**: Click "Load Script" in the sidebar
4. **Navigate**: Answer questions using suggestions or manual input
5. **Debug if needed**: Use debug mode to troubleshoot parsing issues

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.
