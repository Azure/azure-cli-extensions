# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Minimal tests for AKS Agent Status command registration.
"""

import unittest
from unittest.mock import Mock, patch


class TestAksAgentStatusRegistration(unittest.TestCase):
    """Test AKS Agent Status command registration."""

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
        
        # Verify verbose parameter was removed (no longer present to avoid conflicts)
        self.assertNotIn("verbose", sig.parameters)

    def test_display_agent_status_function_exists(self):
        """Test that the _display_agent_status helper function exists."""
        from azext_aks_preview.custom import _display_agent_status
        
        # Verify function exists and is callable
        self.assertTrue(callable(_display_agent_status))

    def test_display_agent_status_signature(self):
        """Test that the _display_agent_status function has correct signature."""
        import inspect
        from azext_aks_preview.custom import _display_agent_status
        
        # Get function signature
        sig = inspect.signature(_display_agent_status)
        
        # Verify required parameters exist
        self.assertIn("status_info", sig.parameters)
        
        # Verify verbose parameter was removed (no longer present to avoid conflicts)
        self.assertNotIn("verbose", sig.parameters)

    @patch('rich.console.Console')
    def test_display_agent_status_basic_output(self, mock_console_class):
        """Test basic output functionality of _display_agent_status."""
        from azext_aks_preview.custom import _display_agent_status
        
        # Create minimal test status info
        status_info = {
            "mode": "traditional",
            "mcp_binary": {
                "available": False,
                "path": "/mock/path",
                "version": None
            },
            "server": {
                "running": False,
                "healthy": False,
                "url": None,
                "port": None
            }
        }
        
        # Mock rich console
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        
        # Call function
        _display_agent_status(status_info)
        
        # Verify rich console was used
        mock_console_class.assert_called()
        mock_console.print.assert_called()


if __name__ == '__main__':
    unittest.main()
