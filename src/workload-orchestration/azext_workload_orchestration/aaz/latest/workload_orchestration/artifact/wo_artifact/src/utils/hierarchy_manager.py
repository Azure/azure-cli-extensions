"""
Hierarchy level manager for WO Artifact Generator
"""

import json
import os
import subprocess
from datetime import datetime
import logging
from typing import List, Optional

class HierarchyManager:
    """Manages hierarchy levels from Azure Edge contexts"""
    
    def __init__(self):
        """Initialize the hierarchy manager"""
        self.hierarchy_file = os.path.join("config", "hierarchy_levels.json")
        self.subscription_id = "973d15c6-6c57-447e-b9c6-6d79b5b784ab"
        self.api_version = "2025-01-01-preview"
        
        # Create config directory if it doesn't exist
        os.makedirs("config", exist_ok=True)
    
    def get_hierarchy_levels(self) -> List[str]:
        """
        Get hierarchy levels from stored file.
        Falls back to ['factory', 'line'] if file doesn't exist.
        
        Returns:
            List of hierarchy level names
        """
        try:
            if os.path.exists(self.hierarchy_file):
                with open(self.hierarchy_file, 'r') as f:
                    data = json.load(f)
                    levels = data.get('levels', [])
                    # Extract level names from response format
                    if isinstance(levels, list):
                        if levels and isinstance(levels[0], dict):
                            # Extract name field if levels are objects
                            return [level.get('name', '').lower() for level in levels if level.get('name')]
                        else:
                            # Use level strings directly
                            return [str(level).lower() for level in levels]
        except Exception as e:
            logging.warning(f"Failed to read hierarchy levels: {e}")
        
        return ['factory', 'line']
    
    def update_hierarchy_levels(self) -> None:
        """
        Update hierarchy levels by querying Azure Edge contexts.
        Stores results in hierarchy_file.
        """
        try:
            # Get contexts
            context_cmd = (
                f"az rest --method get "
                f"--url https://management.azure.com/subscriptions/{self.subscription_id}"
                f"/providers/microsoft.edge/contexts?api-version={self.api_version}"
            )
            
            # Run context command
            context_result = subprocess.run(
                context_cmd,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if context_result.returncode != 0:
                raise Exception(f"Context command failed: {context_result.stderr}")
            
            # Parse context JSON
            context_json = json.loads(context_result.stdout)
            
            # Get hierarchies from first context
            if not context_json.get('value'):
                raise Exception("No contexts found in response")
                
            hierarchies = context_json['value'][0]['properties'].get('hierarchies', [])
            
            # Store hierarchies with timestamp
            data = {
                'levels': hierarchies,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            with open(self.hierarchy_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logging.info(f"Updated hierarchy levels: {hierarchies}")
            
        except Exception as e:
            logging.error(f"Failed to update hierarchy levels: {e}")
            # Don't update file on error to preserve last good state
