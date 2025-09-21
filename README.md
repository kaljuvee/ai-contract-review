# AI Contract Risk Review Application - Enhanced with LLM Analysis

A powerful Streamlit-based application that uses advanced LLM analysis to analyze contracts, identify risks, and suggest improvements. Built with OpenAI GPT models and Exa.ai search for comprehensive contract review.

## 🚀 Enhanced Features

### Advanced Document Processing
- **Multi-Library PDF Extraction**: PyMuPDF, pdfplumber, PyPDF2 with automatic fallback
- **Robust DOCX Processing**: python-docx and docx2txt with error handling
- **Smart Text Cleaning**: Automatic formatting cleanup and OCR error correction
- **Markdown Conversion**: Convert contracts to structured markdown format

### LLM-Powered Analysis (No Regex!)
- **Intelligent Contract Type Detection**: Uses GPT models instead of pattern matching
- **Smart Governing Law Identification**: LLM-based jurisdiction detection
- **Advanced Clause Extraction**: AI identifies and categorizes key contract clauses
- **Risk Assessment**: Individual clause risk analysis with detailed recommendations

## Features

- **Multi-format Support**: Upload PDF, DOCX, or TXT contract files
- **LLM-Based Analysis**: Uses OpenAI GPT models for intelligent contract understanding
- **Comprehensive Clause Detection**: Identifies termination, liability, confidentiality, and more
- **Individual Clause Risk Assessment**: Detailed risk analysis for each clause type
- **Regulatory Research**: Integrates Exa.ai for up-to-date legal information
- **Visual Highlighting**: Color-coded risk highlighting in original text
- **Detailed Suggestions**: AI-powered improvement recommendations
- **Multiple Export Options**: Download as JSON or Markdown

## Supported Contract Types

The LLM can intelligently detect and analyze:
- Non-Disclosure Agreements (NDA)
- Master Service Agreements (MSA)
- Data Processing Agreements (DPA)
- Service Level Agreements (SLA)
- Employment Contracts
- License Agreements
- Purchase Agreements
- Lease Agreements
- General Commercial Contracts

## Installation

1. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   Copy `.env.example` to `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   EXA_API_KEY=your_exa_api_key_here
   ```

## Usage

1. **Start the application**:
   ```bash
   streamlit run Home.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Upload a contract** using the file uploader

4. **Review the LLM analysis**:
   - Contract type and governing law detection
   - Key clauses extraction with summaries
   - Individual clause risk assessments
   - Color-coded risk highlighting

5. **Download results** as JSON or Markdown

## Project Structure

```
contract_review/
├── Home.py                    # Main Streamlit application
├── chain.py                   # Original LangChain integration
├── parsers_llm.py            # Enhanced document parsing with LLM analysis
├── llm_analyzer.py           # LLM-based contract analysis engine
├── exa_search.py             # Exa.ai search integration
├── prompts/                  # LLM prompts directory
│   ├── __init__.py
│   └── contract_analysis.py  # Contract analysis prompts
├── requirements.txt          # Dependencies (no version pinning)
├── test_functionality.py     # Test script
├── sample_contract.txt       # Sample contract for testing
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## LLM Analysis Pipeline

1. **Document Processing**: Multi-library text extraction with fallbacks
2. **Contract Type Detection**: LLM analyzes content to determine contract category
3. **Governing Law Identification**: AI extracts jurisdiction information
4. **Clause Extraction**: LLM identifies and categorizes key contract provisions
5. **Risk Assessment**: Individual analysis of each clause for potential issues
6. **Recommendation Generation**: AI-powered suggestions for improvements

## API Requirements

- **OpenAI API**: For GPT-based contract analysis (gpt-4.1-mini supported)
- **Exa.ai API**: For regulatory and legal research

## Key Enhancements

### No More Regex!
- **Pure LLM Analysis**: Replaced all regex patterns with intelligent AI processing
- **Context-Aware**: Understands contract context and legal terminology
- **Structured Output**: JSON-formatted results for consistent processing

### Enhanced Document Processing
- **Fallback Extraction**: Multiple libraries ensure text extraction success
- **Format Support**: PDF, DOCX, TXT with intelligent handling
- **Text Cleaning**: Automatic cleanup of OCR artifacts and formatting issues

### Advanced UI
- **Real-time Feedback**: Progress indicators during LLM processing
- **Detailed Previews**: Text extraction and clause analysis previews
- **Enhanced Visualization**: Better formatting and risk color coding

## Testing

Run the test script to verify all components are working:

```bash
python test_functionality.py
```

## Disclaimer

This application uses AI for contract analysis and should be used as a tool to assist legal review, not replace professional legal advice. All AI-generated analysis should be reviewed by qualified legal professionals.

## License

This project is provided as-is for educational and demonstration purposes.
