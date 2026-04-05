"""
File Type Detection Module
Automatically detects file type from extension and MIME type.
"""
import os
import mimetypes

SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
}

SUPPORTED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "image/png": "image",
    "image/jpeg": "image",
}


def detect_file_type(filename: str, content_type: str = None) -> str:
    """
    Detect file type from filename extension and optional MIME content type.
    
    Returns: 'pdf', 'docx', 'image', or raises ValueError
    """
    # Try extension first
    ext = os.path.splitext(filename)[1].lower()
    if ext in SUPPORTED_EXTENSIONS:
        return SUPPORTED_EXTENSIONS[ext]
    
    # Try MIME type
    if content_type and content_type in SUPPORTED_MIME_TYPES:
        return SUPPORTED_MIME_TYPES[content_type]
    
    # Try guessing MIME type
    guessed_type, _ = mimetypes.guess_type(filename)
    if guessed_type and guessed_type in SUPPORTED_MIME_TYPES:
        return SUPPORTED_MIME_TYPES[guessed_type]
    
    raise ValueError(
        f"Unsupported file type: {filename}. "
        f"Supported formats: PDF (.pdf), DOCX (.docx), Images (.png, .jpg, .jpeg)"
    )
