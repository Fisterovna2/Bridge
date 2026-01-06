#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Kernel - Core security system
Blocks malicious actions, financial operations, system commands, and private data access
"""

import re
import platform
import logging
from enum import Enum
from typing import Tuple, Dict, Any
from pathlib import Path
import fnmatch

logger = logging.getLogger(__name__)


class OperationMode(Enum):
    """Operation modes for the agent"""
    NORMAL = "NORMAL"
    FAIR_PLAY = "FAIR_PLAY"
    CURIOS = "CURIOS"


class SecurityKernel:
    """
    Security Kernel - Core security system
    Blocks malicious actions, financial operations, system commands, and private data access
    """
    
    # Protected paths that agent cannot modify
    PROTECTED_PATHS = [
        "curios_agent.py",
        "curios_config.json", 
        "agent_system.log",
        "core/security.py",
        ".env",
        "*.key",
        "*.pem",
        "*.pfx",
        "*.p12",
    ]
    
    # Blocked commands (destructive operations)
    BLOCKED_COMMANDS = [
        # Destructive file operations
        "rm -rf", "rmdir /s", "del /f", "format", 
        "diskpart", "fdisk", "mkfs", "dd if=",
        
        # Registry operations
        "reg delete", "regedit", "reg add",
        
        # System operations
        "shutdown", "restart", "reboot", "taskkill /f",
        "net user", "net localgroup",
        
        # Network operations
        "netsh", "iptables", "firewall-cmd",
    ]
    
    # Triggers for harmful actions
    HARM_TRIGGERS = [
        "delete system32", "rm -rf /", "format c:", "del /f /s /q",
        "shutdown", "reboot", "kill", "pkill", "taskkill",
        "registry", "regedit", "sudo rm", "dd if=/dev/zero",
        "virus", "malware", "ransomware", "exploit", "hack",
        "ddos", "attack", "destroy", "corrupt", "wipe",
        "rm -rf", "rmdir", "deltree", "erase"
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
    def detect_vm() -> Tuple[bool, str]:
        """
        Detect if running in VM environment with improved accuracy
        Returns (is_vm, reason)
        
        Uses the dedicated vm_detection module
        """
        try:
            from core.vm_detection import detect_vm
            return detect_vm()
        except ImportError:
            logger.warning("vm_detection module not available, using fallback")
            # Fallback to simple check
            system_info = platform.platform().lower()
            vm_indicators = ["vmware", "virtualbox", "qemu", "xen", "kvm", "virtual"]
            for indicator in vm_indicators:
                if indicator in system_info:
                    return True, f"Platform string: {indicator}"
            return False, "No VM indicators in platform string"
    
    @staticmethod
    def is_vm() -> bool:
        """Detect if running in VM environment (legacy method)"""
        is_vm_detected, _ = SecurityKernel.detect_vm()
        return is_vm_detected
    
    @staticmethod
    def validate_action(action: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate an action before execution
        
        Args:
            action: Action dictionary with 'type' and parameters
        
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        action_str = str(action)
        return SecurityKernel.check_action(action_str, OperationMode.NORMAL)
    
    @staticmethod
    def is_path_protected(path: str) -> bool:
        """
        Check if a path is protected
        
        Args:
            path: File or directory path to check
        
        Returns:
            bool: True if protected, False otherwise
        """
        path_str = str(path).replace('\\', '/')
        
        for protected in SecurityKernel.PROTECTED_PATHS:
            # Handle wildcards
            if '*' in protected:
                if fnmatch.fnmatch(path_str, protected):
                    return True
                # Also check basename for patterns like *.key
                if fnmatch.fnmatch(Path(path_str).name, protected):
                    return True
            else:
                # Direct match or contains
                protected_normalized = protected.replace('\\', '/')
                if protected_normalized in path_str or path_str.endswith(protected_normalized):
                    return True
        
        return False
    
    @staticmethod
    def check_action(action: str, mode: OperationMode) -> Tuple[bool, str]:
        """
        Check if action is allowed
        Returns: (allowed: bool, reason: str)
        """
        action_lower = action.lower()
        
        # Check for protected files (self-protection)
        for protected_path in SecurityKernel.PROTECTED_PATHS:
            if '*' in protected_path:
                # Skip wildcard patterns in simple string matching
                continue
            if protected_path.lower() in action_lower:
                if any(word in action_lower for word in ["edit", "modify", "delete", "change", "write", "update", "remove"]):
                    return False, f"Self-protection: Cannot modify protected path: {protected_path}"
        
        # Check for blocked commands
        for blocked_cmd in SecurityKernel.BLOCKED_COMMANDS:
            if blocked_cmd.lower() in action_lower:
                return False, f"Blocked dangerous command: {blocked_cmd}"
        
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
        """
        Sanitize sensitive data from logs
        Uses privacy filter if available, otherwise uses internal patterns
        """
        try:
            from core.privacy import sanitize_text
            return sanitize_text(message)
        except ImportError:
            # Fallback to basic patterns
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
    
    @staticmethod
    def sanitize_for_log(text: str) -> str:
        """
        Alias for sanitize_log for compatibility
        
        Args:
            text: Text to sanitize
        
        Returns:
            Sanitized text
        """
        return SecurityKernel.sanitize_log(text)
