#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VM Detection Module
Detects if running in a virtual machine environment
Requires at least 2 strong indicators to reduce false positives
"""

import platform
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)


def detect_vm() -> Tuple[bool, str]:
    """
    Determine if running in a VM environment.
    Requires at least 2 STRONG indicators to avoid false positives.
    
    STRONG indicators:
    - BIOS manufacturer: VMware, VirtualBox, QEMU
    - System model: Virtual Machine
    - MAC prefix: 00:0c:29 (VMware), 08:00:27 (VBox)
    - VM processes: vmtoolsd.exe, vboxservice.exe
    
    NOT COUNTED as VM:
    - Windows Insider Preview
    - Hyper-V components on regular Windows
    - WSL
    
    Returns:
        Tuple of (is_vm: bool, reason: str)
    """
    strong_indicators: List[str] = []
    
    # 1. BIOS/System Manufacturer Check
    try:
        if platform.system() == "Windows":
            import subprocess
            
            # Check system manufacturer
            result = subprocess.run(
                ['wmic', 'computersystem', 'get', 'manufacturer'],
                capture_output=True,
                text=True,
                timeout=5
            )
            manufacturer = result.stdout.lower()
            
            vm_manufacturers = ['vmware', 'virtualbox', 'qemu', 'xen', 'microsoft corporation']
            for vm_man in vm_manufacturers:
                if vm_man in manufacturer:
                    # Don't count Microsoft Corporation as it can be physical machines
                    if vm_man == 'microsoft corporation':
                        # Additional check needed
                        continue
                    strong_indicators.append(f"BIOS Manufacturer: {vm_man}")
                    break
            
            # Check system model
            result = subprocess.run(
                ['wmic', 'computersystem', 'get', 'model'],
                capture_output=True,
                text=True,
                timeout=5
            )
            model = result.stdout.lower()
            
            vm_models = ['virtual machine', 'vmware', 'virtualbox', 'qemu']
            for vm_model in vm_models:
                if vm_model in model:
                    strong_indicators.append(f"System Model: {vm_model}")
                    break
                    
    except Exception as e:
        logger.debug(f"Failed to check BIOS/System: {e}")
    
    # 2. MAC Address Check (VM vendor prefixes)
    try:
        import psutil
        
        # Known VM MAC prefixes
        vm_mac_prefixes = [
            '00:0c:29',  # VMware
            '00:50:56',  # VMware
            '08:00:27',  # VirtualBox
            '52:54:00',  # QEMU/KVM
        ]
        
        # Get all network interfaces
        addrs = psutil.net_if_addrs()
        for interface, addr_list in addrs.items():
            for addr in addr_list:
                # Check for MAC address (AF_LINK on Unix, AF_PACKET on Linux)
                if hasattr(psutil, 'AF_LINK') and addr.family == psutil.AF_LINK:
                    mac = addr.address.lower()
                    for prefix in vm_mac_prefixes:
                        if mac.startswith(prefix):
                            strong_indicators.append(f"VM MAC Address: {mac[:8]}... on {interface}")
                            break
    except Exception as e:
        logger.debug(f"Failed to check MAC addresses: {e}")
    
    # 3. VM Process Check
    try:
        import psutil
        
        vm_processes = [
            'vmtoolsd.exe',
            'vmwaretray.exe',
            'vmwareuser.exe',
            'vboxservice.exe',
            'vboxtray.exe',
            'qemu-ga',
        ]
        
        running_processes = [p.name().lower() for p in psutil.process_iter(['name'])]
        found_vm_processes = [p for p in vm_processes if p.lower() in running_processes]
        
        if found_vm_processes:
            strong_indicators.append(f"VM Processes: {', '.join(found_vm_processes[:2])}")
            
    except Exception as e:
        logger.debug(f"Failed to check processes: {e}")
    
    # 4. Registry Check (Windows only)
    if platform.system() == "Windows":
        try:
            import winreg
            
            # Check for VMware Tools
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\VMware, Inc.\VMware Tools"
                )
                winreg.CloseKey(key)
                strong_indicators.append("Registry: VMware Tools installed")
            except FileNotFoundError:
                pass
            
            # Check for VirtualBox Guest Additions
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Oracle\VirtualBox Guest Additions"
                )
                winreg.CloseKey(key)
                strong_indicators.append("Registry: VirtualBox Guest Additions")
            except FileNotFoundError:
                pass
                
        except Exception as e:
            logger.debug(f"Failed to check registry: {e}")
    
    # Determine if VM based on strong indicators (need at least 2)
    is_vm = len(strong_indicators) >= 2
    
    if is_vm:
        reason = "; ".join(strong_indicators)
        logger.info(f"VM Detected: {reason}")
    else:
        if strong_indicators:
            reason = f"Only {len(strong_indicators)} indicator(s) found: {'; '.join(strong_indicators)}"
        else:
            reason = "Physical machine - no VM indicators found"
        logger.info(f"Physical Machine: {reason}")
    
    return is_vm, reason


def is_vm() -> bool:
    """
    Simple boolean check if running in VM.
    
    Returns:
        bool: True if VM, False if physical machine
    """
    detected, _ = detect_vm()
    return detected
