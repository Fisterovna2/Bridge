#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base AI Provider Class
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional
from PIL import Image

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.name = "BaseProvider"
        self.initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the AI provider
        
        Returns:
            True if initialized successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def analyze_screen(self, image: Image.Image, instruction: str) -> Optional[str]:
        """
        Analyze screen image with AI
        
        Args:
            image: PIL Image to analyze
            instruction: User instruction
        
        Returns:
            AI response as string or None
        """
        pass
    
    def test_connection(self) -> bool:
        """
        Test connection to AI provider
        
        Returns:
            True if connection successful, False otherwise
        """
        return self.is_available()
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.initialized and bool(self.api_key)
    
    def get_name(self) -> str:
        """Get provider name"""
        return self.name
