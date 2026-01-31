import io
import os
from PIL import Image
from typing import Tuple, Optional
import logging

def compress_image(
    image_file, 
    quality: int = 85, 
    max_size: Tuple[int, int] = (800, 800),
    format: str = 'JPEG'
) -> Tuple[io.BytesIO, str]:
    """
    Compress and resize image file
    
    Args:
        image_file: Flask uploaded file object
        quality: JPEG quality (1-100, default 85)
        max_size: Maximum dimensions (width, height) 
        format: Output format (JPEG/PNG)
        
    Returns:
        Tuple of (compressed_image_buffer, filename_with_extension)
    """
    try:
        # Reset file pointer
        image_file.seek(0)
        
        # Open image with PIL
        original_image = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary (for JPEG)
        if original_image.mode in ('RGBA', 'LA') and format.upper() == 'JPEG':
            # Create white background
            background = Image.new('RGB', original_image.size, (255, 255, 255))
            if original_image.mode == 'RGBA':
                background.paste(original_image, mask=original_image.split()[-1])
            else:
                background.paste(original_image)
            original_image = background
        elif original_image.mode != 'RGB' and format.upper() == 'JPEG':
            original_image = original_image.convert('RGB')
        
        # Get original dimensions
        original_width, original_height = original_image.size
        logging.info(f"Original image size: {original_width}x{original_height}")
        
        # Calculate new size maintaining aspect ratio
        ratio = min(max_size[0] / original_width, max_size[1] / original_height)
        
        if ratio < 1:  # Only resize if image is larger than max_size
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logging.info(f"Resized image to: {new_width}x{new_height}")
        else:
            resized_image = original_image
            logging.info("Image size within limits, no resizing needed")
        
        # Create output buffer
        output_buffer = io.BytesIO()
        
        # Save compressed image to buffer
        save_kwargs = {'format': format.upper()}
        if format.upper() == 'JPEG':
            save_kwargs.update({
                'quality': quality,
                'optimize': True,
                'progressive': True
            })
        elif format.upper() == 'PNG':
            save_kwargs.update({
                'optimize': True,
                'compress_level': 6
            })
        
        resized_image.save(output_buffer, **save_kwargs)
        
        # Get compressed size info
        output_buffer.seek(0)
        compressed_size = len(output_buffer.getvalue())
        
        # Reset pointer for return
        output_buffer.seek(0)
        
        # Generate new filename with compression info
        original_name = os.path.splitext(image_file.filename)[0] if image_file.filename else "compressed_image"
        extension = '.jpg' if format.upper() == 'JPEG' else '.png'
        compressed_filename = f"{original_name}_compressed{extension}"
        
        logging.info(f"Image compressed successfully. New size: {compressed_size} bytes")
        
        return output_buffer, compressed_filename
        
    except Exception as e:
        logging.error(f"Error compressing image: {e}")
        raise ValueError(f"Failed to compress image: {str(e)}")

def get_image_info(image_file) -> dict:
    """
    Get image information without modifying the file
    
    Args:
        image_file: Flask uploaded file object
        
    Returns:
        Dict with image info (width, height, format, size)
    """
    try:
        image_file.seek(0)
        
        with Image.open(image_file) as img:
            info = {
                'width': img.width,
                'height': img.height, 
                'format': img.format,
                'mode': img.mode,
                'size_bytes': len(image_file.read())
            }
        
        image_file.seek(0)  # Reset for subsequent use
        return info
        
    except Exception as e:
        logging.error(f"Error getting image info: {e}")
        return {}

def should_compress(image_file, size_threshold: int = 500 * 1024) -> bool:
    """
    Check if image should be compressed based on file size
    
    Args:
        image_file: Flask uploaded file object
        size_threshold: Size threshold in bytes (default 500KB)
        
    Returns:
        True if image should be compressed
    """
    try:
        image_file.seek(0)
        size = len(image_file.read())
        image_file.seek(0)
        
        return size > size_threshold
        
    except Exception:
        return True  # Default to compress if can't determine size 