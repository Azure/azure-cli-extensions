import unittest
import os
import sys
import json
from unittest.mock import patch, Mock, AsyncMock
from typing import Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from ai_analyzer.client import AzureOpenAIClient

class TestAzureOpenAIClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Set up test environment"""
        self.endpoint = "https://test.openai.azure.com"
        self.api_key = "test-key"
        self.deployment = "gpt-4"
        self.hierarchy_levels = ["factory", "line", "machine"]
        
        # Create a mock client instance
        self.mock_openai_client = AsyncMock()
        
        with patch('ai_analyzer.client.AsyncAzureOpenAI') as mock_azure:
            mock_azure.return_value = self.mock_openai_client
            self.client = AzureOpenAIClient(
                endpoint=self.endpoint,
                api_key=self.api_key,
                deployment=self.deployment,
                hierarchy_levels=self.hierarchy_levels
            )
        
        # Sample parameters for testing
        self.test_parameters = [
            {
                "name": "param1",
                "type": "string",
                "default_value": "value1",
                "description": "Parameter 1",
                "path": "param1"
            }
        ]
        
        self.test_prompt = "Test prompt"
        
        # Valid response format
        self.valid_response = {
            "param1": {
                "configurable": True,
                "managed_by": "IT",
                "edit_level": "factory",
                "required": True
            }
        }

    def create_mock_response(self, content):
        """Helper method to create mock response"""
        response = Mock()
        if isinstance(content, str):
            response.choices = [Mock(message=Mock(content=content))]
        else:
            response.choices = [Mock(message=Mock(content=json.dumps(content)))]
        return response

    async def test_analyze_parameters_success(self):
        """Test successful parameter analysis"""
        # Set up mock response
        mock_response = self.create_mock_response(self.valid_response)
        self.mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Test successful analysis
        results = await self.client.analyze_parameters(
            self.test_parameters,
            self.test_prompt
        )
        
        # Verify results
        self.assertEqual(len(results), 1)
        self.assertIn("param1", results)
        self.assertTrue(results["param1"]["configurable"])
        self.assertEqual(results["param1"]["managed_by"], "IT")
        self.assertEqual(results["param1"]["edit_level"], "factory")
        self.assertTrue(results["param1"]["required"])
        
        # Verify API call
        self.mock_openai_client.chat.completions.create.assert_called_once()
        call_args = self.mock_openai_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]["model"], self.deployment)
        self.assertEqual(call_args[1]["temperature"], 0.0)

    async def test_analyze_parameters_invalid_response(self):
        """Test handling of invalid API responses"""
        test_cases = [
            # Invalid JSON
            ("invalid json", {}),
            
            # Missing required fields
            ({"param1": {"configurable": True}}, {}),
            
            # Invalid field values
            ({"param1": {
                "configurable": True,
                "managed_by": "INVALID",
                "edit_level": "factory",
                "required": True
            }}, {}),
            
            # Empty response
            ({}, {})
        ]
        
        for content, expected in test_cases:
            mock_response = self.create_mock_response(content)
            self.mock_openai_client.chat.completions.create.return_value = mock_response
            
            results = await self.client.analyze_parameters(
                self.test_parameters,
                self.test_prompt
            )
            self.assertEqual(results, expected)

    async def test_analyze_parameters_retries(self):
        """Test retry mechanism"""
        error_response = AsyncMock(side_effect=Exception("API Error"))
        success_response = self.create_mock_response(self.valid_response)
        
        self.mock_openai_client.chat.completions.create.side_effect = [
            error_response,
            success_response
        ]
        
        results = await self.client.analyze_parameters(
            self.test_parameters,
            self.test_prompt,
            max_retries=2
        )
        
        self.assertIn("param1", results)
        self.assertEqual(self.mock_openai_client.chat.completions.create.call_count, 2)

    def test_validate_parameter_result(self):
        """Test parameter validation"""
        test_cases = [
            # Valid case
            (self.valid_response["param1"], True),
            
            # Missing field
            ({"managed_by": "IT", "edit_level": "factory", "required": True}, False),
            
            # Invalid managed_by
            ({
                "configurable": True,
                "managed_by": "INVALID",
                "edit_level": "factory",
                "required": True
            }, False),
            
            # Invalid edit_level
            ({
                "configurable": True,
                "managed_by": "IT",
                "edit_level": "invalid",
                "required": True
            }, False),
            
            # Invalid type
            ({
                "configurable": "true",  # Should be boolean
                "managed_by": "IT",
                "edit_level": "factory",
                "required": True
            }, False)
        ]
        
        for test_input, expected in test_cases:
            result = self.client._validate_parameter_result(test_input)
            self.assertEqual(result, expected)

    def test_create_response_template(self):
        """Test response template generation"""
        template = self.client._create_response_template()
        
        # Check template contains all required sections
        self.assertIn("Required Format:", template)
        self.assertIn("configurable", template)
        self.assertIn("managed_by", template)
        self.assertIn("edit_level", template)
        self.assertIn("required", template)
        
        # Check hierarchy levels are included
        for level in self.hierarchy_levels:
            self.assertIn(level, template)

if __name__ == '__main__':
    unittest.main()
