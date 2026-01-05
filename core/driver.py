#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kinetic Driver - Handles mouse and keyboard automation
"""

import time
import re
import logging
import pyautogui
import pydirectinput
from typing import Dict, Any
from core.security import OperationMode

logger = logging.getLogger(__name__)


class KineticDriver:
    """Driver for mouse and keyboard automation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
    
    def execute_action(self, action: str, mode: OperationMode) -> bool:
        """Execute a single action"""
        try:
            action = action.strip()
            
            # Parse and execute action
            if action.startswith("move_mouse"):
                return self._move_mouse(action)
            
            elif action.startswith("click"):
                return self._click(action)
            
            elif action.startswith("double_click"):
                return self._double_click()
            
            elif action.startswith("drag"):
                return self._drag(action)
            
            elif action.startswith("type_text"):
                return self._type_text(action, mode)
            
            elif action.startswith("press_key"):
                return self._press_key(action, mode)
            
            elif action.startswith("hotkey"):
                return self._hotkey(action)
            
            elif action.startswith("scroll"):
                return self._scroll(action)
            
            elif action.startswith("wait"):
                return self._wait(action)
            
            logger.warning(f"Unknown action: {action}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to execute action: {e}")
            return False
    
    def _move_mouse(self, action: str) -> bool:
        """Move mouse to coordinates"""
        match = re.search(r'move_mouse\((\d+),\s*(\d+)\)', action)
        if match:
            x, y = int(match.group(1)), int(match.group(2))
            duration = self.config.get("mouse_speed", 0.5)
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"Moved mouse to ({x}, {y})")
            return True
        return False
    
    def _click(self, action: str) -> bool:
        """Click mouse button"""
        match = re.search(r"click\(button=['\"](\w+)['\"]\)", action)
        button = match.group(1) if match else 'left'
        pyautogui.click(button=button)
        logger.info(f"Clicked {button} button")
        return True
    
    def _double_click(self) -> bool:
        """Double click"""
        pyautogui.doubleClick()
        logger.info("Double clicked")
        return True
    
    def _drag(self, action: str) -> bool:
        """Drag from one point to another"""
        match = re.search(r'drag\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', action)
        if match:
            x1, y1 = int(match.group(1)), int(match.group(2))
            x2, y2 = int(match.group(3)), int(match.group(4))
            duration = self.config.get("mouse_speed", 0.5)
            pyautogui.moveTo(x1, y1)
            pyautogui.drag(x2 - x1, y2 - y1, duration=duration)
            logger.info(f"Dragged from ({x1}, {y1}) to ({x2}, {y2})")
            return True
        return False
    
    def _type_text(self, action: str, mode: OperationMode) -> bool:
        """Type text"""
        match = re.search(r'type_text\(["\'](.+?)["\']\)', action)
        if match:
            text = match.group(1)
            interval = self.config.get("typing_speed", 0.1)
            
            # Use pydirectinput for games in FAIR_PLAY mode
            if mode == OperationMode.FAIR_PLAY:
                pydirectinput.write(text, interval=interval)
            else:
                pyautogui.write(text, interval=interval)
            
            logger.info(f"Typed text: {text[:20]}...")
            return True
        return False
    
    def _press_key(self, action: str, mode: OperationMode) -> bool:
        """Press a key"""
        match = re.search(r'press_key\(["\'](.+?)["\']\)', action)
        if match:
            key = match.group(1)
            
            if mode == OperationMode.FAIR_PLAY:
                pydirectinput.press(key)
            else:
                pyautogui.press(key)
            
            logger.info(f"Pressed key: {key}")
            return True
        return False
    
    def _hotkey(self, action: str) -> bool:
        """Press hotkey combination"""
        match = re.search(r'hotkey\(["\'](.+?)["\'],\s*["\'](.+?)["\']\)', action)
        if match:
            key1, key2 = match.group(1), match.group(2)
            pyautogui.hotkey(key1, key2)
            logger.info(f"Pressed hotkey: {key1}+{key2}")
            return True
        return False
    
    def _scroll(self, action: str) -> bool:
        """Scroll mouse wheel"""
        match = re.search(r'scroll\((-?\d+)\)', action)
        if match:
            clicks = int(match.group(1))
            pyautogui.scroll(clicks)
            logger.info(f"Scrolled {clicks} clicks")
            return True
        return False
    
    def _wait(self, action: str) -> bool:
        """Wait for specified seconds"""
        match = re.search(r'wait\((\d+(?:\.\d+)?)\)', action)
        if match:
            seconds = float(match.group(1))
            time.sleep(seconds)
            logger.info(f"Waited {seconds} seconds")
            return True
        return False
