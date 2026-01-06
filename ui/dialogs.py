#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialogs Module
Legal Notice and EULA dialogs
"""

import logging
from pathlib import Path
from typing import Optional, Callable

try:
    import customtkinter as ctk
except ImportError:
    ctk = None

from ui.theme import Theme

logger = logging.getLogger(__name__)


class LegalDialog:
    """
    Legal Notice Dialog
    Blocks application startup until accepted
    """
    
    def __init__(self, parent=None, translations: dict = None):
        """
        Initialize Legal Notice dialog
        
        Args:
            parent: Parent window (None for standalone)
            translations: Translation dictionary
        """
        self.parent = parent
        self.translations = translations or {}
        self.accepted = False
    
    def show(self) -> bool:
        """
        Show Legal Notice dialog
        Application will NOT start until accepted
        
        Returns:
            True if accepted, False if declined
        """
        if ctk is None:
            logger.error("CustomTkinter not available")
            return False
        
        # Create toplevel dialog
        if self.parent:
            dialog = ctk.CTkToplevel(self.parent)
        else:
            dialog = ctk.CTk()
            ctk.set_appearance_mode("dark")
        
        dialog.title(self.translations.get("legal_notice_title", "Legal Notice"))
        dialog.geometry("850x650")
        
        # Make modal
        if self.parent:
            dialog.transient(self.parent)
            dialog.grab_set()
        
        # Configure colors
        dialog.configure(fg_color=Theme.BG_PRIMARY)
        
        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text=self.translations.get("legal_notice_title", "Legal Notice"),
            font=("Arial", 20, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title_label.pack(pady=20)
        
        # Read legal notice content
        legal_text = self._load_legal_notice()
        
        # Text widget with scrollbar
        text_widget = ctk.CTkTextbox(
            dialog,
            width=800,
            height=450,
            fg_color=Theme.BG_SECONDARY,
            text_color=Theme.TEXT_PRIMARY,
            border_color=Theme.BORDER,
            border_width=1
        )
        text_widget.pack(padx=20, pady=10)
        text_widget.insert("1.0", legal_text)
        text_widget.configure(state="disabled")
        
        # Button frame
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def on_accept():
            self.accepted = True
            dialog.destroy()
        
        def on_decline():
            self.accepted = False
            dialog.destroy()
        
        # Accept button
        accept_btn = ctk.CTkButton(
            button_frame,
            text=self.translations.get("legal_notice_accept", "I have read and agree"),
            command=on_accept,
            width=220,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color=Theme.BTN_PRIMARY_BG,
            hover_color=Theme.BTN_PRIMARY_HOVER
        )
        accept_btn.pack(side="left", padx=10)
        
        # Decline button
        decline_btn = ctk.CTkButton(
            button_frame,
            text=self.translations.get("legal_notice_decline", "Decline"),
            command=on_decline,
            width=220,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color=Theme.BTN_DANGER_BG,
            hover_color=Theme.BTN_DANGER_HOVER
        )
        decline_btn.pack(side="left", padx=10)
        
        # Wait for dialog to close
        if self.parent:
            dialog.wait_window()
        else:
            dialog.mainloop()
        
        return self.accepted
    
    def _load_legal_notice(self) -> str:
        """Load legal notice from file"""
        legal_file = Path("LEGAL_NOTICE.md")
        try:
            if legal_file.exists():
                return legal_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to load LEGAL_NOTICE.md: {e}")
        
        return """LEGAL NOTICE

This software is provided for educational and research purposes only.

By using this software, you acknowledge and agree that:

1. You are solely responsible for compliance with all applicable laws and regulations
2. The authors are not liable for any misuse or damages
3. This software must not be used for unauthorized access or malicious purposes
4. You will use this software ethically and responsibly

