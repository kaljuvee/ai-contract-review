"""
Document parsers with LLM-based analysis instead of regex patterns.
"""

import fitz  # PyMuPDF
import pdfplumber
import PyPDF2
from docx import Document
import docx2txt
import re
import markdown
from bs4 import BeautifulSoup
from typing import IO, Optional, Dict
import io
import logging
from llm_analyzer import (
    detect_contract_type_llm,
    detect_governing_law_llm,
    extract_key_clauses_llm,
    analyze_contract_comprehensive
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_pdf_pymupdf(file_obj: IO) -> str:
    """Extract text using PyMuPDF (fitz)."""
    try:
        doc = fitz.open(stream=file_obj.read(), filetype="pdf")
        text = " ".join(page.get_text() for page in doc)
        doc.close()
        return text
    except Exception as e:
        logger.warning(f"PyMuPDF extraction failed: {e}")
        return ""


def extract_text_from_pdf_pdfplumber(file_obj: IO) -> str:
    """Extract text using pdfplumber."""
    try:
        file_obj.seek(0)
        with pdfplumber.open(file_obj) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}")
        return ""


def extract_text_from_pdf_pypdf2(file_obj: IO) -> str:
    """Extract text using PyPDF2."""
    try:
        file_obj.seek(0)
        pdf_reader = PyPDF2.PdfReader(file_obj)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.warning(f"PyPDF2 extraction failed: {e}")
        return ""


def extract_text_from_docx_python_docx(file_obj: IO) -> str:
    """Extract text using python-docx."""
    try:
        file_obj.seek(0)
        doc = Document(file_obj)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        return text
    except Exception as e:
        logger.warning(f"python-docx extraction failed: {e}")
        return ""


def extract_text_from_docx_docx2txt(file_obj: IO) -> str:
    """Extract text using docx2txt."""
    try:
        file_obj.seek(0)
        text = docx2txt.process(file_obj)
        return text if text else ""
    except Exception as e:
        logger.warning(f"docx2txt extraction failed: {e}")
        return ""


def extract_text(file_obj: IO) -> str:
    """
    Extract text from uploaded file with multiple fallback methods.
    
    Args:
        file_obj: File object from Streamlit file uploader
        
    Returns:
        str: Extracted text content
    """
    suffix = file_obj.name.split(".")[-1].lower()
    text = ""
    
    if suffix == "pdf":
        # Try multiple PDF extraction methods
        methods = [
            ("PyMuPDF", extract_text_from_pdf_pymupdf),
            ("pdfplumber", extract_text_from_pdf_pdfplumber),
            ("PyPDF2", extract_text_from_pdf_pypdf2)
        ]
        
        for method_name, method_func in methods:
            file_obj.seek(0)
            text = method_func(file_obj)
            if text.strip():
                logger.info(f"Successfully extracted text using {method_name}")
                break
            else:
                logger.warning(f"{method_name} returned empty text")
                
    elif suffix == "docx":
        # Try multiple DOCX extraction methods
        methods = [
            ("python-docx", extract_text_from_docx_python_docx),
            ("docx2txt", extract_text_from_docx_docx2txt)
        ]
        
        for method_name, method_func in methods:
            file_obj.seek(0)
            text = method_func(file_obj)
            if text.strip():
                logger.info(f"Successfully extracted text using {method_name}")
                break
            else:
                logger.warning(f"{method_name} returned empty text")
                
    elif suffix == "txt":
        try:
            file_obj.seek(0)
            text = file_obj.read().decode('utf-8')
        except UnicodeDecodeError:
            try:
                file_obj.seek(0)
                text = file_obj.read().decode('latin-1')
            except Exception as e:
                logger.error(f"Failed to decode text file: {e}")
                text = ""
    
    return text.strip()


def convert_text_to_markdown(text: str, title: Optional[str] = None) -> str:
    """
    Convert plain text to markdown format with basic formatting.
    
    Args:
        text: Plain text content
        title: Optional title for the document
        
    Returns:
        str: Markdown formatted text
    """
    if not text.strip():
        return ""
    
    markdown_content = ""
    
    # Add title if provided
    if title:
        markdown_content += f"# {title}\n\n"
    
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Check if it looks like a heading (all caps, short line)
        if len(paragraph) < 100 and paragraph.isupper() and not paragraph.endswith('.'):
            markdown_content += f"## {paragraph.title()}\n\n"
        # Check if it looks like a numbered section
        elif re.match(r'^\d+\.?\s+[A-Z]', paragraph):
            markdown_content += f"### {paragraph}\n\n"
        # Regular paragraph
        else:
            markdown_content += f"{paragraph}\n\n"
    
    return markdown_content


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and formatting issues.
    
    Args:
        text: Raw extracted text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page breaks and form feeds
    text = re.sub(r'[\f\r]+', '\n', text)
    
    # Fix common OCR issues
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between lowercase and uppercase
    text = re.sub(r'(\.)([A-Z])', r'\1 \2', text)     # Add space after period before uppercase
    
    # Remove extra newlines but preserve paragraph breaks
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    return text.strip()


# LLM-based functions (replacing regex-based ones)
def detect_contract_type(text: str) -> str:
    """
    Detect contract type using LLM instead of regex.
    
    Args:
        text: Contract text content
        
    Returns:
        str: Detected contract type
    """
    return detect_contract_type_llm(text)


def detect_country(text: str) -> str:
    """
    Detect governing law country using LLM instead of regex.
    
    Args:
        text: Contract text content
        
    Returns:
        str: Detected country or "Unknown"
    """
    return detect_governing_law_llm(text)


def extract_key_clauses(text: str) -> Dict:
    """
    Extract key contract clauses using LLM instead of regex.
    
    Args:
        text: Contract text content
        
    Returns:
        Dict: Dictionary of clause types and their information
    """
    clauses_info = extract_key_clauses_llm(text)
    
    # Convert to format expected by the UI
    clauses = {}
    for clause_type, clause_info in clauses_info.items():
        clauses[clause_type] = [clause_info.text]  # Wrap in list for compatibility
    
    return clauses


def analyze_contract_full(text: str) -> Dict:
    """
    Perform full contract analysis using LLM.
    
    Args:
        text: Contract text content
        
    Returns:
        Dict: Complete analysis results
    """
    return analyze_contract_comprehensive(text)
