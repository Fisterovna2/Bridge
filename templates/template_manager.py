#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template Manager for Curios Agent
Manages action templates - ready-made automation scenarios
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional


class TemplateManager:
    """Manages action templates"""
    
    def __init__(self, templates_file: str = "templates/default_templates.json"):
        self.templates_file = templates_file
        self.templates = self.load_templates()
    
    def load_templates(self) -> List[Dict]:
        """Load templates from file"""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("templates", [])
        except Exception as e:
            print(f"Failed to load templates: {e}")
        
        return []
    
    def get_template(self, name: str) -> Optional[Dict]:
        """Get template by name"""
        for template in self.templates:
            if template.get("name") == name:
                return template
        return None
    
    def get_all_templates(self) -> List[Dict]:
        """Get all templates"""
        return self.templates
    
    def get_templates_by_category(self, category: str) -> List[Dict]:
        """Get templates by category"""
        return [t for t in self.templates if t.get("category") == category]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        categories = set()
        for template in self.templates:
            if "category" in template:
                categories.add(template["category"])
        return sorted(list(categories))
    
    def execute_template(self, template: Dict) -> str:
        """Convert template to instruction text"""
        if "instruction" in template:
            return template["instruction"]
        elif "actions" in template:
            # Join actions into instruction
            return "\n".join(template["actions"])
        return ""
