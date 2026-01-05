#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example Plugin - Demonstrates plugin system usage
"""

import logging
from typing import Dict, Any, Optional
from plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)


class ExamplePlugin(BasePlugin):
    """Example plugin that logs actions"""
    
    def __init__(self):
        super().__init__()
        self.name = "ExamplePlugin"
        self.version = "1.0"
        self.description = "Example plugin that logs all actions"
        self.action_count = 0
    
    def on_load(self) -> bool:
        """Called when plugin is loaded"""
        logger.info(f"{self.name} loaded")
        return True
    
    def on_action(self, action: str, context: Dict[str, Any]) -> Optional[Any]:
        """Called when an action is executed"""
        self.action_count += 1
        logger.info(f"{self.name}: Action #{self.action_count} - {action[:50]}")
        
        # You can modify or inspect the action here
        # Return None to not interfere with normal execution
        return None
    
    def on_unload(self) -> bool:
        """Called when plugin is unloaded"""
        logger.info(f"{self.name} unloaded. Total actions logged: {self.action_count}")
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        info = super().get_info()
        info["action_count"] = self.action_count
        return info
