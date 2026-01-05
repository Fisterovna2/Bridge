#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenRouter Multi-Model Provider
"""

import logging
import base64
from io import BytesIO
from typing import Optional
from PIL import Image

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests not available")

from ai_providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter multi-model provider"""
    
    def __init__(self, api_key: str = "", model: str = "openai/gpt-4-vision-preview"):
        super().__init__(api_key)
        self.name = "OpenRouter"
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
    
    def initialize(self) -> bool:
        """Initialize OpenRouter API"""
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return False
        
        if not self.api_key:
            logger.error("OpenRouter API key not provided")
            return False
        
        self.initialized = True
        logger.info(f"OpenRouter provider initialized with model: {self.model}")
        return True
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def analyze_screen(self, image: Image.Image, instruction: str) -> Optional[str]:
        """Analyze screen with OpenRouter"""
        if not self.is_available():
            logger.error("OpenRouter provider not available")
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
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": base64_image}}
                            ]
                        }
                    ]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"OpenRouter request failed: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"OpenRouter analysis failed: {e}")
            return None
