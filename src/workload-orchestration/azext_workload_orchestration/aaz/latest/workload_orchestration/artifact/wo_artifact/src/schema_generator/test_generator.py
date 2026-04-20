import unittest
import os
import sys
import yaml
import logging
from unittest.mock import patch, Mock, AsyncMock
from typing import Dict, Any

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from schema_generator.generator import SchemaGenerator
from helm_parser.parser import ChartData, ChartParameter
from ai_analyzer.analyzer import AIParameterAnalyzer

class TestSchemaGenerator(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Set up test environment"""
        # Setup logging
        logging.getLogger("SchemaGenerator").setLevel(logging.DEBUG)
        
        # Create mock AI analyzer
        self.mock_analyzer = AsyncMock(spec=AIParameterAnalyzer)
        self.generator = SchemaGenerator(ai_analyzer=self.mock_analyzer)
        
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
                    description="Parameter 1",
                ),
                "param2": ChartParameter(
                    name="param2",
                    type="int",
                    default_value=42,
                    description="Parameter 2",
                    required=True
                )
            },
            dependencies=[]
        )
        
        # Sample analysis results
        self.analysis_results = {
            "param1": {
                "configurable": True,
                "managed_by": "IT",
                "edit_level": "factory",
                "required": True
            },
            "param2": {
                "configurable": False,
                "managed_by": "OT",
                "edit_level": "line",
                "required": False
            }
        }
        
        # Sample stats
        self.stats = {
            "total_parameters": 2,
            "configurable": 1,
            "required": 1,
            "it_managed": 1,
            "ot_managed": 1
        }

    async def test_generate_success(self):
        """Test successful schema generation"""
        # Setup mock analyzer
        self.mock_analyzer.analyze_parameters.return_value = self.analysis_results
        self.mock_analyzer.get_analysis_stats.return_value = self.stats
        
        with self.assertLogs("SchemaGenerator", level='INFO') as log:
            schema_yaml = await self.generator.generate(
                chart_data=self.chart_data,
                name="test-schema",
                version="1.0.0"
            )
            
            # Verify logging
            log_text = "\n".join(log.output)
            self.assertIn("Using AI-based parameter analysis", log_text)
            self.assertIn(f"AI analysis returned {len(self.analysis_results)} parameters", log_text)
            self.assertIn(f"AI Analysis Stats: {self.stats}", log_text)
        
        # Parse generated YAML
        schema = yaml.safe_load(schema_yaml)
        
        # Verify basic structure
        self.assertEqual(schema["name"], "test-schema")
        self.assertEqual(schema["version"], "1.0.0")
        self.assertEqual(schema["description"], "Test description")
        
        # Verify configs
        configs = schema["rules"]["configs"]
        self.assertIn("param1", configs)
        self.assertNotIn("param2", configs)  # Not configurable
        
        # Verify parameter schema
        param1_schema = configs["param1"]
        self.assertEqual(param1_schema["type"], "string")
        self.assertEqual(param1_schema["required"], True)
        self.assertEqual(param1_schema["editableAt"], ["factory"])
        self.assertEqual(param1_schema["editableBy"], ["IT"])

    async def test_generate_empty_analysis(self):
        """Test handling of empty analysis results"""
        self.mock_analyzer.analyze_parameters.return_value = {}
        
        with self.assertLogs("SchemaGenerator", level='ERROR') as log:
            with self.assertRaises(ValueError) as context:
                await self.generator.generate(
                    chart_data=self.chart_data,
                    name="test-schema",
                    version="1.0.0"
                )
            self.assertIn("AI analyzer returned empty results", str(context.exception))
            self.assertIn("Schema generation failed", log.output[0])

    def test_generate_parameter_schema(self):
        """Test parameter schema generation"""
        param = ChartParameter(
            name="test_param",
            type="string",
            default_value="test"
        )
        
        analysis = {
            "configurable": True,
            "managed_by": "IT",
            "edit_level": "factory",
            "required": True
        }
        
        schema = self.generator._generate_parameter_schema(param, analysis)
        
        self.assertEqual(schema["type"], "string")
        self.assertEqual(schema["required"], True)
        self.assertEqual(schema["editableAt"], ["factory"])
        self.assertEqual(schema["editableBy"], ["IT"])

    def test_store_debug_info(self):
        """Test debug info storage"""
        param = ChartParameter(
            name="test_param",
            type="string",
            default_value="test",
            description="Test parameter"
        )
        
        analysis = {
            "configurable": True,
            "required": True
        }
        
        self.generator._store_debug_info("test_param", param, analysis)
        debug_info = self.generator.get_debug_info()
        
        self.assertIn("test_param", debug_info)
        self.assertEqual(debug_info["test_param"]["defaultValue"], "test")
        self.assertEqual(debug_info["test_param"]["description"], "Test parameter")
        self.assertEqual(debug_info["test_param"]["required"], True)

    async def test_generate_yaml_error(self):
        """Test YAML generation error handling"""
        # Mock analyzer to return valid results first
        self.mock_analyzer.analyze_parameters.return_value = self.analysis_results
        self.mock_analyzer.get_analysis_stats.return_value = self.stats

        # Mock yaml.dump to raise an error
        with patch('yaml.dump') as mock_dump:
            mock_dump.side_effect = yaml.YAMLError("Cannot serialize to YAML")
            
            with self.assertLogs("SchemaGenerator", level='ERROR') as log:
                with self.assertRaises(Exception) as context:
                    await self.generator.generate(
                        chart_data=self.chart_data,
                        name="test-schema",
                        version="1.0.0"
                    )
                self.assertIn("Error in schema generation", log.output[-1])
                self.assertIn("Cannot serialize to YAML", str(context.exception))


    async def test_generate_analysis_error(self):
        """Test handling of analyzer errors"""
        error_msg = "Analysis failed"
        self.mock_analyzer.analyze_parameters.side_effect = Exception(error_msg)
        
        with self.assertLogs("SchemaGenerator", level='ERROR') as log:
            with self.assertRaises(Exception) as context:
                await self.generator.generate(
                    chart_data=self.chart_data,
                    name="test-schema",
                    version="1.0.0"
                )
            self.assertEqual(str(context.exception), error_msg)
            self.assertIn("Schema generation failed", log.output[0])

    async def test_generate_invalid_parameter_schema(self):
        """Test handling of invalid parameter schema generation"""
        self.mock_analyzer.analyze_parameters.return_value = {
            "param1": {
                "configurable": True,
                # Missing required fields
            }
        }
        
        with self.assertLogs("SchemaGenerator", level='ERROR') as log:
            schema_yaml = await self.generator.generate(
                chart_data=self.chart_data,
                name="test-schema",
                version="1.0.0"
            )
            schema = yaml.safe_load(schema_yaml)
            self.assertNotIn("param1", schema["rules"]["configs"])
            self.assertIn("Error generating parameter schema", log.output[0])

if __name__ == '__main__':
    unittest.main()
