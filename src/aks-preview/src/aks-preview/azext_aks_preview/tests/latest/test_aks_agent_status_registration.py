# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Tests for AKS Agent Status command registration and functionality.
"""

import unittest
from unittest.mock import Mock, patch


class TestAksAgentStatusCommand(unittest.TestCase):
    """Test AKS Agent Status command registration and functionality."""

    def test_aks_agent_status_function_exists(self):
        """Test that the aks_agent_status function is properly defined."""
        from azext_aks_preview.custom import aks_agent_status
        
        # Verify function exists and is callable
        self.assertTrue(callable(aks_agent_status))

    def test_aks_agent_status_function_signature(self):
        """Test that the aks_agent_status function has correct signature."""
        import inspect
        from azext_aks_preview.custom import aks_agent_status
        
        # Get function signature
        sig = inspect.signature(aks_agent_status)
        
        # Verify required parameters exist
        self.assertIn("cmd", sig.parameters)
        self.assertIn("verbose", sig.parameters)
        
        # Verify verbose default value is False
        verbose_param = sig.parameters["verbose"]
        self.assertEqual(verbose_param.default, False)

    def test_command_registration_imports(self):
        """Test that the command registration imports work correctly."""
        try:
            from azext_aks_preview.custom import aks_agent_status
            from azext_aks_preview.custom import _display_agent_status
            
            # If we can import these functions, the basic registration should work
            self.assertTrue(callable(aks_agent_status))
            self.assertTrue(callable(_display_agent_status))
            
        except ImportError as e:
            self.fail(f"Command registration imports failed: {e}")


if __name__ == '__main__':
    unittest.main()