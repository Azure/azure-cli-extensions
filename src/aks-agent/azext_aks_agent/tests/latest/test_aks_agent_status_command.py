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
        from azext_aks_agent.custom import aks_agent_status
        
        # Verify function exists and is callable
        self.assertTrue(callable(aks_agent_status))

    def test_aks_agent_status_function_signature(self):
        """Test that the aks_agent_status function has correct signature."""
        import inspect
        from azext_aks_agent.custom import aks_agent_status
        
        # Get function signature
        sig = inspect.signature(aks_agent_status)
        
        # Verify required parameters exist
        self.assertIn("cmd", sig.parameters)
        
        # Verify verbose parameter is not present
        self.assertNotIn("verbose", sig.parameters)

    def test_aks_agent_status_basic_execution(self):
        """Test basic execution of aks_agent_status function."""
        from azext_aks_agent.custom import aks_agent_status
        
        # Mock all the imports that happen inside the function
        with patch('azext_aks_agent.agent.binary_manager.AksMcpBinaryManager') as mock_binary_manager_class, \
             patch('azure.cli.core.api.get_config_dir') as mock_get_config_dir, \
             patch('rich.console.Console') as mock_console_class:
            
            # Setup config dir mock
            mock_get_config_dir.return_value = "/mock/config"
            
            # Mock binary manager instance
            mock_binary_instance = Mock()
            mock_binary_instance.is_binary_available.return_value = False
            mock_binary_instance.get_binary_path.return_value = "/mock/binary/path"
            mock_binary_manager_class.return_value = mock_binary_instance
            
            # Mock rich console
            mock_console = Mock()
            mock_console_class.return_value = mock_console
            
            # Mock command context
            mock_cmd = Mock()
            
            # Execute function
            result = aks_agent_status(mock_cmd)
            
            # Verify function completes without error and returns None (status displayed via console)
            self.assertIsNone(result)
            
            # Verify rich console was used
            mock_console_class.assert_called()
            mock_console.print.assert_called()

    def test_aks_agent_status_with_binary_available(self):
        """Test aks_agent_status when MCP binary is available."""
        from azext_aks_agent.custom import aks_agent_status
        
        # Mock all the imports that happen inside the function
        with patch('azext_aks_agent.agent.binary_manager.AksMcpBinaryManager') as mock_binary_manager_class, \
             patch('azext_aks_agent.agent.mcp_manager.MCPManager') as mock_mcp_manager_class, \
             patch('azure.cli.core.api.get_config_dir') as mock_get_config_dir, \
             patch('rich.console.Console') as mock_console_class:
            
            # Setup config dir mock
            mock_get_config_dir.return_value = "/mock/config"
            
            # Mock binary manager with available binary
            mock_binary_instance = Mock()
            mock_binary_instance.is_binary_available.return_value = True
            mock_binary_instance.get_binary_version.return_value = "1.0.0"
            mock_binary_instance.get_binary_path.return_value = "/mock/binary/path"
            mock_binary_instance.validate_version.return_value = True
            mock_binary_manager_class.return_value = mock_binary_instance
            
            # Mock MCP manager
            mock_mcp_instance = Mock()
            mock_mcp_instance.is_server_running.return_value = False
            mock_mcp_instance.is_server_healthy.return_value = False
            mock_mcp_instance.get_server_url.return_value = None
            mock_mcp_instance.get_server_port.return_value = None
            mock_mcp_manager_class.return_value = mock_mcp_instance
            
            # Mock rich console
            mock_console = Mock()
            mock_console_class.return_value = mock_console
            
            mock_cmd = Mock()
            
            result = aks_agent_status(mock_cmd)
            
            # Verify function completes and returns None (status displayed via console)
            self.assertIsNone(result)
            
            # Verify rich console was used
            mock_console_class.assert_called()
            mock_console.print.assert_called()

    def test_aks_agent_status_error_handling(self):
        """Test aks_agent_status error handling with graceful fallback."""
        from azext_aks_agent.custom import aks_agent_status
        
        # Mock to raise exception during config dir access
        with patch('azure.cli.core.api.get_config_dir') as mock_get_config_dir, \
             patch('rich.console.Console') as mock_console_class:
            mock_get_config_dir.side_effect = Exception("Config dir error")
            
            # Mock rich console
            mock_console = Mock()
            mock_console_class.return_value = mock_console
            
            mock_cmd = Mock()
            
            # The function should gracefully handle the error and return None (status displayed via console)
            result = aks_agent_status(mock_cmd)
            
            # Verify function completes without raising CLIError and returns None
            self.assertIsNone(result)
            
            # Verify rich console was used
            mock_console_class.assert_called()
            mock_console.print.assert_called()

    def test_display_agent_status_basic(self):
        """Test _display_agent_status function basic functionality."""
        from azext_aks_agent.custom import _display_agent_status
        
        # Create test status info
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
        
        with patch('rich.console.Console') as mock_console_class:
            # Mock rich console
            mock_console = Mock()
            mock_console_class.return_value = mock_console
            
            _display_agent_status(status_info)
            
            # Verify rich console was used
            mock_console_class.assert_called()
            mock_console.print.assert_called()

    def test_display_agent_status_verbose(self):
        """Test _display_agent_status function with detailed information."""
        from azext_aks_agent.custom import _display_agent_status
        
        # Create test status info with more details
        status_info = {
            "mode": "mcp_ready",
            "mcp_binary": {
                "available": True,
                "path": "/mock/binary/path",
                "version": "1.0.0",
                "version_valid": True
            },
            "server": {
                "running": True,
                "healthy": True,
                "url": "http://localhost:8003/sse",
                "port": 8003
            }
        }
        
        with patch('rich.console.Console') as mock_console_class:
            # Mock rich console
            mock_console = Mock()
            mock_console_class.return_value = mock_console
            
            _display_agent_status(status_info)
            
            # Verify rich console was used
            mock_console_class.assert_called()
            mock_console.print.assert_called()
            
            # Check that print was called multiple times (for table and recommendations)
            self.assertTrue(mock_console.print.call_count >= 2)

    def test_status_command_registration(self):
        """Test that the agent status command is properly registered."""
        # Import functions to verify presence
        try:
            from azext_aks_agent.custom import aks_agent_status
            from azext_aks_agent.custom import _display_agent_status
            
            self.assertTrue(callable(aks_agent_status))
            self.assertTrue(callable(_display_agent_status))
        except ImportError as e:
            self.fail(f"Command registration imports failed: {e}")


if __name__ == '__main__':
    unittest.main()
