#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anthropic Claude Vision Provider
"""

import logging
import base64
from io import BytesIO
from typing import Optional
from PIL import Image

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("anthropic not available")

from ai_providers.base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude Vision provider"""
    
    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
        self.name = "Claude"
        self.client = None
    
    def initialize(self) -> bool:
        """Initialize Anthropic API"""
        if not ANTHROPIC_AVAILABLE:
            logger.error("Anthropic library not available")
            return False
        
        if not self.api_key:
            logger.error("Anthropic API key not provided")
            return False
        
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.initialized = True
            logger.info("Claude provider initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Claude: {e}")
            return False
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def analyze_screen(self, image: Image.Image, instruction: str) -> Optional[str]:
        """Analyze screen with Claude Vision"""
        if not self.is_available():
            logger.error("Claude provider not available")
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
            
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Claude analysis failed: {e}")
            return None
