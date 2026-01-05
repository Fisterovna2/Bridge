#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI GPT-4 Vision Provider
"""

import logging
import base64
from io import BytesIO
from typing import Optional
from PIL import Image

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("openai not available")

from ai_providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT-4 Vision provider"""
    
    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.name = "OpenAI GPT-4V"
        self.client = None
    
    def initialize(self) -> bool:
        """Initialize OpenAI API"""
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI library not available")
            return False
        
        if not self.api_key:
            logger.error("OpenAI API key not provided")
            return False
        
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
            self.initialized = True
            logger.info("OpenAI provider initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            return False
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def analyze_screen(self, image: Image.Image, instruction: str) -> Optional[str]:
        """Analyze screen with GPT-4 Vision"""
        if not self.is_available():
            logger.error("OpenAI provider not available")
            return None
        
        try:
            base64_image = self._image_to_base64(image)
            
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
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": base64_image}}
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return None
