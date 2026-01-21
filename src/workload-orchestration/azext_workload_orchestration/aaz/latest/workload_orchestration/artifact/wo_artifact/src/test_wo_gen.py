# src/test_wo_gen.py
import unittest
import asyncio
import os
import shutil
from unittest.mock import patch, Mock, AsyncMock
from argparse import Namespace
import sys

# Add src directory to Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from wo_gen import parse_args, ensure_output_dir, main

class TestWOGen(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = "test_output"
        self.test_args = {
            "chart_path": "./test_chart",
            "output_dir": self.test_dir,
            "schema_name": "test-schema",
            "schema_version": "1.0.0",
            "ai_endpoint": "https://test.openai.azure.com",
            "ai_key": "test-key",
            "ai_model": "gpt-4",
            "verbose": False,
            "prompt": None
        }
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.loop.close()

    def test_parse_args_required(self):
        """Test parsing of required arguments"""
        with patch('sys.argv', [
            'wo_gen.py',
            './test_chart',
            '--schema-name', 'test-schema',
            '--schema-version', '1.0.0',
            '--ai-endpoint', 'https://test.openai.azure.com',
            '--ai-key', 'test-key',
            '--ai-model', 'gpt-4'
        ]):
            args = parse_args()
            self.assertEqual(args.chart_path, './test_chart')
            self.assertEqual(args.schema_name, 'test-schema')
            self.assertEqual(args.schema_version, '1.0.0')
            self.assertEqual(args.ai_endpoint, 'https://test.openai.azure.com')
            self.assertEqual(args.ai_key, 'test-key')
            self.assertEqual(args.ai_model, 'gpt-4')

    def test_parse_args_defaults(self):
        """Test default argument values"""
        with patch('sys.argv', [
            'wo_gen.py',
            './test_chart',
            '--schema-name', 'test-schema',
            '--schema-version', '1.0.0',
            '--ai-endpoint', 'https://test.openai.azure.com',
            '--ai-key', 'test-key',
            '--ai-model', 'gpt-4'
        ]):
            args = parse_args()
            self.assertEqual(args.output_dir, './output')
            self.assertFalse(args.verbose)
            self.assertIsNone(args.prompt)

    def test_ensure_output_dir_new(self):
        """Test creating new output directory"""
        test_dir = os.path.join(self.test_dir, "new_dir")
        self.assertFalse(os.path.exists(test_dir))
        ensure_output_dir(test_dir)
        self.assertTrue(os.path.exists(test_dir))

    def test_ensure_output_dir_existing(self):
        """Test with existing output directory"""
        test_dir = os.path.join(self.test_dir, "existing_dir")
        os.makedirs(test_dir)
        ensure_output_dir(test_dir)
        self.assertTrue(os.path.exists(test_dir))

    @patch('wo_gen.HierarchyManager')
    @patch('wo_gen.PromptManager')
    @patch('wo_gen.AIParameterAnalyzer')
    @patch('wo_gen.HelmChartParser')
    @patch('wo_gen.SchemaGenerator')
    @patch('wo_gen.TemplateGenerator')
    def test_main_workflow(self, mock_template_gen, mock_schema_gen, 
                         mock_parser, mock_analyzer, mock_prompt, 
                         mock_hierarchy):
        """Test main workflow with mocked components"""
        # Setup mocks
        mock_hierarchy_instance = Mock()
        mock_hierarchy_instance.get_hierarchy_levels.return_value = ['factory', 'line']
        mock_hierarchy.return_value = mock_hierarchy_instance

        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt.return_value = "test prompt"
        mock_prompt.return_value = mock_prompt_instance

        mock_parser_instance = Mock()
        mock_parser_instance.parse.return_value = {"test": "data"}
        mock_parser.return_value = mock_parser_instance

        mock_analyzer_instance = Mock()
        mock_analyzer.return_value = mock_analyzer_instance

        # Create async mock for schema generator
        mock_schema_gen_instance = AsyncMock()
        mock_schema_gen_instance.generate.return_value = "test schema"
        mock_schema_gen.return_value = mock_schema_gen_instance

        mock_template_gen_instance = Mock()
        mock_template_gen_instance.generate.return_value = "test template"
        mock_template_gen.return_value = mock_template_gen_instance

        # Create test arguments
        test_args = Namespace(**self.test_args)

        # Run main with mocked arguments
        with patch('wo_gen.parse_args', return_value=test_args):
            self.loop.run_until_complete(main())

        # Verify workflow
        mock_hierarchy_instance.update_hierarchy_levels.assert_called_once()
        mock_prompt_instance.get_prompt.assert_called_once()
        mock_parser_instance.parse.assert_called_once()
        mock_schema_gen_instance.generate.assert_called_once()
        mock_template_gen_instance.generate.assert_called_once()

        # Verify output files
        schema_file = os.path.join(self.test_dir, "test-schema-schema.yaml")
        template_file = os.path.join(self.test_dir, "test-schema-template.yaml")
        self.assertTrue(os.path.exists(schema_file))
        self.assertTrue(os.path.exists(template_file))

    @patch('wo_gen.HierarchyManager')
    @patch('wo_gen.PromptManager')
    def test_main_error_handling(self, mock_prompt, mock_hierarchy):
        """Test error handling in main workflow"""
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt.side_effect = Exception("Test error")
        mock_prompt.return_value = mock_prompt_instance

        test_args = Namespace(**self.test_args)
        with patch('wo_gen.parse_args', return_value=test_args):
            with self.assertRaises(Exception):
                self.loop.run_until_complete(main())

if __name__ == '__main__':
    unittest.main()