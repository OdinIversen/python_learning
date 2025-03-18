"""
File Handler for Plagiarism Detector

Utilities for loading and saving files in various formats.
"""

import json
import os
from pathlib import Path
from typing import Optional, Any, Dict
import PyPDF2
import docx


def load_document(file_path: str) -> str:
    """
    Load document content from various file formats.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Extracted text from the document
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    file_extension = file_path.suffix.lower()
    
    if file_extension in ['.txt', '.md', '.tex']:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            return file.read()
            
    elif file_extension == '.pdf':
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text() + "\n\n"
            return text
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {e}")
            
    elif file_extension in ['.docx', '.doc']:
        try:
            doc = docx.Document(file_path)
            return "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        except Exception as e:
            raise ValueError(f"Error extracting text from Word document: {e}")
            
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")


def save_text_file(content: str, file_path: str) -> str:
    """
    Save text content to a file.
    
    Args:
        content: Text content to save
        file_path: Path where the file should be saved
        
    Returns:
        Path to the saved file
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(file_path)


def save_json_file(data: Dict[str, Any], file_path: str, indent: int = 2) -> str:
    """
    Save data as a JSON file.
    
    Args:
        data: Data to save
        file_path: Path where the file should be saved
        indent: Number of spaces for indentation
        
    Returns:
        Path to the saved file
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)
    
    return str(file_path)


def ensure_output_dir(output_dir: Optional[str] = None) -> Path:
    """
    Ensure that the output directory exists.
    
    Args:
        output_dir: Directory path (created if it doesn't exist)
        
    Returns:
        Path object for the output directory
    """
    if output_dir is None:
        # Use the default personal_files/plagiarism_results directory from project structure
        output_dir = os.path.join("personal_files", "plagiarism_results")
        
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    return output_path


def get_output_filename(base_name: str, extension: str, output_dir: Optional[str] = None) -> str:
    """
    Generate an output filename with the given base name and extension.
    
    Args:
        base_name: Base name for the file
        extension: File extension (without dot)
        output_dir: Optional directory path
        
    Returns:
        Full output file path
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.{extension}"
    
    output_path = ensure_output_dir(output_dir) / filename
    
    return str(output_path)