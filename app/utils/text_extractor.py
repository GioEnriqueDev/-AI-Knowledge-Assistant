"""
Text Extraction Utilities
Extract text content from various document formats (PDF, TXT).
"""

import io
from typing import Optional
from PyPDF2 import PdfReader
from fastapi import UploadFile, HTTPException


async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text content from uploaded file.
    
    Supports PDF and TXT formats.
    
    Args:
        file: Uploaded file object
        
    Returns:
        str: Extracted text content
        
    Raises:
        HTTPException: If file format is unsupported or extraction fails
    """
    filename = file.filename.lower()
    
    try:
        content = await file.read()
        
        if filename.endswith('.pdf'):
            return extract_from_pdf(content)
        elif filename.endswith('.txt'):
            return extract_from_txt(content)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Only PDF and TXT are allowed."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting text from file: {str(e)}"
        )


def extract_from_pdf(content: bytes) -> str:
    """
    Extract text from PDF file.
    
    Args:
        content: PDF file bytes
        
    Returns:
        str: Extracted text
    """
    pdf_file = io.BytesIO(content)
    reader = PdfReader(pdf_file)
    
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    
    full_text = "\n\n".join(text_parts)
    
    if not full_text.strip():
        raise ValueError("No text could be extracted from PDF")
    
    return full_text


def extract_from_txt(content: bytes) -> str:
    """
    Extract text from TXT file.
    
    Args:
        content: TXT file bytes
        
    Returns:
        str: Decoded text
    """
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            text = content.decode(encoding)
            if text.strip():
                return text
        except UnicodeDecodeError:
            continue
    
    raise ValueError("Could not decode text file with supported encodings")
