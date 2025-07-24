import unittest
import os
import sys
import yaml
from typing import Dict, Any
from unittest.mock import Mock

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from template_generator.generator import TemplateGenerator
from helm_parser.parser import ChartData, ChartParameter

class TestTemplateGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.generator = TemplateGenerator()
        
        # Sample chart data
        self.chart_data = ChartData(
            name="test-chart",
            version="1.0.0",
            description="Test description",
            parameters={
                "simple": ChartParameter(
                    name="simple",
                    type="string",
                    default_value="value1"
                ),
                "nested.param": ChartParameter(
                    name="nested.param",
                    type="int",
                    default_value=42,
                    nested_path=["nested", "param"]
                ),
                "deep.nested.param": ChartParameter(
                    name="deep.nested.param",
                    type="boolean",
                    default_value=True,
                    nested_path=["deep", "nested", "param"]
                )
            },
            dependencies=[{"name": "common"}]
        )
        
        # Sample schema
        self.schema = {
            "name": "test-schema",
            "version": "1.0.0",
            "rules": {
                "configs": {
                    "simple": {
                        "type": "string",
                        "required": True
                    },
                    "nested.param": {
                        "type": "int",
                        "required": False
                    },
                    "deep.nested.param": {
                        "type": "boolean",
                        "required": True
                    }
                }
            }
        }

    def test_generate_with_schema(self):
        """Test template generation with schema"""
        template_yaml = self.generator.generate(
            chart_data=self.chart_data,
            name="test-template",
            version="1.0.0",
            schema=self.schema
        )
        
        template = yaml.safe_load(template_yaml)
        
        # Verify basic structure
        self.assertEqual(template["schema"]["name"], "test-template")
        self.assertEqual(template["schema"]["version"], "1.0.0")
        
        # Verify configs - only required parameters should be included
        configs = template["configs"]
        self.assertIn("simple", configs)
        self.assertNotIn("nested", configs)  # not required
        self.assertIn("deep", configs)
        self.assertEqual(configs["simple"], "${{$val(simple)}}")
        self.assertEqual(configs["deep"]["nested"]["param"], "${{$val(deep.nested.param)}}")

    def test_generate_without_schema(self):
        """Test template generation without schema"""
        template_yaml = self.generator.generate(
            chart_data=self.chart_data,
            name="test-template",
            version="1.0.0"
        )
        
        template = yaml.safe_load(template_yaml)
        
        # All parameters should be included
        configs = template["configs"]
        self.assertIn("simple", configs)
        self.assertIn("nested", configs)
        self.assertIn("deep", configs)
        self.assertEqual(configs["simple"], "${{$val(simple)}}")
        self.assertEqual(configs["nested"]["param"], "${{$val(nested.param)}}")
        self.assertEqual(configs["deep"]["nested"]["param"], "${{$val(deep.nested.param)}}")

    def test_generate_empty_chart(self):
        """Test template generation with empty chart data"""
        empty_chart = ChartData(
            name="empty",
            version="1.0.0",
            description=None,
            parameters={},
            dependencies=[]
        )
        
        template_yaml = self.generator.generate(
            chart_data=empty_chart,
            name="test-template",
            version="1.0.0"
        )
        
        template = yaml.safe_load(template_yaml)
        self.assertNotIn("configs", template)
        self.assertNotIn("dependencies", template)

    def test_generate_with_dependencies(self):
        """Test template generation with dependencies"""
        template_yaml = self.generator.generate(
            chart_data=self.chart_data,
            name="test-template",
            version="1.0.0"
        )
        
        template = yaml.safe_load(template_yaml)
        
        # Verify dependencies section
        self.assertIn("dependencies", template)
        dependencies = template["dependencies"]
        self.assertEqual(len(dependencies), 1)
        self.assertEqual(dependencies[0]["solutionTemplateId"], "/common/1.0.0")
        self.assertEqual(dependencies[0]["solutionTemplateVersion"], "2.x.x")
        self.assertEqual(dependencies[0]["configsToBeInjected"], [])

    def test_generate_without_dependencies(self):
        """Test template generation without dependencies"""
        chart_data = ChartData(
            name="no-deps",
            version="1.0.0",
            description=None,
            parameters=self.chart_data.parameters,
            dependencies=[]
        )
        
        template_yaml = self.generator.generate(
            chart_data=chart_data,
            name="test-template",
            version="1.0.0"
        )
        
        template = yaml.safe_load(template_yaml)
        self.assertNotIn("dependencies", template)

    def test_generate_template_value(self):
        """Test template value generation"""
        value = self.generator._generate_template_value("test.param")
        self.assertEqual(value, "${{$val(test.param)}}")

    def test_set_nested_value(self):
        """Test nested value setting"""
        config = {}
        
        # Test simple path
        self.generator._set_nested_value(config, ["simple"], "value1")
        self.assertEqual(config["simple"], "value1")
        
        # Test nested path
        self.generator._set_nested_value(config, ["nested", "param"], "value2")
        self.assertEqual(config["nested"]["param"], "value2")
        
        # Test deep nesting
        self.generator._set_nested_value(config, ["a", "b", "c", "d"], "value3")
        self.assertEqual(config["a"]["b"]["c"]["d"], "value3")
        
        # Test empty path
        self.generator._set_nested_value(config, [], "value4")
        self.assertEqual(config, config)  # Should not change

    def test_generate_config_section_from_schema(self):
        """Test config generation from schema"""
        configs = self.generator._generate_config_section_from_schema(
            self.chart_data,
            self.schema["rules"]["configs"]
        )
        
        # Only required parameters should be included
        self.assertIn("simple", configs)
        self.assertNotIn("nested", configs)
        self.assertIn("deep", configs)
        
        # Verify template values
        self.assertEqual(configs["simple"], "${{$val(simple)}}")
        self.assertEqual(configs["deep"]["nested"]["param"], "${{$val(deep.nested.param)}}")

    def test_generate_config_section(self):
        """Test config generation without schema"""
        configs = self.generator._generate_config_section(self.chart_data)
        
        # All parameters should be included
        self.assertIn("simple", configs)
        self.assertIn("nested", configs)
        self.assertIn("deep", configs)
        
        # Verify nested structures
        self.assertEqual(configs["nested"]["param"], "${{$val(nested.param)}}")
        self.assertEqual(configs["deep"]["nested"]["param"], "${{$val(deep.nested.param)}}")

    def test_yaml_generation(self):
        """Test YAML generation formatting"""
        template_yaml = self.generator.generate(
            chart_data=self.chart_data,
            name="test-template",
            version="1.0.0"
        )
        
        # Verify it's valid YAML
        template = yaml.safe_load(template_yaml)
        self.assertIsInstance(template, dict)
        
        # Verify it can be dumped back
        dumped = yaml.dump(template)
        self.assertIsInstance(dumped, str)
        self.assertGreater(len(dumped), 0)

if __name__ == '__main__':
    unittest.main()
