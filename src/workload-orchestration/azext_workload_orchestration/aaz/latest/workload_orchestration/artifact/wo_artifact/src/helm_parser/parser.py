"""
Helm chart parsing module for WO Artifact Generator
"""

import os
import yaml
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from utils.logger import LoggerMixin

@dataclass
class ChartParameter:
    """Data class representing a Helm chart parameter"""
    name: str
    type: str
    default_value: Optional[Any] = None
    description: Optional[str] = None
    required: bool = False
    nested_path: Optional[List[str]] = None
    
@dataclass
class ChartData:
    """Data class representing parsed Helm chart data"""
    name: str
    version: str
    description: Optional[str]
    parameters: Dict[str, ChartParameter]
    dependencies: List[Dict[str, Any]]

class BaseChartParser(ABC, LoggerMixin):
    """Abstract base class for Helm chart parsing"""
    
    def __init__(self, chart_path: str) -> None:
        """
        Initialize the chart parser.
        
        Args:
            chart_path: Path to the Helm chart directory
        """
        super().__init__()
        self.chart_path = chart_path
        self.values_file = os.path.join(chart_path, 'values.yaml')
        self.chart_file = os.path.join(chart_path, 'Chart.yaml')
        
    @abstractmethod
    def parse(self) -> ChartData:
        """
        Parse the Helm chart and extract relevant data.
        
        Returns:
            ChartData object containing parsed information
        """
        pass
    
    def _read_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        Read and parse a YAML file.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Dictionary containing parsed YAML data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If the file is not valid YAML
        """
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"File not found: {file_path}")
                return {}
                
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {}
                
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML file {file_path}: {str(e)}")
            raise

class HelmChartParser(BaseChartParser):
    """Implementation of Helm chart parser"""
    
    def _extract_parameters(self, data: Dict[str, Any], path: List[str] = None) -> Dict[str, ChartParameter]:
        """
        Recursively extract parameters from values.yaml
        
        Args:
            data: Dictionary containing values data
            path: Current path in nested structure
            
        Returns:
            Dictionary mapping parameter names to ChartParameter objects
        """
        if path is None:
            path = []
            
        parameters = {}
        
        for key, value in data.items():
            current_path = path + [key]
            
            if isinstance(value, dict):
                # Recursively process nested dictionaries
                nested_params = self._extract_parameters(value, current_path)
                parameters.update(nested_params)
            else:
                # Create parameter entry
                param_name = '.'.join(current_path)
                param_type = self._infer_type(value)
                
                parameters[param_name] = ChartParameter(
                    name=param_name,
                    type=param_type,
                    default_value=value,
                    nested_path=current_path,
                    required=False  # Will be updated by schema generator
                )
                
        return parameters
    
    def _infer_type(self, value: Any) -> str:
        """
        Infer the type of a parameter value.
        
        Args:
            value: Parameter value
            
        Returns:
            String representing the parameter type
        """
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, list):
            if value:
                element_type = self._infer_type(value[0])
                return f'array[{element_type}]'
            return 'array[string]'  # Default to string array if empty
        else:
            return 'string'
    
    def parse(self) -> ChartData:
        """
        Parse the Helm chart and extract relevant data.
        
        Returns:
            ChartData object containing parsed information
            
        Raises:
            ValueError: If Chart.yaml is missing or invalid
        """
        # Read Chart.yaml
        chart_info = self._read_yaml(self.chart_file)
        if not chart_info:
            raise ValueError(f"Invalid or missing Chart.yaml in {self.chart_path}")
            
        # Read values.yaml (may be empty)
        values = self._read_yaml(self.values_file)
        
        # Extract parameters
        parameters = self._extract_parameters(values)
        
        # Create ChartData object
        return ChartData(
            name=chart_info.get('name', ''),
            version=chart_info.get('version', ''),
            description=chart_info.get('description'),
            parameters=parameters,
            dependencies=chart_info.get('dependencies', [])
        )
