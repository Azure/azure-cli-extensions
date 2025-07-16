import unittest
import os
import sys
import yaml
from unittest.mock import patch, mock_open

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from helm_parser.parser import HelmChartParser, ChartParameter, ChartData

class TestHelmChartParser(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_chart_path = "test_chart"
        self.chart_yaml = {
            "name": "test-chart",
            "version": "1.0.0",
            "description": "Test chart description",
            "dependencies": [
                {"name": "dep1", "version": "1.0.0"},
                {"name": "dep2", "version": "2.0.0"}
            ]
        }
        
        self.values_yaml = {
            "simple": "value",
            "boolean": True,
            "number": 42,
            "float_num": 3.14,
            "array": ["item1", "item2"],
            "nested": {
                "param1": True,
                "param2": 100,
                "deep": {
                    "param3": "value3"
                }
            }
        }
        
        self.parser = HelmChartParser(self.test_chart_path)

    def test_infer_type_boolean(self):
        """Test type inference for boolean values"""
        self.assertEqual(self.parser._infer_type(True), 'boolean')
        self.assertEqual(self.parser._infer_type(False), 'boolean')

    def test_infer_type_integer(self):
        """Test type inference for integer values"""
        self.assertEqual(self.parser._infer_type(42), 'int')
        self.assertEqual(self.parser._infer_type(-17), 'int')
        self.assertEqual(self.parser._infer_type(0), 'int')

    def test_infer_type_float(self):
        """Test type inference for float values"""
        self.assertEqual(self.parser._infer_type(3.14), 'float')
        self.assertEqual(self.parser._infer_type(-2.5), 'float')
        self.assertEqual(self.parser._infer_type(0.0), 'float')

    def test_infer_type_string(self):
        """Test type inference for string values"""
        self.assertEqual(self.parser._infer_type("hello"), 'string')
        self.assertEqual(self.parser._infer_type(""), 'string')
        self.assertEqual(self.parser._infer_type("123"), 'string')

    def test_infer_type_array(self):
        """Test type inference for array values"""
        self.assertEqual(self.parser._infer_type([1, 2, 3]), 'array[int]')
        self.assertEqual(self.parser._infer_type(["a", "b"]), 'array[string]')
        self.assertEqual(self.parser._infer_type([]), 'array[string]')
        self.assertEqual(self.parser._infer_type([True, False]), 'array[boolean]')

    def test_extract_parameters_flat(self):
        """Test parameter extraction for flat structure"""
        flat_values = {
            "param1": "value1",
            "param2": True,
            "param3": 42
        }
        
        params = self.parser._extract_parameters(flat_values)
        
        self.assertEqual(len(params), 3)
        self.assertIn("param1", params)
        self.assertIn("param2", params)
        self.assertIn("param3", params)
        
        self.assertEqual(params["param1"].type, "string")
        self.assertEqual(params["param2"].type, "boolean")
        self.assertEqual(params["param3"].type, "int")

    def test_extract_parameters_nested(self):
        """Test parameter extraction for nested structure"""
        params = self.parser._extract_parameters(self.values_yaml)
        
        self.assertIn("nested.param1", params)
        self.assertIn("nested.deep.param3", params)
        
        nested_param = params["nested.param1"]
        self.assertEqual(nested_param.name, "nested.param1")
        self.assertEqual(nested_param.type, "boolean")
        self.assertEqual(nested_param.nested_path, ["nested", "param1"])
        
        deep_param = params["nested.deep.param3"]
        self.assertEqual(deep_param.name, "nested.deep.param3")
        self.assertEqual(deep_param.type, "string")
        self.assertEqual(deep_param.nested_path, ["nested", "deep", "param3"])

    def test_extract_parameters_empty(self):
        """Test parameter extraction with empty values"""
        params = self.parser._extract_parameters({})
        self.assertEqual(len(params), 0)

    @patch('os.path.exists')
    def test_read_yaml_missing_file(self, mock_exists):
        """Test reading non-existent YAML file"""
        mock_exists.return_value = False
        result = self.parser._read_yaml("nonexistent.yaml")
        self.assertEqual(result, {})

    @patch('builtins.open')
    @patch('os.path.exists')
    def test_read_yaml_empty_file(self, mock_exists, mock_file):
        """Test reading empty YAML file"""
        # Mock file existence
        mock_exists.return_value = True
        
        # Mock empty file
        mock_file_handle = mock_open(read_data="").return_value
        mock_file.return_value = mock_file_handle
        result = self.parser._read_yaml("empty.yaml")
        self.assertEqual(result, {})

    @patch('builtins.open')
    @patch('os.path.exists')
    def test_read_yaml_invalid_yaml(self, mock_exists, mock_file):
        """Test reading invalid YAML file"""
        # Mock file existence
        mock_exists.return_value = True
        
        # Mock file read operation to return invalid YAML
        mock_file_handle = mock_open(read_data="invalid: yaml: :").return_value
        mock_file.return_value = mock_file_handle
        
        # Mock yaml.safe_load to raise YAMLError
        with patch('yaml.safe_load', side_effect=yaml.YAMLError("Invalid YAML")):
            with self.assertRaises(yaml.YAMLError):
                self.parser._read_yaml("invalid.yaml")

    @patch('helm_parser.parser.HelmChartParser._read_yaml')
    def test_parse_complete(self, mock_read_yaml):
        """Test complete chart parsing"""
        mock_read_yaml.side_effect = [
            self.chart_yaml,  # Chart.yaml
            self.values_yaml  # values.yaml
        ]
        
        chart_data = self.parser.parse()
        
        self.assertIsInstance(chart_data, ChartData)
        self.assertEqual(chart_data.name, "test-chart")
        self.assertEqual(chart_data.version, "1.0.0")
        self.assertEqual(chart_data.description, "Test chart description")
        self.assertEqual(len(chart_data.dependencies), 2)
        self.assertTrue(len(chart_data.parameters) > 0)

    @patch('helm_parser.parser.HelmChartParser._read_yaml')
    def test_parse_missing_chart_yaml(self, mock_read_yaml):
        """Test parsing with missing Chart.yaml"""
        mock_read_yaml.side_effect = [{}, {}]  # Empty Chart.yaml and values.yaml
        
        with self.assertRaises(ValueError):
            self.parser.parse()

    @patch('helm_parser.parser.HelmChartParser._read_yaml')
    def test_parse_missing_values_yaml(self, mock_read_yaml):
        """Test parsing with missing values.yaml"""
        mock_read_yaml.side_effect = [
            self.chart_yaml,  # Chart.yaml
            {}  # Empty values.yaml
        ]
        
        chart_data = self.parser.parse()
        self.assertEqual(len(chart_data.parameters), 0)

    def test_parameter_defaults(self):
        """Test ChartParameter default values"""
        param = ChartParameter(name="test", type="string")
        self.assertIsNone(param.default_value)
        self.assertIsNone(param.description)
        self.assertFalse(param.required)
        self.assertIsNone(param.nested_path)

    def test_chart_data_defaults(self):
        """Test ChartData default values"""
        data = ChartData(
            name="test",
            version="1.0.0",
            description=None,
            parameters={},
            dependencies=[]
        )
        self.assertEqual(data.name, "test")
        self.assertEqual(data.version, "1.0.0")
        self.assertIsNone(data.description)
        self.assertEqual(len(data.parameters), 0)
        self.assertEqual(len(data.dependencies), 0)

if __name__ == '__main__':
    unittest.main()