If you do not agree with these terms, you must not use this software.
"""


class EULADialog:
    """
    EULA Dialog for FAIR_PLAY and CURIOS modes
    Required before enabling these modes
    """
    
    def __init__(self, parent, translations: dict = None):
        """
        Initialize EULA dialog
        
        Args:
            parent: Parent window
            translations: Translation dictionary
        """
        self.parent = parent
        self.translations = translations or {}
        self.accepted = False
    
    def show(self) -> bool:
        """
        Show EULA dialog
        FAIR_PLAY and CURIOS modes unavailable without acceptance
        
        Returns:
            True if accepted, False if declined
        """
        if ctk is None:
            logger.error("CustomTkinter not available")
            return False
        
        # Create toplevel dialog
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(self.translations.get("eula_title", "End User License Agreement"))
        dialog.geometry("850x650")
        
        # Make modal
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Configure colors
        dialog.configure(fg_color=Theme.BG_PRIMARY)
        
        # Title
        title_label = ctk.CTkLabel(
            dialog,
            text=self.translations.get("eula_title", "End User License Agreement"),
            font=("Arial", 20, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title_label.pack(pady=20)
        
        # Read EULA content
        eula_text = self._load_eula()
        
        # Text widget
        text_widget = ctk.CTkTextbox(
            dialog,
            width=800,
            height=450,
            fg_color=Theme.BG_SECONDARY,
            text_color=Theme.TEXT_PRIMARY,
            border_color=Theme.BORDER,
            border_width=1
        )
        text_widget.pack(padx=20, pady=10)
        text_widget.insert("1.0", eula_text)
        text_widget.configure(state="disabled")
        
        # Button frame
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def on_accept():
            self.accepted = True
            dialog.destroy()
        
        def on_decline():
            self.accepted = False
            dialog.destroy()
        
        # Accept button
        accept_btn = ctk.CTkButton(
            button_frame,
            text=self.translations.get("eula_accept", "I accept the EULA"),
            command=on_accept,
            width=220,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color=Theme.BTN_PRIMARY_BG,
            hover_color=Theme.BTN_PRIMARY_HOVER
        )
        accept_btn.pack(side="left", padx=10)
        
        # Decline button
        decline_btn = ctk.CTkButton(
            button_frame,
            text=self.translations.get("eula_decline", "Decline"),
            command=on_decline,
            width=220,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color=Theme.BTN_DANGER_BG,
            hover_color=Theme.BTN_DANGER_HOVER
        )
        decline_btn.pack(side="left", padx=10)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return self.accepted
    
    def _load_eula(self) -> str:
        """Load EULA from file"""
        eula_file = Path("EULA.md")
        try:
            if eula_file.exists():
                return eula_file.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to load EULA.md: {e}")
        
        return """END USER LICENSE AGREEMENT (EULA)

For FAIR_PLAY and CURIOS Operation Modes

By accepting this agreement, you acknowledge that:

1. FAIR_PLAY Mode:
   - Designed for game automation with human-like behavior
   - Must only be used in Virtual Machine environments
   - May violate game Terms of Service
   - You are responsible for any consequences

2. CURIOS Mode:
   - Sandbox mode with reduced restrictions
   - Must only be used in Virtual Machine environments
   - Intended for research and testing
   - Not for production use

3. General Terms:
   - You will only use these modes in VM environments
   - You accept all risks and liability
   - Authors are not responsible for misuse
   - You will comply with all applicable laws

If you do not accept these terms, FAIR_PLAY and CURIOS modes will remain disabled.
"""


def show_error_dialog(parent, title: str, message: str):
    """
    Show error dialog
    
    Args:
        parent: Parent window
        title: Dialog title
        message: Error message
    """
    try:
        from tkinter import messagebox
        messagebox.showerror(title, message, parent=parent)
    except Exception as e:
        logger.error(f"Failed to show error dialog: {e}")


def show_info_dialog(parent, title: str, message: str):
    """
    Show info dialog
    
    Args:
        parent: Parent window
        title: Dialog title
        message: Info message
    """
    try:
        from tkinter import messagebox
        messagebox.showinfo(title, message, parent=parent)
    except Exception as e:
        logger.error(f"Failed to show info dialog: {e}")


def show_confirm_dialog(parent, title: str, message: str) -> bool:
    """
    Show confirmation dialog
    
    Args:
        parent: Parent window
        title: Dialog title
        message: Confirmation message
    
    Returns:
        True if confirmed, False otherwise
    """
    try:
        from tkinter import messagebox
        return messagebox.askyesno(title, message, parent=parent)
    except Exception as e:
        logger.error(f"Failed to show confirm dialog: {e}")
        return False
