"""
Schema generator module
"""

import yaml
from typing import Dict, Any
import asyncio
from utils.logger import LoggerMixin
from helm_parser.parser import ChartData, ChartParameter
from ai_analyzer.analyzer import AIParameterAnalyzer

class SchemaGenerator(LoggerMixin):
    """Generator for WO schemas from Helm chart data"""
    
    def __init__(self, ai_analyzer: AIParameterAnalyzer):
        """
        Initialize the schema generator.
        
        Args:
            ai_analyzer: AI analyzer instance for parameter analysis
        """
        super().__init__()
        self.ai_analyzer = ai_analyzer
        self._debug_info = {}  # Store additional info for debugging
        
    async def generate(self, chart_data: ChartData, name: str, version: str) -> str:
        """
        Generate WO schema from chart data.
        
        Args:
            chart_data: Parsed chart data
            name: Schema name
            version: Schema version
            
        Returns:
            YAML string containing generated schema
        """
        schema = {
            'name': name,
            'version': version,
            'rules': {
                'configs': {}
            }
        }

        try:
            self.logger.info("Using AI-based parameter analysis")
            analysis_results = await self.ai_analyzer.analyze_parameters(chart_data)
            
            if not analysis_results:
                raise ValueError("AI analyzer returned empty results")
                
            self.logger.info(f"AI analysis returned {len(analysis_results)} parameters")
            
            # Generate schema based on AI analysis
            for param_name, param in chart_data.parameters.items():
                if param_name in analysis_results and analysis_results[param_name]['configurable']:
                    analysis = analysis_results[param_name]
                    param_schema = self._generate_parameter_schema(param, analysis)
                    if param_schema:
                        schema['rules']['configs'][param_name] = param_schema
                        self.logger.debug(f"Added AI-analyzed parameter: {param_name}")
                        # Store additional info for debugging
                        self._store_debug_info(param_name, param, analysis)
            
            # Log analysis statistics
            stats = self.ai_analyzer.get_analysis_stats(analysis_results)
            self.logger.info(f"AI Analysis Stats: {stats}")
            
        except Exception as e:
            self.logger.error(f"Schema generation failed: {str(e)}", exc_info=True)
            raise
        
        # Add metadata if not empty
        if chart_data.description:
            schema['description'] = chart_data.description
            
        # Convert to YAML
        try:
            # Log schema structure for debugging
            self.logger.debug(f"Generated schema structure: {schema.keys()}")
            self.logger.debug(f"Number of configs: {len(schema['rules']['configs'])}")
            
            yaml_str = yaml.dump(schema, sort_keys=False, allow_unicode=True)
            
            # Validate by trying to parse back
            yaml.safe_load(yaml_str)
            
            return yaml_str
            
        except Exception as e:
            self.logger.error(f"Error in schema generation: {str(e)}", exc_info=True)
            raise
    
    def _generate_parameter_schema(self, param: ChartParameter, 
                                 analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate schema for a parameter using AI analysis results.
        
        Args:
            param: Parameter data
            analysis: AI analysis results
            
        Returns:
            Dictionary containing parameter schema
        """
        try:
            # Generate schema with required fields
            return {
                'type': param.type,
                'required': analysis['required'],
                'editableAt': [analysis['edit_level']],
                'editableBy': [analysis['managed_by']]
            }
        except Exception as e:
            self.logger.error(f"Error generating parameter schema for {param.name}: {str(e)}")
            return None
    
    def _store_debug_info(self, param_name: str, param: ChartParameter, 
                         analysis: Dict[str, Any]) -> None:
        """
        Store additional parameter information for debugging.
        
        Args:
            param_name: Name of the parameter
            param: Parameter data
            analysis: AI analysis results
        """
        self._debug_info[param_name] = {
            'defaultValue': param.default_value,
            'description': param.description,
            'required': analysis.get('required', [])
        }
        
    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get stored debug information.
        
        Returns:
            Dictionary containing debug information for parameters
        """
        return self._debug_info
