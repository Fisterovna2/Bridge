#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Curios Agent v1.0 - AI Desktop Automation Agent
Copyright (c) 2026. All rights reserved.

AI-powered desktop automation agent with computer vision capabilities.
Features multi-mode operation, built-in security, and privacy protection.
"""

import os
import sys
import json
import time
import logging
import platform
import threading
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

try:
    import customtkinter as ctk
    import pyautogui
    import pydirectinput
    import google.generativeai as genai
    from PIL import Image, ImageFilter, ImageDraw
    from tkinter import messagebox, scrolledtext
    import tkinter as tk
except ImportError as e:
    print(f"Error: Missing required dependency - {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

# Import templates
try:
    from templates import TemplateManager
except ImportError:
    print("Warning: Templates module not found")
    TemplateManager = None

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

VERSION = "1.0"
APP_NAME = "Curios Agent"
CONFIG_FILE = "curios_config.json"
LOG_FILE = "agent_system.log"

# Self-protection: files that agent cannot modify
PROTECTED_FILES = [
    "curios_agent.py",
    "curios_config.json", 
    "agent_system.log"
]

# ============================================================================
# ENUMS
# ============================================================================

class OperationMode(Enum):
    """Operation modes for the agent"""
    NORMAL = "NORMAL"  # Safe mode with confirmations (works everywhere)
    FAIR_PLAY = "FAIR_PLAY"  # For games, human-like behavior (VM only)
    CURIOS = "CURIOS"  # Sandbox without restrictions (VM only)

class Language(Enum):
    """Supported languages"""
    EN = "en"
    RU = "ru"

# ============================================================================
# TRANSLATIONS
# ============================================================================

TRANSLATIONS = {
    "en": {
        "app_title": "Curios Agent v1.0",
        "control_panel": "Control Panel",
        "settings": "Settings",
        "logs": "Logs",
        "about": "About",
        "templates": "Templates",
        "prompt": "Enter your instruction:",
        "execute": "Execute",
        "stop": "Stop",
        "clear_logs": "Clear Logs",
        "mode": "Operation Mode:",
        "api_key": "Gemini API Key:",
        "save_settings": "Save Settings",
        "language": "Language:",
        "status": "Status:",
        "idle": "Idle",
        "executing": "Executing...",
        "stopped": "Stopped",
        "about_text": f"{APP_NAME} v{VERSION}\n\nAI-powered desktop automation agent with computer vision.\n\nFeatures:\n- Multi-mode operation\n- Built-in security kernel\n- Privacy protection\n- Vision AI integration\n\nDeveloped with safety in mind.",
        "vm_required": "Error: This mode requires VM environment!",
        "api_key_required": "Please set Gemini API key in Settings",
        "settings_saved": "Settings saved successfully",
        "normal_mode_desc": "Safe mode with confirmations",
        "fair_play_mode_desc": "Human-like behavior (VM only)",
        "curios_mode_desc": "Sandbox mode (VM only)",
        "blocked_action": "Action blocked by SecurityKernel",
        "self_protection": "Cannot modify protected files",
        "confirm_action": "Confirm Action",
        "confirm_message": "Allow this action?",
        "legal_notice_title": "Legal Notice",
        "legal_notice_accept": "I have read and agree",
        "legal_notice_decline": "Decline",
        "eula_title": "End User License Agreement",
        "eula_accept": "I accept the EULA",
        "eula_decline": "Decline",
        "eula_required": "You must accept the EULA to use FAIR_PLAY or CURIOS modes",
        "select_template": "Select a template to run:",
        "run_template": "Run Template",
        "template_category": "Category:",
    },
    "ru": {
        "app_title": "Curios Agent v1.0",
        "control_panel": "Пульт Управления",
        "settings": "Настройки",
        "logs": "Логи",
        "about": "О Программе",
        "templates": "Шаблоны",
        "prompt": "Введите инструкцию:",
        "execute": "Выполнить",
        "stop": "Остановить",
        "clear_logs": "Очистить Логи",
        "mode": "Режим Работы:",
        "api_key": "Gemini API Ключ:",
        "save_settings": "Сохранить Настройки",
        "language": "Язык:",
        "status": "Статус:",
        "idle": "Ожидание",
        "executing": "Выполняется...",
        "stopped": "Остановлено",
        "about_text": f"{APP_NAME} v{VERSION}\n\nAI-агент для автоматизации задач на ПК с компьютерным зрением.\n\nВозможности:\n- Мультирежимная работа\n- Встроенная система безопасности\n- Защита приватности\n- Интеграция Vision AI\n\nРазработан с акцентом на безопасность.",
        "vm_required": "Ошибка: Этот режим требует VM окружение!",
        "api_key_required": "Укажите Gemini API ключ в Настройках",
        "settings_saved": "Настройки успешно сохранены",
        "normal_mode_desc": "Безопасный режим с подтверждениями",
        "fair_play_mode_desc": "Человекоподобное поведение (только VM)",
        "curios_mode_desc": "Песочница без ограничений (только VM)",
        "blocked_action": "Действие заблокировано SecurityKernel",
        "self_protection": "Невозможно изменить защищённые файлы",
        "confirm_action": "Подтверждение Действия",
        "confirm_message": "Разрешить это действие?",
        "legal_notice_title": "Правовое уведомление",
        "legal_notice_accept": "Я прочитал и согласен",
        "legal_notice_decline": "Отклонить",
        "eula_title": "Лицензионное соглашение",
        "eula_accept": "Я принимаю EULA",
        "eula_decline": "Отклонить",
        "eula_required": "Вы должны принять EULA для использования режимов FAIR_PLAY или CURIOS",
        "select_template": "Выберите шаблон для запуска:",
        "run_template": "Запустить шаблон",
        "template_category": "Категория:",
    }
}

# ============================================================================
# SECURITY KERNEL
# ============================================================================

class SecurityKernel:
    """
    Security Kernel - Core security system
    Blocks malicious actions, financial operations, system commands, and private data access
    """
    
    # Triggers for harmful actions
    HARM_TRIGGERS = [
        "delete system32", "rm -rf /", "format c:", "del /f /s /q",
        "shutdown", "reboot", "kill", "pkill", "taskkill",
        "registry", "regedit", "sudo rm", "dd if=/dev/zero",
        "virus", "malware", "ransomware", "exploit", "hack",
        "ddos", "attack", "destroy", "corrupt", "wipe"
    ]
    
    # Triggers for financial operations
    FINANCE_TRIGGERS = [
        "bank", "credit card", "payment", "paypal", "transaction",
        "bitcoin", "crypto", "wallet", "purchase", "buy",
        "money transfer", "wire transfer", "account number",
        "cvv", "pin code", "balance", "withdraw"
    ]
    
    # Triggers for system commands
    SYSTEM_TRIGGERS = [
        "cmd.exe", "powershell", "bash", "terminal", "shell",
        "execute", "run as admin", "sudo", "root",
        "installer", "setup.exe", "modify system"
    ]
    
    # Triggers for private data
    PRIVATE_TRIGGERS = [
        "password", "passwd", "credential", "token", "secret",
        "api key", "private key", "ssh key", "cookie",
        "session", "auth", "login", "email", "phone"
    ]
    
    @staticmethod
    def is_vm() -> bool:
        """Detect if running in VM environment"""
        vm_indicators = [
            "vmware", "virtualbox", "qemu", "xen", "kvm",
            "virtual", "hyperv", "parallels"
        ]
        
        system_info = platform.platform().lower()
        for indicator in vm_indicators:
            if indicator in system_info:
                return True
        
        # Check for VM-specific hardware
        try:
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(
                    ["systeminfo"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                output = result.stdout.lower()
                for indicator in vm_indicators:
                    if indicator in output:
                        return True
        except:
            pass
        
        return False
    
    @staticmethod
    def check_action(action: str, mode: OperationMode) -> Tuple[bool, str]:
        """
        Check if action is allowed
        Returns: (allowed: bool, reason: str)
        """
        action_lower = action.lower()
        
        # Check for protected files (self-protection)
        for protected_file in PROTECTED_FILES:
            if protected_file.lower() in action_lower:
                if any(word in action_lower for word in ["edit", "modify", "delete", "change", "write", "update"]):
                    return False, "Self-protection: Cannot modify protected files"
        
        # Check for harmful actions (all modes)
        for trigger in SecurityKernel.HARM_TRIGGERS:
            if trigger in action_lower:
                return False, f"Blocked harmful action: {trigger}"
        
        # Check for financial operations (all modes)
        for trigger in SecurityKernel.FINANCE_TRIGGERS:
            if trigger in action_lower:
                return False, f"Blocked financial operation: {trigger}"
        
        # Check for system commands in NORMAL mode
        if mode == OperationMode.NORMAL:
            for trigger in SecurityKernel.SYSTEM_TRIGGERS:
                if trigger in action_lower:
                    return False, f"Blocked system command in NORMAL mode: {trigger}"
        
        # VM check for dangerous modes
        if mode in [OperationMode.FAIR_PLAY, OperationMode.CURIOS]:
            if not SecurityKernel.is_vm():
                return False, f"Mode {mode.value} requires VM environment"
        
        return True, "OK"
    
    @staticmethod
    def sanitize_log(message: str) -> str:
        """Sanitize sensitive data from logs"""
        patterns = [
            (r'api[_\s-]?key[_\s:-]*["\']?([a-zA-Z0-9_-]+)["\']?', 'api_key: ***'),
            (r'password[_\s:-]*["\']?([^\s"\']+)["\']?', 'password: ***'),
            (r'token[_\s:-]*["\']?([a-zA-Z0-9_-]+)["\']?', 'token: ***'),
            (r'secret[_\s:-]*["\']?([a-zA-Z0-9_-]+)["\']?', 'secret: ***'),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***'),
            (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '***-***-****'),
        ]
        
        sanitized = message
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized

# ============================================================================
# PRIVACY PROTECTION
# ============================================================================

class PrivacyFilter:
    """Privacy filter for screenshots"""
    
    @staticmethod
    def blur_sensitive_areas(image: Image.Image) -> Image.Image:
        """
        Blur sensitive areas on screenshot
        This is a basic implementation - in production, use ML-based detection
        """
        # Create a copy
        blurred = image.copy()
        
        # For demonstration, blur top-right corner (typically where private info is)
        # In production, use OCR/ML to detect sensitive text
        width, height = blurred.size
        
        # Define regions that might contain sensitive info
        regions = [
            (int(width * 0.7), 0, width, int(height * 0.15)),  # Top-right
        ]
        
        for region in regions:
            # Extract region
            box = region
            region_img = blurred.crop(box)
            
            # Apply blur
            blurred_region = region_img.filter(ImageFilter.GaussianBlur(radius=15))
            
            # Paste back
            blurred.paste(blurred_region, box)
        
        return blurred

# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================

class ConfigManager:
    """Manage application configuration"""
    
    DEFAULT_CONFIG = {
        "mode": OperationMode.NORMAL.value,
        "language": Language.EN.value,
        "api_key": "",
        "mouse_speed": 0.5,
        "typing_speed": 0.1,
        "screenshot_privacy": True,
        "log_sanitization": True,
        "legal_notice_accepted": False,
        "eula_accepted": False,
    }
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults
                    return {**self.DEFAULT_CONFIG, **config}
        except Exception as e:
            logging.warning(f"Failed to load config: {e}")
        
        return self.DEFAULT_CONFIG.copy()
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value

# ============================================================================
# LOGGER SETUP
# ============================================================================

class SanitizedLogger(logging.Logger):
    """Logger with automatic sanitization"""
    
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        # Sanitize message
        if isinstance(msg, str):
            msg = SecurityKernel.sanitize_log(msg)
        
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

# Setup logging
logging.setLoggerClass(SanitizedLogger)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# AGENT CORE
# ============================================================================

class CuriosAgent:
    """Core agent with computer vision and automation capabilities"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.running = False
        self.current_action = None
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Initialize Gemini API
        self._init_gemini()
    
    def _init_gemini(self):
        """Initialize Gemini API"""
        api_key = self.config.get("api_key", "")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini API initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.model = None
        else:
            self.model = None
    
    def take_screenshot(self) -> Optional[Image.Image]:
        """Take screenshot with privacy filter"""
        try:
            screenshot = pyautogui.screenshot()
            
            # Apply privacy filter if enabled
            if self.config.get("screenshot_privacy", True):
                screenshot = PrivacyFilter.blur_sensitive_areas(screenshot)
            
            return screenshot
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def analyze_screen(self, instruction: str) -> Optional[str]:
        """Analyze screen with Vision AI"""
        if not self.model:
            logger.error("Gemini API not initialized")
            return None
        
        try:
            screenshot = self.take_screenshot()
            if not screenshot:
                return None
            
            # Create prompt
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
            
            # Generate response
            response = self.model.generate_content([prompt, screenshot])
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to analyze screen: {e}")
            return None
    
    def execute_action(self, action: str, mode: OperationMode) -> bool:
        """Execute a single action"""
        # Security check
        allowed, reason = SecurityKernel.check_action(action, mode)
        if not allowed:
            logger.warning(f"Action blocked: {reason}")
            return False
        
        try:
            action = action.strip()
            
            # Parse and execute action
            if action.startswith("move_mouse"):
                # Extract coordinates
                match = re.search(r'move_mouse\((\d+),\s*(\d+)\)', action)
                if match:
                    x, y = int(match.group(1)), int(match.group(2))
                    duration = self.config.get("mouse_speed", 0.5)
                    pyautogui.moveTo(x, y, duration=duration)
                    logger.info(f"Moved mouse to ({x}, {y})")
                    return True
            
            elif action.startswith("click"):
                # Extract button
                match = re.search(r"click\(button=['\"](\w+)['\"]\)", action)
                button = match.group(1) if match else 'left'
                pyautogui.click(button=button)
                logger.info(f"Clicked {button} button")
                return True
            
            elif action.startswith("double_click"):
                pyautogui.doubleClick()
                logger.info("Double clicked")
                return True
            
            elif action.startswith("drag"):
                match = re.search(r'drag\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', action)
                if match:
                    x1, y1 = int(match.group(1)), int(match.group(2))
                    x2, y2 = int(match.group(3)), int(match.group(4))
                    duration = self.config.get("mouse_speed", 0.5)
                    pyautogui.moveTo(x1, y1)
                    pyautogui.drag(x2 - x1, y2 - y1, duration=duration)
                    logger.info(f"Dragged from ({x1}, {y1}) to ({x2}, {y2})")
                    return True
            
            elif action.startswith("type_text"):
                match = re.search(r'type_text\(["\'](.+?)["\']\)', action)
                if match:
                    text = match.group(1)
                    interval = self.config.get("typing_speed", 0.1)
                    
                    # Use pydirectinput for games in FAIR_PLAY mode
                    if mode == OperationMode.FAIR_PLAY:
                        # Use pydirectinput.write for text input with human-like timing
                        pydirectinput.write(text, interval=interval)
                    else:
                        pyautogui.write(text, interval=interval)
                    
                    logger.info(f"Typed text: {text[:20]}...")
                    return True
            
            elif action.startswith("press_key"):
                match = re.search(r'press_key\(["\'](.+?)["\']\)', action)
                if match:
                    key = match.group(1)
                    
                    if mode == OperationMode.FAIR_PLAY:
                        pydirectinput.press(key)
                    else:
                        pyautogui.press(key)
                    
                    logger.info(f"Pressed key: {key}")
                    return True
            
            elif action.startswith("hotkey"):
                match = re.search(r'hotkey\(["\'](.+?)["\'],\s*["\'](.+?)["\']\)', action)
                if match:
                    key1, key2 = match.group(1), match.group(2)
                    pyautogui.hotkey(key1, key2)
                    logger.info(f"Pressed hotkey: {key1}+{key2}")
                    return True
            
            elif action.startswith("scroll"):
                match = re.search(r'scroll\((-?\d+)\)', action)
                if match:
                    clicks = int(match.group(1))
                    pyautogui.scroll(clicks)
                    logger.info(f"Scrolled {clicks} clicks")
                    return True
            
            elif action.startswith("wait"):
                match = re.search(r'wait\((\d+(?:\.\d+)?)\)', action)
                if match:
                    seconds = float(match.group(1))
                    time.sleep(seconds)
                    logger.info(f"Waited {seconds} seconds")
                    return True
            
            logger.warning(f"Unknown action: {action}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to execute action: {e}")
            return False
    
    def execute_instruction(self, instruction: str, mode: OperationMode, 
                          confirm_callback=None) -> bool:
        """Execute user instruction"""
        logger.info(f"Executing instruction in {mode.value} mode: {instruction}")
        
        # Security check
        allowed, reason = SecurityKernel.check_action(instruction, mode)
        if not allowed:
            logger.warning(f"Instruction blocked: {reason}")
            return False
        
        # Confirmation in NORMAL mode
        if mode == OperationMode.NORMAL and confirm_callback:
            if not confirm_callback(instruction):
                logger.info("User declined action")
                return False
        
        # Analyze screen and get actions
        self.running = True
        try:
            response = self.analyze_screen(instruction)
            if not response:
                logger.error("Failed to analyze screen")
                return False
            
            logger.info(f"AI Response: {response[:200]}...")
            
            # Extract and execute actions
            lines = response.split('\n')
            for line in lines:
                if not self.running:
                    logger.info("Execution stopped by user")
                    return False
                
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('//'):
                    # Check if line contains an action
                    if any(action in line for action in [
                        'move_mouse', 'click', 'double_click', 'drag',
                        'type_text', 'press_key', 'hotkey', 'scroll', 'wait'
                    ]):
                        if mode == OperationMode.NORMAL and confirm_callback:
                            if not confirm_callback(line):
                                logger.info("User declined action")
                                continue
                        
                        self.execute_action(line, mode)
            
            logger.info("Instruction completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute instruction: {e}")
            return False
        finally:
            self.running = False
    
    def stop(self):
        """Stop current execution"""
        self.running = False
        logger.info("Stopping execution...")

