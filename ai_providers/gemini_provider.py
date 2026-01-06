#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Gemini AI Provider
"""

import logging
from typing import Optional
from PIL import Image

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-genai not available")

from ai_providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Google Gemini AI provider"""
    
    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.name = "Gemini"
        self.client = None
    
    def initialize(self) -> bool:
        """Initialize Gemini API"""
        if not GEMINI_AVAILABLE:
            logger.error("Gemini library not available")
            return False
        
        if not self.api_key:
            logger.error("Gemini API key not provided")
            return False
        
        try:
            self.client = genai.Client(api_key=self.api_key)
            self.initialized = True
            logger.info("Gemini provider initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            return False
    
    def analyze_screen(self, image: Image.Image, instruction: str) -> Optional[str]:
        """Analyze screen with Gemini Vision"""
        if not self.is_available():
            logger.error("Gemini provider not available")
            return None
        
        try:
            prompt = f"""You are a desktop automation assistant. 
Analyze the screenshot and provide step-by-step instructions to accomplish this task:
{instruction}

Respond with clear, executable steps using these actions:
- move_mouse(x, y)
- click(button='left/right/middle')
- double_click()
- drag(x1, y1, x2, y2)
- type_text("text")
- press_key("key")
- hotkey("ctrl", "c")
- scroll(clicks)
- wait(seconds)

Be specific with coordinates and actions."""
            
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=[prompt, image]
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return None
