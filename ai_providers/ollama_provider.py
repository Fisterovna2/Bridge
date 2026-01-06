#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Local AI Provider
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

# Ollama models configuration
OLLAMA_MODELS = {
    "vision": "llava",              # Vision model - can see screen
    "smart": "llama3",              # Smart model for complex tasks
    "uncensored": "dolphin-mixtral",  # For CURIOS mode, without restrictions
    "fast": "phi3"                  # Fast model for quick tasks
}


class OllamaProvider(BaseAIProvider):
    """Ollama local AI provider"""
    
    def __init__(self, api_key: str = "", base_url: str = "http://localhost:11434", model: str = "llava"):
        super().__init__(api_key)
        self.name = "Ollama"
        self.base_url = base_url
        self.model = model  # Default vision model
    
    def set_model(self, model: str):
        """Set the model to use"""
        self.model = model
        logger.info(f"Ollama model set to: {model}")
    
    def initialize(self) -> bool:
        """Initialize Ollama connection"""
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return False
        
        try:
            # Test connection
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.initialized = True
                logger.info(f"Ollama provider initialized at {self.base_url}")
                return True
            else:
                logger.error(f"Ollama server not responding: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def analyze_screen(self, image: Image.Image, instruction: str) -> Optional[str]:
        """Analyze screen with Ollama Vision"""
        if not self.is_available():
            logger.error("Ollama provider not available")
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
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "images": [base64_image],
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama request failed: {response.status_code}")
                return None
            
        except Exception as e:
            logger.error(f"Ollama analysis failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if provider is available (no API key needed for local)"""
        return self.initialized
