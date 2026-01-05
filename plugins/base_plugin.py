#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Plugin Class
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0"
        self.description = "Base plugin"
        self.enabled = False
        self.config = {}
    
    @abstractmethod
    def on_load(self) -> bool:
        """
        Called when plugin is loaded
        
        Returns:
            True if loaded successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def on_action(self, action: str, context: Dict[str, Any]) -> Optional[Any]:
        """
        Called when an action is executed
        
        Args:
            action: Action string
            context: Context dictionary with agent state
        
        Returns:
            Plugin can return data or None
        """
        pass
    
    @abstractmethod
    def on_unload(self) -> bool:
        """
        Called when plugin is unloaded
        
        Returns:
            True if unloaded successfully, False otherwise
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled
        }
    
    def set_config(self, config: Dict[str, Any]):
        """Set plugin configuration"""
        self.config = config
    
    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self.config
