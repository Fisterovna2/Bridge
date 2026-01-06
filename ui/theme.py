#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Dark Theme
Provides color scheme matching GitHub's dark mode
"""


class Theme:
    """GitHub Dark theme colors and styling"""
    
    # Background colors
    BG_PRIMARY = "#0d1117"      # Main background
    BG_SECONDARY = "#161b22"    # Cards, panels
    BG_TERTIARY = "#21262d"     # Inputs, buttons
    BG_HOVER = "#30363d"        # Hover states
    
    # Border colors
    BORDER = "#30363d"          # Default borders
    BORDER_ACTIVE = "#58a6ff"   # Active/focused borders
    BORDER_SUBTLE = "#21262d"   # Subtle dividers
    
    # Text colors
    TEXT_PRIMARY = "#e6edf3"    # Main text
    TEXT_SECONDARY = "#8b949e"  # Secondary text
    TEXT_MUTED = "#6e7681"      # Muted/disabled text
    TEXT_LINK = "#58a6ff"       # Links
    
    # Accent colors
    ACCENT_GREEN = "#238636"    # Success, primary actions
    ACCENT_GREEN_HOVER = "#2ea043"
    ACCENT_BLUE = "#58a6ff"     # Info, links
    ACCENT_BLUE_HOVER = "#79c0ff"
    ACCENT_ORANGE = "#d29922"   # Warnings
    ACCENT_ORANGE_HOVER = "#e0ad3e"
    ACCENT_RED = "#f85149"      # Errors, danger
    ACCENT_RED_HOVER = "#ff7b72"
    ACCENT_PURPLE = "#a371f7"   # Special features
    ACCENT_PURPLE_HOVER = "#b083f0"
    
    # Button colors
    BTN_PRIMARY_BG = "#238636"
    BTN_PRIMARY_HOVER = "#2ea043"
    BTN_PRIMARY_TEXT = "#ffffff"
    
    BTN_SECONDARY_BG = "#21262d"
    BTN_SECONDARY_HOVER = "#30363d"
    BTN_SECONDARY_TEXT = "#e6edf3"
    
    BTN_DANGER_BG = "#da3633"
    BTN_DANGER_HOVER = "#f85149"
    BTN_DANGER_TEXT = "#ffffff"
    
    # Status colors
    STATUS_SUCCESS = "#238636"
    STATUS_WARNING = "#d29922"
    STATUS_ERROR = "#f85149"
    STATUS_INFO = "#58a6ff"
    STATUS_IDLE = "#8b949e"
    
    # Semantic colors for modes
    MODE_NORMAL = "#58a6ff"     # Blue - safe
    MODE_FAIR_PLAY = "#d29922"  # Orange - caution
    MODE_CURIOS = "#f85149"     # Red - danger
    
    @classmethod
    def get_customtkinter_colors(cls) -> dict:
        """
        Get color configuration for CustomTkinter
        
        Returns:
            Dictionary with color mappings for CTk widgets
        """
        return {
            "fg_color": cls.BG_SECONDARY,
            "bg_color": cls.BG_PRIMARY,
            "border_color": cls.BORDER,
            "button_color": cls.BTN_SECONDARY_BG,
            "button_hover_color": cls.BTN_SECONDARY_HOVER,
            "text_color": cls.TEXT_PRIMARY,
            "text_color_disabled": cls.TEXT_MUTED,
        }
    
    @classmethod
    def get_mode_color(cls, mode: str) -> str:
        """
        Get color for operation mode
        
        Args:
            mode: Operation mode name
        
        Returns:
            Color hex string
        """
        mode_colors = {
            "NORMAL": cls.MODE_NORMAL,
            "FAIR_PLAY": cls.MODE_FAIR_PLAY,
            "CURIOS": cls.MODE_CURIOS,
        }
        return mode_colors.get(mode, cls.TEXT_SECONDARY)
    
    @classmethod
    def get_status_color(cls, status: str) -> str:
        """
        Get color for status
        
        Args:
            status: Status name (success, warning, error, info, idle)
        
        Returns:
            Color hex string
        """
        status_colors = {
            "success": cls.STATUS_SUCCESS,
            "warning": cls.STATUS_WARNING,
            "error": cls.STATUS_ERROR,
            "info": cls.STATUS_INFO,
            "idle": cls.STATUS_IDLE,
            "ready": cls.STATUS_SUCCESS,
            "executing": cls.STATUS_INFO,
            "stopped": cls.STATUS_WARNING,
        }
        return status_colors.get(status.lower(), cls.TEXT_SECONDARY)
