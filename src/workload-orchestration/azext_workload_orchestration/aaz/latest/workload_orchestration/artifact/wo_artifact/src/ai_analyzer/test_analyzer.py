import unittest
import os
import sys
from unittest.mock import patch, Mock, AsyncMock
from typing import Dict, Any

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ai_analyzer.analyzer import AIParameterAnalyzer
from helm_parser.parser import ChartData, ChartParameter

class TestAIParameterAnalyzer(unittest.IsolatedAsyncioTestCase):  # Changed to IsolatedAsyncioTestCase
    async def asyncSetUp(self):  # Changed to asyncSetUp
        """Set up test environment"""
        self.endpoint = "https://test.openai.azure.com"
        self.api_key = "test-key"
        self.deployment = "gpt-4"
        self.custom_prompt = "Test prompt with {chart_context}"
        self.hierarchy_levels = ["factory", "line", "machine"]
        
        self.analyzer = AIParameterAnalyzer(
            endpoint=self.endpoint,
            api_key=self.api_key,
            deployment=self.deployment,
            custom_prompt=self.custom_prompt,
            hierarchy_levels=self.hierarchy_levels
        )
        
        # Sample chart data
        self.chart_data = ChartData(
            name="test-chart",
            version="1.0.0",
            description="Test description",
            parameters={
                "param1": ChartParameter(
                    name="param1",
                    type="string",
                    default_value="value1",
                    description="Parameter 1"
                ),
                "param2": ChartParameter(
                    name="param2",
                    type="int",
                    default_value=42,
                    description="Parameter 2",
                    nested_path=["nested", "param2"]
                )
            },
            dependencies=[{"name": "dep1"}]
        )

    async def test_init(self):  # Changed to async
        """Test analyzer initialization"""
        self.assertEqual(self.analyzer.system_prompt, self.custom_prompt)
        self.assertEqual(self.analyzer.hierarchy_levels, self.hierarchy_levels)
        
        # Test default hierarchy levels
        default_analyzer = AIParameterAnalyzer(
            endpoint=self.endpoint,
            api_key=self.api_key,
            deployment=self.deployment
        )
        self.assertEqual(default_analyzer.hierarchy_levels, ['factory', 'line'])

    async def test_build_chart_context(self):  # Changed to async
        """Test chart context building"""
        context = self.analyzer._build_chart_context(self.chart_data)
        
        self.assertEqual(context["name"], "test-chart")
        self.assertEqual(context["version"], "1.0.0")
        self.assertEqual(context["description"], "Test description")
        self.assertEqual(context["dependencies"], ["dep1"])
        self.assertEqual(context["application_type"], "web_server")
        self.assertEqual(context["deployment_type"], "kubernetes")
        self.assertEqual(context["target_environment"], "production")
        self.assertEqual(context["hierarchy_levels"], self.hierarchy_levels)

    async def test_format_parameter(self):  # Changed to async
        """Test parameter formatting"""
        # Test simple parameter
        param1 = self.chart_data.parameters["param1"]
        formatted1 = self.analyzer._format_parameter(param1)
        
        self.assertEqual(formatted1["name"], "param1")
        self.assertEqual(formatted1["type"], "string")
        self.assertEqual(formatted1["default_value"], "value1")
        self.assertEqual(formatted1["description"], "Parameter 1")
        self.assertEqual(formatted1["path"], "param1")
        
        # Test nested parameter
        param2 = self.chart_data.parameters["param2"]
        formatted2 = self.analyzer._format_parameter(param2)
        
        self.assertEqual(formatted2["name"], "param2")
        self.assertEqual(formatted2["path"], "nested.param2")

    @patch('ai_analyzer.analyzer.AIParameterAnalyzer._build_chart_context')
    @patch('ai_analyzer.client.AzureOpenAIClient.analyze_parameters')
    async def test_analyze_parameters_success(self, mock_analyze, mock_context):
        """Test successful parameter analysis"""
        # Mock responses
        mock_context.return_value = {"test": "context"}
        mock_analyze.return_value = {
            "param1": {
                "configurable": True,
                "required": True,
                "managed_by": "IT",
                "edit_level": "factory"
            },
            "param2": {
                "configurable": False,
                "required": False,
                "managed_by": "OT",
                "edit_level": "line"
            }
        }
        
        results = await self.analyzer.analyze_parameters(self.chart_data)
        
        # Only configurable parameters should be included
        self.assertEqual(len(results), 1)
        self.assertIn("param1", results)
        self.assertNotIn("param2", results)

    @patch('ai_analyzer.client.AzureOpenAIClient.analyze_parameters')
    async def test_analyze_parameters_error(self, mock_analyze):
        """Test error handling in parameter analysis"""
        mock_analyze.side_effect = Exception("API Error")
        
        with self.assertRaises(Exception):
            await self.analyzer.analyze_parameters(self.chart_data)

    async def test_get_analysis_stats(self):  # Changed to async
        """Test analysis statistics generation"""
        results = {
            "param1": {
                "configurable": True,
                "required": True,
                "managed_by": "IT",
                "edit_level": "factory"
            },
            "param2": {
                "configurable": True,
                "required": False,
                "managed_by": "OT",
                "edit_level": "line"
            },
            "param3": {
                "configurable": True,
                "required": True,
                "managed_by": "OT",
                "edit_level": "machine"
            }
        }
        
        stats = self.analyzer.get_analysis_stats(results)
        
        self.assertEqual(stats["total_parameters"], 3)
        self.assertEqual(stats["configurable"], 3)
        self.assertEqual(stats["required"], 2)
        self.assertEqual(stats["it_managed"], 1)
        self.assertEqual(stats["ot_managed"], 2)
        self.assertEqual(stats["hierarchy_levels"]["factory"], 1)
        self.assertEqual(stats["hierarchy_levels"]["line"], 1)
        self.assertEqual(stats["hierarchy_levels"]["machine"], 1)

    @patch('ai_analyzer.client.AzureOpenAIClient.analyze_parameters')
    async def test_analyze_empty_parameters(self, mock_analyze):
        """Test analysis with no parameters"""
        empty_chart = ChartData(
            name="empty-chart",
            version="1.0.0",
            description=None,
            parameters={},
            dependencies=[]
        )
        
        mock_analyze.return_value = {}
        results = await self.analyzer.analyze_parameters(empty_chart)
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
