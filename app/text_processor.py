"""
Text Processing Module
Cleans and normalizes extracted text for AI processing.
"""
import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Clean extracted text:
    - Normalize Unicode characters
    - Remove control characters
    - Fix encoding artifacts
    - Normalize whitespace while preserving paragraph structure
    - Remove excessive blank lines
    """
    if not text:
        return ""
    
    # Normalize Unicode
    text = unicodedata.normalize("NFKD", text)
    
    # Remove control characters except newline and tab
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Fix common OCR/encoding artifacts
    text = text.replace('\xad', '-')  # soft hyphen
    text = text.replace('\u2019', "'")  # right single quote
    text = text.replace('\u2018', "'")  # left single quote
    text = text.replace('\u201c', '"')  # left double quote
    text = text.replace('\u201d', '"')  # right double quote
    text = text.replace('\u2013', '-')  # en dash
    text = text.replace('\u2014', '-')  # em dash
    text = text.replace('\u2026', '...')  # ellipsis
    
    # Normalize whitespace within lines (preserve newlines)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Collapse multiple spaces/tabs to single space
        line = re.sub(r'[ \t]+', ' ', line)
        cleaned_lines.append(line.strip())
    
    text = '\n'.join(cleaned_lines)
    
    # Remove excessive blank lines (keep max 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def truncate_for_model(text: str, max_chars: int = 10000) -> str:
    """
    Truncate text to fit within model context limits.
    Tries to truncate at sentence boundaries.
    """
    if len(text) <= max_chars:
        return text
    
    # Try to cut at a sentence boundary
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    last_newline = truncated.rfind('\n')
    
    cut_point = max(last_period, last_newline)
    if cut_point > max_chars * 0.7:
        return truncated[:cut_point + 1]
    
    return truncated


def process_text(raw_text: str) -> str:
    """
    Full text processing pipeline:
    1. Clean text
    2. Normalize
    Returns processed text ready for AI modules.
    """
    cleaned = clean_text(raw_text)
    return cleaned
