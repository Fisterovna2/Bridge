#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Macro Manager - Record, save, and playback action macros
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MacroManager:
    """Manages action macros"""
    
    def __init__(self, macros_dir: str = "macros"):
        self.macros_dir = Path(macros_dir)
        self.macros_dir.mkdir(exist_ok=True)
        
        self.recording = False
        self.current_macro = []
        self.current_macro_name = None
    
    def start_recording(self, macro_name: str):
        """Start recording a macro"""
        self.recording = True
        self.current_macro = []
        self.current_macro_name = macro_name
        logger.info(f"Started recording macro: {macro_name}")
    
    def stop_recording(self) -> Optional[List[str]]:
        """Stop recording and return recorded actions"""
        if not self.recording:
            logger.warning("Not currently recording")
            return None
        
        self.recording = False
        logger.info(f"Stopped recording macro: {self.current_macro_name} ({len(self.current_macro)} actions)")
        return self.current_macro.copy()
    
    def record_action(self, action: str):
        """Record an action to current macro"""
        if self.recording:
            self.current_macro.append(action)
            logger.debug(f"Recorded action: {action}")
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.recording
    
    def save_macro(self, macro_name: str, actions: List[str], description: str = "") -> bool:
        """
        Save macro to file
        
        Args:
            macro_name: Name of the macro
            actions: List of action strings
            description: Optional description
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            macro_data = {
                "name": macro_name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "actions": actions,
                "version": "2.0"
            }
            
            file_path = self.macros_dir / f"{macro_name}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(macro_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved macro: {macro_name} ({len(actions)} actions)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save macro: {e}")
            return False
    
    def load_macro(self, macro_name: str) -> Optional[Dict[str, Any]]:
        """
        Load macro from file
        
        Args:
            macro_name: Name of the macro
        
        Returns:
            Macro data dictionary or None
        """
        try:
            file_path = self.macros_dir / f"{macro_name}.json"
            
            if not file_path.exists():
                logger.error(f"Macro not found: {macro_name}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                macro_data = json.load(f)
            
            logger.info(f"Loaded macro: {macro_name}")
            return macro_data
            
        except Exception as e:
            logger.error(f"Failed to load macro: {e}")
            return None
    
    def delete_macro(self, macro_name: str) -> bool:
        """Delete a macro file"""
        try:
            file_path = self.macros_dir / f"{macro_name}.json"
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted macro: {macro_name}")
                return True
            else:
                logger.warning(f"Macro not found: {macro_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete macro: {e}")
            return False
    
    def list_macros(self) -> List[Dict[str, Any]]:
        """
        List all available macros
        
        Returns:
            List of macro info dictionaries
        """
        macros = []
        
        try:
            for file_path in self.macros_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        macro_data = json.load(f)
                    
                    macros.append({
                        "name": macro_data.get("name", file_path.stem),
                        "description": macro_data.get("description", ""),
                        "created_at": macro_data.get("created_at", ""),
                        "action_count": len(macro_data.get("actions", []))
                    })
                except Exception as e:
                    logger.error(f"Failed to load macro info from {file_path}: {e}")
            
            logger.info(f"Found {len(macros)} macros")
            
        except Exception as e:
            logger.error(f"Failed to list macros: {e}")
        
        return macros
    
    def get_macro_actions(self, macro_name: str) -> Optional[List[str]]:
        """
        Get actions from a macro
        
        Args:
            macro_name: Name of the macro
        
        Returns:
            List of action strings or None
        """
        macro_data = self.load_macro(macro_name)
        
        if macro_data:
            return macro_data.get("actions", [])
        
        return None
    
    def export_macro(self, macro_name: str) -> Optional[str]:
        """
        Export macro as JSON string
        
        Args:
            macro_name: Name of the macro
        
        Returns:
            JSON string or None
        """
        macro_data = self.load_macro(macro_name)
        
        if macro_data:
            return json.dumps(macro_data, indent=2, ensure_ascii=False)
        
        return None
    
    def import_macro(self, json_string: str) -> Optional[str]:
        """
        Import macro from JSON string
        
        Args:
            json_string: JSON string with macro data
        
        Returns:
            Macro name if imported successfully, None otherwise
        """
        try:
            macro_data = json.loads(json_string)
            
            macro_name = macro_data.get("name")
            if not macro_name:
                logger.error("Macro name not found in import data")
                return None
            
            actions = macro_data.get("actions", [])
            description = macro_data.get("description", "")
            
            if self.save_macro(macro_name, actions, description):
                return macro_name
            else:
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse macro JSON: {e}")
            return None
