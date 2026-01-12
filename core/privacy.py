#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Privacy Filter Module
Provides privacy protection for screenshots and logs
"""

import re
import logging
from typing import List, Tuple
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)


class PrivacyFilter:
    """Filter for protecting privacy in screenshots and logs"""
    
    # Regions for blur (can be configured)
    # Format: (x, y, width, height) as percentages or absolute pixels
    BLUR_REGIONS: List[Tuple[int, int, int, int]] = []
    
    # Patterns for sanitizing sensitive data
    SENSITIVE_PATTERNS = [
        # API Keys
        (r'api[_-]?key["\s:=]+["\']?[\w-]{20,}', 'api_key: ***'),
        (r'sk-[a-zA-Z0-9]{48}', '***'),  # OpenAI keys
        (r'AIza[a-zA-Z0-9_-]{35}', '***'),  # Google API keys
        
        # Passwords and secrets
        (r'password["\s:=]+["\']?[^\s"\']+', 'password: ***'),
        (r'passwd["\s:=]+["\']?[^\s"\']+', 'passwd: ***'),
        (r'secret["\s:=]+["\']?[^\s"\']+', 'secret: ***'),
        
        # Tokens
        (r'token["\s:=]+["\']?[\w-]{20,}', 'token: ***'),
        (r'Bearer\s+[\w-]+', 'Bearer ***'),
        
        # Credentials
        (r'credential[s]?["\s:=]+["\']?[^\s"\']+', 'credentials: ***'),
        
        # Private keys
        (r'private[_-]?key["\s:=]+["\']?[^\s"\']+', 'private_key: ***'),
        (r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----', 
         '*** PRIVATE KEY REDACTED ***'),
        
        # Email addresses
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***'),
        
        # Phone numbers
        (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '***-***-****'),
        (r'\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '+***-***-****'),
        
        # Credit card patterns (basic)
        (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '****-****-****-****'),
        
        # Social security numbers
        (r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****'),
    ]
    
    def __init__(self, custom_blur_regions: List[Tuple[int, int, int, int]] = None):
        """
        Initialize privacy filter
        
        Args:
            custom_blur_regions: Optional list of regions to blur (x, y, width, height)
        """
        if custom_blur_regions:
            self.BLUR_REGIONS = custom_blur_regions
    
    def blur_screenshot(self, image: Image.Image, blur_radius: int = 15) -> Image.Image:
        """
        Blur confidential zones on screenshot
        
        Args:
            image: PIL Image to process
            blur_radius: Gaussian blur radius (default: 15)
        
        Returns:
            PIL Image with blurred regions
        """
        if not self.BLUR_REGIONS:
            # No regions to blur
            return image
        
        try:
            blurred = image.copy()
            width, height = blurred.size
            
            for region in self.BLUR_REGIONS:
                x, y, w, h = region
                
                # Handle percentage-based coordinates (0-1 range)
                if all(isinstance(v, float) and 0 <= v <= 1 for v in region):
                    x = int(x * width)
                    y = int(y * height)
                    w = int(w * width)
                    h = int(h * height)
                
                # Ensure region is within image bounds
                x = max(0, min(x, width))
                y = max(0, min(y, height))
                w = max(0, min(w, width - x))
                h = max(0, min(h, height - y))
                
                if w > 0 and h > 0:
                    # Extract region
                    box = (x, y, x + w, y + h)
                    region_img = blurred.crop(box)
                    
                    # Apply Gaussian blur
                    blurred_region = region_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                    
                    # Paste back
                    blurred.paste(blurred_region, box)
                    
                    logger.debug(f"Blurred region: {box}")
            
            return blurred
            
        except Exception as e:
            logger.error(f"Failed to blur screenshot: {e}")
            return image
    
    def add_blur_region(self, x: int, y: int, width: int, height: int):
        """
        Add a region to be blurred
        
        Args:
            x: X coordinate (or percentage if 0-1)
            y: Y coordinate (or percentage if 0-1)
            width: Width (or percentage if 0-1)
            height: Height (or percentage if 0-1)
        """
        self.BLUR_REGIONS.append((x, y, width, height))
        logger.info(f"Added blur region: ({x}, {y}, {width}, {height})")
    
    def clear_blur_regions(self):
        """Clear all blur regions"""
        self.BLUR_REGIONS = []
        logger.info("Cleared all blur regions")
    
    def sanitize_text(self, text: str) -> str:
        """
        Replace sensitive data in text with placeholders
        
        Args:
            text: Text to sanitize
        
        Returns:
            Sanitized text with sensitive data replaced
        """
        if not text:
            return text
        
        sanitized = text
        
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            try:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
            except Exception as e:
                logger.debug(f"Failed to apply pattern {pattern}: {e}")
        
        return sanitized
    
    def sanitize_for_log(self, text: str) -> str:
        """
        Sanitize text specifically for logging
        Alias for sanitize_text for compatibility
        
        Args:
            text: Text to sanitize
        
        Returns:
            Sanitized text
        """
        return self.sanitize_text(text)
    
    def add_sensitive_pattern(self, pattern: str, replacement: str = '***'):
        """
        Add a custom sensitive pattern
        
        Args:
            pattern: Regular expression pattern to match
            replacement: Replacement string
        """
        self.SENSITIVE_PATTERNS.append((pattern, replacement))
        logger.info(f"Added custom sensitive pattern: {pattern}")
    
    @staticmethod
    def blur_sensitive_areas(image: Image.Image, blur_radius: int = 15) -> Image.Image:
        """
        Static method to blur sensitive areas (alias for backward compatibility)
        
        Args:
            image: PIL Image to process
            blur_radius: Gaussian blur radius (default: 15)
        
        Returns:
            PIL Image with blurred regions
        """
        return default_filter.blur_screenshot(image, blur_radius)


# Create a global instance for easy access
default_filter = PrivacyFilter()


def blur_screenshot(image: Image.Image, blur_radius: int = 15) -> Image.Image:
    """
    Convenience function to blur screenshot using default filter
    
    Args:
        image: PIL Image to process
        blur_radius: Gaussian blur radius
    
    Returns:
        PIL Image with blurred regions
    """
    return default_filter.blur_screenshot(image, blur_radius)


def sanitize_text(text: str) -> str:
    """
    Convenience function to sanitize text using default filter
    
    Args:
        text: Text to sanitize
    
    Returns:
        Sanitized text
    """
    return default_filter.sanitize_text(text)
