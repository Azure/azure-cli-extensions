"""
AI-based parameter analyzer implementation
"""

from dataclasses import asdict
from typing import Dict, List, Any, Optional
import json
from utils.logger import LoggerMixin
from helm_parser.parser import ChartData, ChartParameter
from .client import AzureOpenAIClient

class AIParameterAnalyzer(LoggerMixin):
    """Analyzes Helm chart parameters using Azure OpenAI"""
    
    def __init__(self, endpoint: str, api_key: str, deployment: str, 
                 custom_prompt: Optional[str] = None,
                 hierarchy_levels: Optional[List[str]] = None):
        """
        Initialize the analyzer.
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            deployment: Model deployment name
            custom_prompt: Optional custom system prompt
            hierarchy_levels: Optional list of hierarchy levels
        """
        super().__init__()
        self.ai_client = AzureOpenAIClient(
            endpoint=endpoint,
            api_key=api_key,
            deployment=deployment,
            hierarchy_levels=hierarchy_levels
        )
        self.system_prompt = custom_prompt
        self.hierarchy_levels = hierarchy_levels or ['factory', 'line']
        
    def _build_chart_context(self, chart_data: ChartData) -> Dict[str, Any]:
        """
        Build context information about the chart.
        
        Args:
            chart_data: Parsed chart data
            
        Returns:
            Dictionary containing chart context
        """
        return {
            "name": chart_data.name,
            "version": chart_data.version,
            "description": chart_data.description,
            "dependencies": [dep.get('name') for dep in chart_data.dependencies],
            "application_type": "web_server",
            "deployment_type": "kubernetes",
            "target_environment": "production",
            "hierarchy_levels": self.hierarchy_levels
        }
        
    def _format_parameter(self, param: ChartParameter) -> Dict[str, Any]:
        """
        Format parameter data for AI analysis.
        
        Args:
            param: Chart parameter
            
        Returns:
            Dictionary containing formatted parameter data
        """
        return {
            "name": param.name,
            "type": param.type,
            "default_value": param.default_value,
            "description": param.description,
            "path": ".".join(param.nested_path) if param.nested_path else param.name
        }
        
    async def analyze_parameters(self, chart_data: ChartData) -> Dict[str, Dict[str, Any]]:
        """
        Analyze chart parameters using Azure OpenAI.
        
        Args:
            chart_data: Parsed chart data
            
        Returns:
            Dictionary mapping parameter names to their analysis results
        """
        # Format all parameters for analysis
        formatted_params = [
            self._format_parameter(param)
            for param in chart_data.parameters.values()
        ]
        
        self.logger.info(f"Analyzing {len(formatted_params)} parameters")
        
        # Build context for AI
        chart_context = self._build_chart_context(chart_data)
        
        try:
            # Build prompt from template
            prompt = self.system_prompt.replace('{chart_context}', json.dumps(chart_context, indent=2))
            
            # Get AI analysis
            analysis_results = await self.ai_client.analyze_parameters(
                formatted_params, 
                prompt
            )
            
            # Process and validate results, filtering out non-essential parameters
            validated_results = {}
            for param_name, result in analysis_results.items():
                if (result.get('configurable', False)): # Only include configurable parameters
                    validated_results[param_name] = result
                else:
                    self.logger.debug(f"Filtered out {param_name}: non-essential or invalid")
            
            self.logger.info(f"AI filtering: {len(analysis_results)} -> {len(validated_results)} parameters")
            return validated_results
            
        except Exception as e:
            self.logger.error(f"Parameter analysis failed: {str(e)}")
            raise
           
    def get_analysis_stats(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics about the analysis results.
        
        Args:
            results: Analysis results
            
        Returns:
            Dictionary containing analysis statistics
        """
        stats = {
            'total_parameters': len(results),
            'configurable': 0,
            'required': 0,
            'it_managed': 0,
            'ot_managed': 0,
            'hierarchy_levels': {level: 0 for level in self.hierarchy_levels},
        }
        
        for result in results.values():
            if result['configurable']:
                stats['configurable'] += 1
            if result['required']:    
                stats['required'] += 1
            if result['managed_by'] == 'IT':
                stats['it_managed'] += 1
            if result['managed_by'] == 'OT':
                stats['ot_managed'] += 1
            stats['hierarchy_levels'][result['edit_level']] += 1
                
        return stats
