#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Text Detection Module
"""

import logging
from typing import List, Tuple, Optional
from PIL import Image
import pyautogui

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logging.warning("EasyOCR not available, OCR features disabled")

logger = logging.getLogger(__name__)


class OCREngine:
    """OCR engine for text detection and interaction"""
    
    def __init__(self, languages: List[str] = None):
        """
        Initialize OCR engine
        
        Args:
            languages: List of language codes (default: ['en'])
        """
        self.languages = languages or ['en']
        self.reader = None
        
        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(self.languages, gpu=False)
                logger.info(f"OCR initialized with languages: {self.languages}")
            except Exception as e:
                logger.error(f"Failed to initialize OCR: {e}")
                self.reader = None
        else:
            logger.warning("OCR not available - install easyocr")
    
    def is_available(self) -> bool:
        """Check if OCR is available"""
        return self.reader is not None
    
    def find_text(self, image: Image.Image, search_text: str, 
                  case_sensitive: bool = False) -> List[Tuple[str, Tuple[int, int, int, int], float]]:
        """
        Find text on screen
        
        Args:
            image: PIL Image to search
            search_text: Text to find
            case_sensitive: Whether search is case-sensitive
        
        Returns:
            List of (text, bbox, confidence) tuples
            bbox format: (x1, y1, x2, y2)
        """
        if not self.is_available():
            logger.error("OCR not available")
            return []
        
        try:
            # Run OCR
            results = self.reader.readtext(image)
            
            # Filter results by search text
            matches = []
            search_lower = search_text if case_sensitive else search_text.lower()
            
            for detection in results:
                bbox, text, confidence = detection
                text_to_compare = text if case_sensitive else text.lower()
                
                if search_lower in text_to_compare:
                    # Convert bbox format from [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] to (x1,y1,x2,y2)
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    x1, y1 = min(x_coords), min(y_coords)
                    x2, y2 = max(x_coords), max(y_coords)
                    
                    matches.append((text, (int(x1), int(y1), int(x2), int(y2)), confidence))
            
            logger.info(f"Found {len(matches)} matches for '{search_text}'")
            return matches
            
        except Exception as e:
            logger.error(f"OCR search failed: {e}")
            return []
    
    def find_text_on_screen(self, search_text: str, 
                           case_sensitive: bool = False) -> List[Tuple[str, Tuple[int, int, int, int], float]]:
        """
        Find text on current screen
        
        Args:
            search_text: Text to find
            case_sensitive: Whether search is case-sensitive
        
        Returns:
            List of (text, bbox, confidence) tuples
        """
        try:
            screenshot = pyautogui.screenshot()
            return self.find_text(screenshot, search_text, case_sensitive)
        except Exception as e:
            logger.error(f"Failed to search screen: {e}")
            return []
    
    def click_text(self, search_text: str, case_sensitive: bool = False, 
                   occurrence: int = 0) -> bool:
        """
        Click on found text
        
        Args:
            search_text: Text to click
            case_sensitive: Whether search is case-sensitive
            occurrence: Which occurrence to click (0 = first)
        
        Returns:
            True if clicked, False if not found
        """
        matches = self.find_text_on_screen(search_text, case_sensitive)
        
        if not matches:
            logger.warning(f"Text '{search_text}' not found on screen")
            return False
        
        if occurrence >= len(matches):
            logger.warning(f"Occurrence {occurrence} not found (only {len(matches)} matches)")
            return False
        
        # Get bbox of target occurrence
        text, bbox, confidence = matches[occurrence]
        x1, y1, x2, y2 = bbox
        
        # Calculate center point
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        # Click center
        pyautogui.click(center_x, center_y)
        logger.info(f"Clicked text '{text}' at ({center_x}, {center_y})")
        return True
    
    def get_all_text(self, image: Image.Image) -> List[Tuple[str, Tuple[int, int, int, int], float]]:
        """
        Get all text from image
        
        Args:
            image: PIL Image to analyze
        
        Returns:
            List of (text, bbox, confidence) tuples
        """
        if not self.is_available():
            logger.error("OCR not available")
            return []
        
        try:
            results = self.reader.readtext(image)
            
            parsed_results = []
            for detection in results:
                bbox, text, confidence = detection
                
                # Convert bbox format
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                x1, y1 = min(x_coords), min(y_coords)
                x2, y2 = max(x_coords), max(y_coords)
                
                parsed_results.append((text, (int(x1), int(y1), int(x2), int(y2)), confidence))
            
            logger.info(f"Extracted {len(parsed_results)} text regions")
            return parsed_results
            
        except Exception as e:
            logger.error(f"Failed to extract text: {e}")
            return []
