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
from typing import Tuple

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
    
    # Protected files that agent cannot modify
    PROTECTED_FILES = [
        "curios_agent.py",
        "curios_config.json", 
        "agent_system.log"
    ]
    
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
    def detect_vm() -> Tuple[bool, str]:
        """
        Detect if running in VM environment with improved accuracy
        Returns (is_vm, reason)
        Requires at least 2 indicators to reduce false positives
        """
        indicators = []
        
        # 1. Check SMBIOS/DMI
        try:
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(
                    ['wmic', 'computersystem', 'get', 'model'],
                    capture_output=True, text=True, timeout=5
                )
                model = result.stdout.lower()
                if any(x in model for x in ['virtual', 'vmware', 'virtualbox', 'qemu', 'kvm']):
                    indicators.append(f"SMBIOS: {model.strip()}")
        except:
            pass
        
        # 2. Check MAC address prefixes (VM vendors)
        vm_macs = ['00:0c:29', '00:50:56', '08:00:27', '52:54:00']
        try:
            import psutil
            # Get all network interfaces
            addrs = psutil.net_if_addrs()
            for interface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family == psutil.AF_LINK:  # MAC address
                        mac = addr.address.lower()
                        if any(mac.startswith(prefix) for prefix in vm_macs):
                            indicators.append(f"MAC: {mac[:8]}")
                            break
        except:
            pass
        
        # 3. Check running processes
        vm_processes = ['vmtoolsd.exe', 'vmwaretray.exe', 'vboxservice.exe', 'vboxtray.exe']
        try:
            import psutil
            running = [p.name().lower() for p in psutil.process_iter(['name'])]
            found = [p for p in vm_processes if p in running]
            if found:
                indicators.append(f"Processes: {', '.join(found)}")
        except:
            pass
        
        # 4. Check registry (Windows)
        if platform.system() == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VMware, Inc.\VMware Tools")
                indicators.append("Registry: VMware Tools")
                winreg.CloseKey(key)
            except:
                pass
        
        is_vm = len(indicators) >= 2  # Require at least 2 indicators
        reason = "; ".join(indicators) if indicators else "No VM indicators"
        return is_vm, reason
    
    @staticmethod
    def is_vm() -> bool:
        """Detect if running in VM environment (legacy method)"""
        is_vm_detected, _ = SecurityKernel.detect_vm()
        return is_vm_detected
    
    @staticmethod
    def check_action(action: str, mode: OperationMode) -> Tuple[bool, str]:
        """
        Check if action is allowed
        Returns: (allowed: bool, reason: str)
        """
        action_lower = action.lower()
        
        # Check for protected files (self-protection)
        for protected_file in SecurityKernel.PROTECTED_FILES:
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
