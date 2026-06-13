"""
Template generator module for WO Artifact Generator
"""

import yaml
from typing import Dict, Any, List, Optional
from utils.logger import LoggerMixin
from helm_parser.parser import ChartData

class TemplateGenerator(LoggerMixin):
    """Generator for WO solution templates from Helm chart data"""
    
    def generate(self, chart_data: ChartData, name: str, version: str, schema: Dict[str, Any] = None) -> str:
        """
        Generate WO solution template from chart data and schema.
        
        Args:
            chart_data: Parsed chart data
            name: Schema name
            version: Schema version
            schema: Generated WO schema (optional)
            
        Returns:
            YAML string containing generated solution template
        """
        # Build template structure
        template = {
            'schema': {
                'name': name,
                'version': version
            }
        }
        
        # Generate configs section using schema-defined parameters if available
        if schema and 'rules' in schema and 'configs' in schema['rules']:
            template['configs'] = self._generate_config_section_from_schema(
                chart_data, 
                schema['rules']['configs']
            )
        elif chart_data.parameters:
            # Fallback to all parameters if no schema
            template['configs'] = self._generate_config_section(chart_data)
        
        # Add dependencies if present
        if chart_data.dependencies:
            template['dependencies'] = self._generate_dependencies_section(chart_data)
        
        # Return formatted YAML
        return yaml.dump(template, sort_keys=False, allow_unicode=True)
    
    def _generate_config_section_from_schema(self, 
                                          chart_data: ChartData,
                                          schema_configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the configs section using schema-defined parameters.
        
        Args:
            chart_data: Parsed chart data
            schema_configs: Schema configuration rules
            
        Returns:
            Dictionary containing the configs section
        """
        configs = {}
        
        # Process only required parameters from schema
        for param_name, param_config in schema_configs.items():
            if param_config.get('required', False):  # Only include if required=True
                if '.' in param_name:
                    path = param_name.split('.')
                    self._set_nested_value(configs, path, self._generate_template_value(param_name))
                else:
                    configs[param_name] = self._generate_template_value(param_name)
        
        return configs
    
    def _generate_config_section(self, chart_data: ChartData) -> Dict[str, Any]:
        """
        Generate the configs section from all chart parameters (fallback).
        
        Args:
            chart_data: Parsed chart data
            
        Returns:
            Dictionary containing the configs section
        """
        configs = {}
        
        # Process each parameter
        for param_name, param in chart_data.parameters.items():
            if param.nested_path:
                # Handle nested parameters
                self._set_nested_value(configs, param.nested_path, 
                                     self._generate_template_value(param_name))
            else:
                # Handle top-level parameters
                configs[param_name] = self._generate_template_value(param_name)
        
        return configs
    
    def _generate_template_value(self, param_name: str) -> str:
        """
        Generate template value following Config Manager Templating Language.
        
        Args:
            param_name: Parameter name
            
        Returns:
            Template value string
        """
        return f"${{{{$val({param_name})}}}}"
    
    def _set_nested_value(
        self,
        config_dict: Dict[str, Any],
        path: List[str],
        value: Any
    ) -> None:
        """
        Set a value in a nested dictionary structure.
        
        Args:
            config_dict: Dictionary to modify
            path: Path to the value location
            value: Value to set
        """
        current = config_dict
        
        # Create nested structure
        for component in path[:-1]:
            if component not in current:
                current[component] = {}
            current = current[component]
        
        # Set the final value
        if path:
            current[path[-1]] = value
    
    def _generate_dependencies_section(self, chart_data: ChartData) -> List[Dict[str, Any]]:
        """
        Generate the dependencies section if chart has dependencies.
        
        Args:
            chart_data: Parsed chart data
            
        Returns:
            List of dependency configurations
        """
        return [{
            'solutionTemplateId': '/common/1.0.0',
            'configsToBeInjected': [],
            'solutionTemplateVersion': '2.x.x'
        }] if chart_data.dependencies else []
