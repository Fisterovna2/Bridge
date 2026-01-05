#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin Manager - Load, unload, and manage plugins
"""

import os
import sys
import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages plugins with hot reload support"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_modules: Dict[str, Any] = {}
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugin files
        
        Returns:
            List of plugin file paths
        """
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return []
        
        plugin_files = []
        
        # Search for .py files
        for file_path in self.plugins_dir.rglob("*.py"):
            # Skip __init__.py and base_plugin.py
            if file_path.name in ["__init__.py", "base_plugin.py", "plugin_manager.py"]:
                continue
            
            plugin_files.append(str(file_path))
        
        logger.info(f"Discovered {len(plugin_files)} plugin files")
        return plugin_files
    
    def load_plugin(self, plugin_path: str) -> bool:
        """
        Load a plugin from file
        
        Args:
            plugin_path: Path to plugin .py file
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            plugin_path = Path(plugin_path)
            
            if not plugin_path.exists():
                logger.error(f"Plugin file not found: {plugin_path}")
                return False
            
            # Generate module name
            module_name = f"plugin_{plugin_path.stem}"
            
            # Load module
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if not spec or not spec.loader:
                logger.error(f"Failed to load plugin spec: {plugin_path}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find plugin class (subclass of BasePlugin)
            plugin_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and 
                    issubclass(obj, BasePlugin) and 
                    obj is not BasePlugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                logger.error(f"No plugin class found in {plugin_path}")
                return False
            
            # Instantiate plugin
            plugin = plugin_class()
            
            # Call on_load
            if plugin.on_load():
                plugin.enabled = True
                self.plugins[plugin.name] = plugin
                self.plugin_modules[plugin.name] = module_name
                logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
                return True
            else:
                logger.error(f"Plugin on_load failed: {plugin.name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}", exc_info=True)
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin
        
        Args:
            plugin_name: Name of plugin to unload
        
        Returns:
            True if unloaded successfully, False otherwise
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin not loaded: {plugin_name}")
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            
            # Call on_unload
            plugin.on_unload()
            
            # Remove from plugins dict
            del self.plugins[plugin_name]
            
            # Remove module
            if plugin_name in self.plugin_modules:
                module_name = self.plugin_modules[plugin_name]
                if module_name in sys.modules:
                    del sys.modules[module_name]
                del self.plugin_modules[plugin_name]
            
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str, plugin_path: str) -> bool:
        """
        Reload a plugin (hot reload)
        
        Args:
            plugin_name: Name of plugin to reload
            plugin_path: Path to plugin file
        
        Returns:
            True if reloaded successfully, False otherwise
        """
        logger.info(f"Reloading plugin: {plugin_name}")
        
        # Unload if already loaded
        if plugin_name in self.plugins:
            self.unload_plugin(plugin_name)
        
        # Load again
        return self.load_plugin(plugin_path)
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get plugin by name"""
        return self.plugins.get(plugin_name)
    
    def get_loaded_plugins(self) -> List[Dict[str, Any]]:
        """Get list of loaded plugins"""
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def execute_action_hooks(self, action: str, context: Dict[str, Any]) -> List[Any]:
        """
        Execute action hooks in all loaded plugins
        
        Args:
            action: Action string
            context: Context dictionary
        
        Returns:
            List of results from plugins
        """
        results = []
        
        for plugin_name, plugin in self.plugins.items():
            if plugin.enabled:
                try:
                    result = plugin.on_action(action, context)
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Plugin {plugin_name} action hook failed: {e}")
        
        return results
    
    def load_all_plugins(self) -> int:
        """
        Load all discovered plugins
        
        Returns:
            Number of plugins loaded successfully
        """
        plugin_files = self.discover_plugins()
        loaded_count = 0
        
        for plugin_path in plugin_files:
            if self.load_plugin(plugin_path):
                loaded_count += 1
        
        logger.info(f"Loaded {loaded_count} of {len(plugin_files)} plugins")
        return loaded_count
    
    def unload_all_plugins(self):
        """Unload all plugins"""
        plugin_names = list(self.plugins.keys())
        
        for plugin_name in plugin_names:
            self.unload_plugin(plugin_name)
        
        logger.info("All plugins unloaded")
