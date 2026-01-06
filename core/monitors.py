#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-monitor support module
"""

import logging
from typing import List, Dict, Tuple, Optional
from PIL import Image
import pyautogui

try:
    from screeninfo import get_monitors, Monitor
    SCREENINFO_AVAILABLE = True
except ImportError:
    SCREENINFO_AVAILABLE = False
    logging.warning("screeninfo not available, multi-monitor support limited")

logger = logging.getLogger(__name__)


class MonitorManager:
    """Manages multiple monitors"""
    
    def __init__(self):
        self.monitors = self._detect_monitors()
        self.selected_monitor = 0  # Primary monitor by default
    
    def _detect_monitors(self) -> List[Dict[str, any]]:
        """Detect all connected monitors"""
        monitors = []
        
        if SCREENINFO_AVAILABLE:
            try:
                screen_monitors = get_monitors()
                for i, monitor in enumerate(screen_monitors):
                    monitors.append({
                        "id": i,
                        "name": monitor.name if hasattr(monitor, 'name') else f"Monitor {i+1}",
                        "x": monitor.x,
                        "y": monitor.y,
                        "width": monitor.width,
                        "height": monitor.height,
                        "is_primary": monitor.is_primary if hasattr(monitor, 'is_primary') else (i == 0)
                    })
                logger.info(f"Detected {len(monitors)} monitors")
            except Exception as e:
                logger.error(f"Failed to detect monitors with screeninfo: {e}")
        
        # Fallback to pyautogui screen size if no monitors detected
        if not monitors:
            screen_width, screen_height = pyautogui.size()
            monitors.append({
                "id": 0,
                "name": "Primary Monitor",
                "x": 0,
                "y": 0,
                "width": screen_width,
                "height": screen_height,
                "is_primary": True
            })
            logger.info("Using fallback single monitor detection")
        
        return monitors
    
    def get_monitors(self) -> List[Dict[str, any]]:
        """Get list of all monitors with human-readable numbering"""
        return self.monitors
    
    def get_list(self) -> List[str]:
        """
        Get list of monitors as formatted strings with numbering from 1
        Returns list like: ["Monitor 1: Display (1920x1080)", "Monitor 2: Display (2560x1440)"]
        """
        result = []
        for i, m in enumerate(self.monitors):
            # Clean up monitor name
            name = m.get("name", f"Display")
            # Remove Windows-specific prefix
            if name.startswith("\\\\.\\"):
                name = name.replace("\\\\.\\", "")
            # Simplify generic names
            if "DISPLAY" in name.upper():
                name = "Display"
            
            # Format: Monitor 1: Name (WIDTHxHEIGHT)
            result.append(f"Monitor {i+1}: {name} ({m['width']}x{m['height']})")
        return result
    
    def get_monitor(self, monitor_id: int) -> Optional[Dict[str, any]]:
        """Get specific monitor by ID"""
        for monitor in self.monitors:
            if monitor["id"] == monitor_id:
                return monitor
        return None
    
    def get_primary_monitor(self) -> Dict[str, any]:
        """Get primary monitor"""
        for monitor in self.monitors:
            if monitor.get("is_primary", False):
                return monitor
        # Fallback to first monitor
        return self.monitors[0] if self.monitors else None
    
    def select_monitor(self, monitor_id: int) -> bool:
        """
        Select monitor for operations
        
        Args:
            monitor_id: Monitor ID (0-based index)
        """
        if self.get_monitor(monitor_id):
            self.selected_monitor = monitor_id
            logger.info(f"Selected monitor {monitor_id}")
            return True
        return False
    
    def select(self, index: int):
        """
        Select monitor (0-based index)
        Alias for select_monitor for compatibility
        """
        return self.select_monitor(index)
    
    def get_selected_monitor(self) -> Dict[str, any]:
        """Get currently selected monitor"""
        return self.get_monitor(self.selected_monitor)
    
    def get_region(self) -> Tuple[int, int, int, int]:
        """
        Get region of selected monitor as (x, y, width, height)
        
        Returns:
            Tuple of (x, y, width, height)
        """
        monitor = self.get_selected_monitor()
        if monitor:
            return (monitor["x"], monitor["y"], monitor["width"], monitor["height"])
        # Fallback to full screen
        import pyautogui
        w, h = pyautogui.size()
        return (0, 0, w, h)
    
    def screenshot(self, monitor_id: Optional[int] = None) -> Optional[Image.Image]:
        """
        Take screenshot of specific monitor or selected monitor
        Alias for take_screenshot for compatibility
        
        Args:
            monitor_id: Optional monitor ID, uses selected if None
        
        Returns:
            PIL Image or None
        """
        return self.take_screenshot(monitor_id=monitor_id)
    
    def take_screenshot(self, monitor_id: Optional[int] = None, all_monitors: bool = False) -> Optional[Image.Image]:
        """
        Take screenshot of specific monitor or all monitors
        
        Args:
            monitor_id: ID of monitor to screenshot (None = selected monitor)
            all_monitors: If True, screenshot all monitors as one image
        
        Returns:
            PIL Image or None
        """
        try:
            if all_monitors:
                # Screenshot entire virtual screen
                screenshot = pyautogui.screenshot()
                logger.info("Took screenshot of all monitors")
                return screenshot
            
            # Get target monitor
            if monitor_id is None:
                monitor = self.get_selected_monitor()
            else:
                monitor = self.get_monitor(monitor_id)
            
            if not monitor:
                logger.error("Monitor not found")
                return None
            
            # Take screenshot of specific region
            screenshot = pyautogui.screenshot(region=(
                monitor["x"],
                monitor["y"],
                monitor["width"],
                monitor["height"]
            ))
            
            logger.info(f"Took screenshot of monitor {monitor['id']}: {monitor['name']}")
            return screenshot
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def get_monitor_info_text(self) -> str:
        """Get formatted text with monitor information"""
        if not self.monitors:
            return "No monitors detected"
        
        lines = [f"Detected {len(self.monitors)} monitor(s):"]
        for monitor in self.monitors:
            primary = " (Primary)" if monitor.get("is_primary") else ""
            selected = " [Selected]" if monitor["id"] == self.selected_monitor else ""
            lines.append(
                f"  Monitor {monitor['id']}: {monitor['name']}{primary}{selected}\n"
                f"    Position: ({monitor['x']}, {monitor['y']})\n"
                f"    Size: {monitor['width']}x{monitor['height']}"
            )
        
        return "\n".join(lines)