# ============================================================================
# GUI APPLICATION
# ============================================================================

class CuriosAgentGUI:
    """CustomTkinter GUI for Curios Agent"""
    
    def __init__(self):
        # Setup
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Load config
        self.config = ConfigManager()
        self.lang = Language(self.config.get("language", "en"))
        self.t = TRANSLATIONS[self.lang.value]
        
        # Check legal notice acceptance
        if not self.config.get("legal_notice_accepted", False):
            if not self._show_legal_notice():
                # User declined, exit
                sys.exit(0)
        
        # Create agent
        self.agent = CuriosAgent(self.config)
        
        # Initialize template manager
        self.template_manager = TemplateManager() if TemplateManager else None
        
        # Create window
        self.root = ctk.CTk()
        self.root.title(self.t["app_title"])
        self.root.geometry("900x700")
        
        # Create UI
        self._create_ui()
        
        # Status
        self.update_status(self.t["idle"])
        
        logger.info("Curios Agent GUI initialized")
    
    def _create_ui(self):
        """Create user interface"""
        # Create tabview
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tab_control = self.tabview.add(self.t["control_panel"])
        self.tab_settings = self.tabview.add(self.t["settings"])
        self.tab_templates = self.tabview.add(self.t["templates"])
        self.tab_logs = self.tabview.add(self.t["logs"])
        self.tab_about = self.tabview.add(self.t["about"])
        
        # Setup tabs
        self._setup_control_tab()
        self._setup_settings_tab()
        self._setup_templates_tab()
        self._setup_logs_tab()
        self._setup_about_tab()
    
    def _setup_control_tab(self):
        """Setup control panel tab"""
        # Status
        status_frame = ctk.CTkFrame(self.tab_control)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(status_frame, text=self.t["status"], 
                    font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(status_frame, text=self.t["idle"],
                                        font=("Arial", 12))
        self.status_label.pack(side="left", padx=5)
        
        # Prompt
        ctk.CTkLabel(self.tab_control, text=self.t["prompt"],
                    font=("Arial", 14)).pack(pady=10)
        
        self.prompt_text = ctk.CTkTextbox(self.tab_control, height=150)
        self.prompt_text.pack(fill="x", padx=10, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.tab_control)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.execute_btn = ctk.CTkButton(
            button_frame, text=self.t["execute"],
            command=self._on_execute,
            font=("Arial", 14, "bold"),
            height=40
        )
        self.execute_btn.pack(side="left", expand=True, padx=5)
        
        self.stop_btn = ctk.CTkButton(
            button_frame, text=self.t["stop"],
            command=self._on_stop,
            font=("Arial", 14, "bold"),
            height=40,
            fg_color="red",
            hover_color="darkred"
        )
        self.stop_btn.pack(side="left", expand=True, padx=5)
        self.stop_btn.configure(state="disabled")
    
    def _setup_settings_tab(self):
        """Setup settings tab"""
        # Mode
        ctk.CTkLabel(self.tab_settings, text=self.t["mode"],
                    font=("Arial", 12, "bold")).pack(pady=10)
        
        self.mode_var = ctk.StringVar(value=self.config.get("mode"))
        
        modes = [
            (OperationMode.NORMAL.value, self.t["normal_mode_desc"]),
            (OperationMode.FAIR_PLAY.value, self.t["fair_play_mode_desc"]),
            (OperationMode.CURIOS.value, self.t["curios_mode_desc"]),
        ]
        
        for mode_value, description in modes:
            frame = ctk.CTkFrame(self.tab_settings)
            frame.pack(fill="x", padx=10, pady=5)
            
            radio = ctk.CTkRadioButton(
                frame, text=f"{mode_value}", 
                variable=self.mode_var,
                value=mode_value
            )
            radio.pack(side="left", padx=5)
            
            ctk.CTkLabel(frame, text=f"({description})",
                        font=("Arial", 10)).pack(side="left", padx=5)
        
        # Language
        ctk.CTkLabel(self.tab_settings, text=self.t["language"],
                    font=("Arial", 12, "bold")).pack(pady=10)
        
        self.lang_var = ctk.StringVar(value=self.config.get("language"))
        lang_frame = ctk.CTkFrame(self.tab_settings)
        lang_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkRadioButton(lang_frame, text="English", 
                          variable=self.lang_var, value="en").pack(side="left", padx=10)
        ctk.CTkRadioButton(lang_frame, text="Русский",
                          variable=self.lang_var, value="ru").pack(side="left", padx=10)
        
        # API Key
        ctk.CTkLabel(self.tab_settings, text=self.t["api_key"],
                    font=("Arial", 12, "bold")).pack(pady=10)
        
        self.api_key_entry = ctk.CTkEntry(self.tab_settings, width=400,
                                         show="*")
        self.api_key_entry.pack(padx=10, pady=5)
        self.api_key_entry.insert(0, self.config.get("api_key", ""))
        
        # Save button
        ctk.CTkButton(
            self.tab_settings, text=self.t["save_settings"],
            command=self._on_save_settings,
            font=("Arial", 14, "bold"),
            height=40
        ).pack(pady=20)
    
    def _setup_logs_tab(self):
        """Setup logs tab"""
        # Clear button
        ctk.CTkButton(
            self.tab_logs, text=self.t["clear_logs"],
            command=self._on_clear_logs,
            height=30
        ).pack(pady=5)
        
        # Log display
        self.log_text = ctk.CTkTextbox(self.tab_logs)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Load logs
        self._load_logs()
    
    def _setup_about_tab(self):
        """Setup about tab"""
        ctk.CTkLabel(
            self.tab_about, text=self.t["about_text"],
            font=("Arial", 12),
            justify="left"
        ).pack(pady=20, padx=20)
    
    def _on_execute(self):
        """Handle execute button"""
        instruction = self.prompt_text.get("1.0", "end-1c").strip()
        if not instruction:
            return
        
        # Check API key
        if not self.config.get("api_key"):
            self._show_error(self.t["api_key_required"])
            return
        
        # Get mode
        mode = OperationMode(self.mode_var.get())
        
        # Update UI
        self.execute_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.update_status(self.t["executing"])
        
        # Execute in thread
        def execute_thread():
            try:
                self.agent.execute_instruction(
                    instruction, mode,
                    confirm_callback=self._confirm_action
                )
            finally:
                self.root.after(0, self._execution_finished)
        
        thread = threading.Thread(target=execute_thread, daemon=True)
        thread.start()
    
    def _on_stop(self):
        """Handle stop button"""
        self.agent.stop()
        self.update_status(self.t["stopped"])
    
    def _execution_finished(self):
        """Called when execution finishes"""
        self.execute_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.update_status(self.t["idle"])
        self._load_logs()
    
    def _on_save_settings(self):
        """Handle save settings"""
        # Check if mode is changing to FAIR_PLAY or CURIOS
        new_mode = self.mode_var.get()
        if new_mode in [OperationMode.FAIR_PLAY.value, OperationMode.CURIOS.value]:
            # Check if EULA has been accepted
            if not self.config.get("eula_accepted", False):
                if not self._show_eula():
                    # User declined EULA, revert mode to current
                    self.mode_var.set(self.config.get("mode"))
                    self._show_error(self.t["eula_required"])
                    return
        
        self.config.set("mode", self.mode_var.get())
        self.config.set("language", self.lang_var.get())
        self.config.set("api_key", self.api_key_entry.get())
        
        if self.config.save():
            # Reinitialize agent with new API key
            self.agent._init_gemini()
            
            # Update language
            if self.lang_var.get() != self.lang.value:
                self._show_info(self.t["settings_saved"])
                # Would need to restart for full language change
            else:
                self._show_info(self.t["settings_saved"])
        
        self._load_logs()
    
    def _on_clear_logs(self):
        """Clear logs"""
        try:
            open(LOG_FILE, 'w').close()
            self.log_text.delete("1.0", "end")
            logger.info("Logs cleared")
        except Exception as e:
            logger.error(f"Failed to clear logs: {e}")
    
    def _load_logs(self):
        """Load logs into display"""
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    logs = f.read()
                    self.log_text.delete("1.0", "end")
                    self.log_text.insert("1.0", logs)
        except Exception as e:
            logger.error(f"Failed to load logs: {e}")
    
    def _confirm_action(self, action: str) -> bool:
        """Confirmation dialog for actions in NORMAL mode"""
        return messagebox.askyesno(
            self.t["confirm_action"],
            f"{self.t['confirm_message']}\n\n{action}"
        )
    
    def _show_error(self, message: str):
        """Show error message"""
        messagebox.showerror("Error", message)
    
    def _show_info(self, message: str):
        """Show info message"""
        messagebox.showinfo("Info", message)
    
    def update_status(self, status: str):
        """Update status label"""
        self.status_label.configure(text=status)
    
    def _show_legal_notice(self) -> bool:
        """Show legal notice dialog and get acceptance"""
        # Create dialog window
        dialog = ctk.CTkToplevel(None)
        dialog.title(self.t["legal_notice_title"])
        dialog.geometry("800x600")
        dialog.grab_set()
        
        accepted = [False]  # Use list to modify in nested function
        
        # Read legal notice
        legal_text = ""
        try:
            with open("LEGAL_NOTICE.md", "r", encoding="utf-8") as f:
                legal_text = f.read()
        except:
            legal_text = "LEGAL_NOTICE.md not found"
        
        # Text widget
        text_widget = ctk.CTkTextbox(dialog, width=750, height=480)
        text_widget.pack(padx=20, pady=20)
        text_widget.insert("1.0", legal_text)
        text_widget.configure(state="disabled")
        
        # Button frame
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=10)
        
        def on_accept():
            accepted[0] = True
            self.config.set("legal_notice_accepted", True)
            self.config.save()
            dialog.destroy()
        
        def on_decline():
            accepted[0] = False
            dialog.destroy()
        
        ctk.CTkButton(
            button_frame,
            text=self.t["legal_notice_accept"],
            command=on_accept,
            width=200,
            height=40,
            fg_color="green"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text=self.t["legal_notice_decline"],
            command=on_decline,
            width=200,
            height=40,
            fg_color="red"
        ).pack(side="left", padx=10)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return accepted[0]
    
    def _show_eula(self) -> bool:
        """Show EULA dialog and get acceptance"""
        # Create dialog window
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.t["eula_title"])
        dialog.geometry("800x600")
        dialog.grab_set()
        
        accepted = [False]  # Use list to modify in nested function
        
        # Read EULA
        eula_text = ""
        try:
            with open("EULA.md", "r", encoding="utf-8") as f:
                eula_text = f.read()
        except:
            eula_text = "EULA.md not found"
        
        # Text widget
        text_widget = ctk.CTkTextbox(dialog, width=750, height=480)
        text_widget.pack(padx=20, pady=20)
        text_widget.insert("1.0", eula_text)
        text_widget.configure(state="disabled")
        
        # Button frame
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=10)
        
        def on_accept():
            accepted[0] = True
            self.config.set("eula_accepted", True)
            self.config.save()
            dialog.destroy()
        
        def on_decline():
            accepted[0] = False
            dialog.destroy()
        
        ctk.CTkButton(
            button_frame,
            text=self.t["eula_accept"],
            command=on_accept,
            width=200,
            height=40,
            fg_color="green"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text=self.t["eula_decline"],
            command=on_decline,
            width=200,
            height=40,
            fg_color="red"
        ).pack(side="left", padx=10)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return accepted[0]
    
    def _setup_templates_tab(self):
        """Setup templates tab"""
        if not self.template_manager:
            ctk.CTkLabel(
                self.tab_templates,
                text="Templates module not available",
                font=("Arial", 14)
            ).pack(pady=20)
            return
        
        # Title
        ctk.CTkLabel(
            self.tab_templates,
            text=self.t["select_template"],
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Category filter
        category_frame = ctk.CTkFrame(self.tab_templates)
        category_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            category_frame,
            text=self.t["template_category"],
            font=("Arial", 12)
        ).pack(side="left", padx=5)
        
        categories = ["all"] + self.template_manager.get_categories()
        self.template_category_var = ctk.StringVar(value="all")
        
        category_menu = ctk.CTkOptionMenu(
            category_frame,
            variable=self.template_category_var,
            values=categories,
            command=self._on_template_category_change
        )
        category_menu.pack(side="left", padx=5)
        
        # Templates list
        self.templates_frame = ctk.CTkScrollableFrame(self.tab_templates, height=400)
        self.templates_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load templates
        self._load_templates_list()
    
    def _on_template_category_change(self, category: str):
        """Handle category filter change"""
        self._load_templates_list()
    
    def _load_templates_list(self):
        """Load and display templates list"""
        # Clear existing
        for widget in self.templates_frame.winfo_children():
            widget.destroy()
        
        # Get filtered templates
        category = self.template_category_var.get()
        if category == "all":
            templates = self.template_manager.get_all_templates()
        else:
            templates = self.template_manager.get_templates_by_category(category)
        
        # Display templates
        for template in templates:
            frame = ctk.CTkFrame(self.templates_frame)
            frame.pack(fill="x", padx=5, pady=5)
            
            # Get localized name and description
            name_key = f"name_{self.lang.value}"
            desc_key = f"description_{self.lang.value}"
            name = template.get(name_key, template.get("name", "Unknown"))
            description = template.get(desc_key, template.get("description_en", ""))
            
            # Name label
            ctk.CTkLabel(
                frame,
                text=name,
                font=("Arial", 12, "bold")
            ).pack(side="left", padx=5)
            
            # Description label
            ctk.CTkLabel(
                frame,
                text=description,
                font=("Arial", 10)
            ).pack(side="left", padx=5)
            
            # Run button
            ctk.CTkButton(
                frame,
                text=self.t["run_template"],
                command=lambda t=template: self._run_template(t),
                width=120
            ).pack(side="right", padx=5)
    
    def _run_template(self, template: Dict):
        """Run a template"""
        instruction = self.template_manager.execute_template(template)
        
        # Switch to control tab
        self.tabview.set(self.t["control_panel"])
        
        # Set the instruction
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", instruction)
        
        # Execute if API key is set
        if self.config.get("api_key"):
            self._on_execute()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    logger.info(f"Starting {APP_NAME} v{VERSION}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"VM Detected: {SecurityKernel.is_vm()}")
    
    try:
        app = CuriosAgentGUI()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
    finally:
        logger.info("Application terminated")

if __name__ == "__main__":
    main()
