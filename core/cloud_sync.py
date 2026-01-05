#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Sync Module - Sync configurations via GitHub Gist
"""

import json
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CloudSync:
    """Cloud synchronization via GitHub Gist"""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize cloud sync
        
        Args:
            github_token: GitHub personal access token with gist scope
        """
        self.github_token = github_token
        self.gist_id = None
        self.api_url = "https://api.github.com"
    
    def is_configured(self) -> bool:
        """Check if cloud sync is configured"""
        return self.github_token is not None
    
    def export_config(self, config: Dict[str, Any]) -> str:
        """
        Export configuration as JSON string
        
        Args:
            config: Configuration dictionary
        
        Returns:
            JSON string
        """
        # Add metadata
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "version": "2.0",
            "config": config
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def import_config(self, json_string: str) -> Optional[Dict[str, Any]]:
        """
        Import configuration from JSON string
        
        Args:
            json_string: JSON string with config
        
        Returns:
            Configuration dictionary or None
        """
        try:
            data = json.loads(json_string)
            
            if "config" in data:
                logger.info(f"Imported config from {data.get('exported_at', 'unknown date')}")
                return data["config"]
            else:
                # Assume raw config format
                logger.info("Imported raw config")
                return data
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config JSON: {e}")
            return None
    
    def backup_to_gist(self, config: Dict[str, Any], gist_description: str = "Curios Agent Config") -> Optional[str]:
        """
        Backup configuration to GitHub Gist
        
        Args:
            config: Configuration to backup
            gist_description: Description for the gist
        
        Returns:
            Gist ID if successful, None otherwise
        """
        if not self.is_configured():
            logger.error("GitHub token not configured")
            return None
        
        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            config_json = self.export_config(config)
            
            # Create or update gist
            gist_data = {
                "description": gist_description,
                "public": False,
                "files": {
                    "curios_config.json": {
                        "content": config_json
                    }
                }
            }
            
            if self.gist_id:
                # Update existing gist
                response = requests.patch(
                    f"{self.api_url}/gists/{self.gist_id}",
                    headers=headers,
                    json=gist_data,
                    timeout=10
                )
            else:
                # Create new gist
                response = requests.post(
                    f"{self.api_url}/gists",
                    headers=headers,
                    json=gist_data,
                    timeout=10
                )
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.gist_id = result["id"]
                logger.info(f"Backed up config to gist: {self.gist_id}")
                return self.gist_id
            else:
                logger.error(f"Failed to backup to gist: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to backup to gist: {e}")
            return None
    
    def restore_from_gist(self, gist_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Restore configuration from GitHub Gist
        
        Args:
            gist_id: Gist ID to restore from (uses stored ID if None)
        
        Returns:
            Configuration dictionary or None
        """
        if not self.is_configured():
            logger.error("GitHub token not configured")
            return None
        
        target_gist_id = gist_id or self.gist_id
        if not target_gist_id:
            logger.error("No gist ID provided")
            return None
        
        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(
                f"{self.api_url}/gists/{target_gist_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Get config file content
                files = result.get("files", {})
                config_file = files.get("curios_config.json")
                
                if config_file:
                    content = config_file.get("content", "")
                    config = self.import_config(content)
                    
                    if config:
                        self.gist_id = target_gist_id
                        logger.info(f"Restored config from gist: {target_gist_id}")
                        return config
                else:
                    logger.error("Config file not found in gist")
                    return None
            else:
                logger.error(f"Failed to restore from gist: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to restore from gist: {e}")
            return None
    
    def list_gists(self) -> list:
        """
        List user's gists
        
        Returns:
            List of gist info dictionaries
        """
        if not self.is_configured():
            logger.error("GitHub token not configured")
            return []
        
        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(
                f"{self.api_url}/gists",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                gists = response.json()
                
                # Filter for Curios Agent configs
                curios_gists = []
                for gist in gists:
                    if "curios_config.json" in gist.get("files", {}):
                        curios_gists.append({
                            "id": gist["id"],
                            "description": gist.get("description", ""),
                            "created_at": gist.get("created_at", ""),
                            "updated_at": gist.get("updated_at", "")
                        })
                
                logger.info(f"Found {len(curios_gists)} Curios Agent config gists")
                return curios_gists
            else:
                logger.error(f"Failed to list gists: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to list gists: {e}")
            return []
