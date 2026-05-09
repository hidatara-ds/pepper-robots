"""
Image Helper Utilities
Functions for validating and processing image files
"""

import logging
from typing import Tuple, Optional
from PIL import Image

logger = logging.getLogger(__name__)

# Allowed image file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

# Allowed MIME types for image uploads
ALLOWED_MIME = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

def is_valid_image(file) -> Tuple[bool, Optional[str]]:
    """
    Validate if uploaded file is a valid image
    
    Args:
        file: Flask uploaded file object with filename and mimetype attributes
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
        - If valid: (True, None)
        - If invalid: (False, error_message)
    """
    if not file or not hasattr(file, 'filename'):
        return False, "File object is invalid"
    
    filename = file.filename.lower() if file.filename else ""

    # 1. Check file extension
    if '.' not in filename:
        return False, "File extension not found"
    
    extension = filename.rsplit('.', 1)[1]
    if extension not in ALLOWED_EXTENSIONS:
        return False, f"File format not supported. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"

    # 2. Check MIME type
    if not hasattr(file, 'mimetype') or file.mimetype not in ALLOWED_MIME:
        return False, f"Invalid file type. Allowed MIME types: {', '.join(ALLOWED_MIME)}"

    # 3. Validate file content using Pillow
    try:
        if not hasattr(file, 'stream'):
            return False, "File stream not available"
        
        # Reset stream position to beginning
        file.stream.seek(0)
        img = Image.open(file.stream)
        img.verify()  # Raises exception if file is not a valid image
        file.stream.seek(0)  # Reset position for further use
        
        logger.debug(f"Image validation successful: {filename}")
        return True, None
        
    except Exception as e:
        logger.warning(f"Image validation failed for {filename}: {e}")
        return False, "File is not a valid image"
