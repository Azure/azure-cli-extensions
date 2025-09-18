# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Tests for AKS Agent parameter parsing and validation.
"""

import unittest


class TestAksAgentParameters(unittest.TestCase):
    """Test AKS Agent parameter parsing and functionality."""

    def test_agent_function_signature_includes_use_aks_mcp(self):
        """Test that the agent function includes use_aks_mcp parameter."""
        import inspect
        from azext_aks_agent.agent.agent import aks_agent
        
        # Get function signature
        sig = inspect.signature(aks_agent)
        
        # Verify use_aks_mcp parameter exists
        self.assertIn("use_aks_mcp", sig.parameters)
        
        # Verify default value is False
        param = sig.parameters["use_aks_mcp"]
        self.assertEqual(param.default, False)

    def test_custom_function_signature_includes_use_aks_mcp(self):
        """Test that the custom.py function includes use_aks_mcp parameter."""
        import inspect
        from azext_aks_agent.custom import aks_agent
        
        # Get function signature
        sig = inspect.signature(aks_agent)
        
        # Verify use_aks_mcp parameter exists
        self.assertIn("use_aks_mcp", sig.parameters)
        
        # Verify default value is False
        param = sig.parameters["use_aks_mcp"]
        self.assertEqual(param.default, False)

    def test_parameter_boolean_type(self):
        """Test that use_aks_mcp parameter behaves as a boolean flag."""
        # Test default value behavior
        import inspect
        from azext_aks_agent.agent.agent import aks_agent
        
        sig = inspect.signature(aks_agent)
        param = sig.parameters["use_aks_mcp"]
        
        # Should have a default value of False
        self.assertIsInstance(param.default, bool)
        self.assertFalse(param.default)

    def test_parameter_docstring_updated(self):
        """Test that the function docstring includes the new parameter."""
        from azext_aks_agent.agent.agent import aks_agent
        
        # Check if docstring mentions the new parameter
        docstring = aks_agent.__doc__
        self.assertIsNotNone(docstring, "Function should have a docstring")
        self.assertIn("use_aks_mcp", docstring, "Docstring should mention use_aks_mcp parameter")
        self.assertIn("MCP", docstring, "Docstring should mention MCP")


if __name__ == '__main__':
    unittest.main()
