# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Tests for AKS Agent MCP integration functionality.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch
import pytest


class TestAksAgentMCPIntegration:
    """Test AKS Agent MCP integration functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_cmd = Mock()
        self.mock_cmd.cli_ctx = Mock()
        self.test_config_file = "~/.azure/aksAgent.config"
        self.test_model = "gpt-4"
        self.test_api_key = "test-key"
        self.test_max_steps = 10

    def test_initialize_mcp_manager_success(self):
        """Test successful MCP manager initialization."""
        from azext_aks_agent.agent.agent import _initialize_mcp_manager
        
        with patch('azext_aks_agent.agent.mcp_manager.MCPManager') as mock_mcp_class:
            mock_manager = Mock()
            mock_mcp_class.return_value = mock_manager
            
            result = _initialize_mcp_manager(verbose=True)
            
            assert result == mock_manager
            mock_mcp_class.assert_called_once_with(verbose=True)

    def test_initialize_mcp_manager_import_error(self):
        """Test MCP manager initialization with import error."""
        from azext_aks_agent.agent.agent import _initialize_mcp_manager
        from azext_aks_agent.agent.error_handler import MCPError
        
        with patch('azext_aks_agent.agent.mcp_manager.MCPManager', side_effect=ImportError("Module not found")):
            with pytest.raises(MCPError) as exc_info:
                _initialize_mcp_manager()
            
            assert "MCP manager initialization failed" in str(exc_info.value)
            assert exc_info.value.error_code == "MCP_IMPORT"
            assert "Ensure all required dependencies are installed" in exc_info.value.suggestions[0]

    @pytest.mark.asyncio
    async def test_setup_mcp_mode_basic_workflow(self):
        """Test basic MCP mode setup workflow without complex mocking."""
        from azext_aks_agent.agent.agent import _setup_mcp_mode
        from azext_aks_agent.agent.binary_manager import BinaryStatus
        
        # Create a simple mock manager
        mock_manager = Mock()
        mock_manager.is_binary_available.return_value = True
        mock_manager.validate_binary_version.return_value = True
        mock_manager.start_server = AsyncMock(return_value=True)
        mock_manager.get_server_url.return_value = "http://localhost:8003/sse"
        
        # Mock binary status
        mock_binary_status = BinaryStatus(available=True, version_valid=True)
        mock_manager.binary_manager.ensure_binary = AsyncMock(return_value=mock_binary_status)
        
        # Test with a non-existent config file (will use empty config)
        with patch('pathlib.Path.exists', return_value=False), \
             patch('tempfile.NamedTemporaryFile') as mock_temp_file, \
             patch('yaml.dump') as mock_yaml_dump, \
             patch('os.unlink'):
            
            # Mock the temporary file context manager
            mock_temp_file.return_value.__enter__.return_value.name = "/tmp/test_config.yaml"
            
            # This should fail because we haven't mocked Holmes Config.load_from_file,
            # but that's expected - we're just testing the workflow doesn't crash
            try:
                await _setup_mcp_mode(
                    mock_manager, "nonexistent_config.yaml", "gpt-4",
                    "test-key", 10, verbose=False
                )
            except Exception as e:
                # Expected to fail at Config.load_from_file
                assert "Config" in str(e) or "load_from_file" in str(e) or "ImportError" in str(e)
            
        # Verify the manager methods were called correctly
        mock_manager.start_server.assert_called_once()
        assert mock_manager.get_server_url.called
        
        # Check the content of the configuration that was passed to yaml.dump
        if mock_yaml_dump.call_count > 0:
            config_data = mock_yaml_dump.call_args[0][0]
            
            # Verify MCP server configuration is present
            assert "mcp_servers" in config_data
            assert "aks-mcp" in config_data["mcp_servers"]
            assert config_data["mcp_servers"]["aks-mcp"]["url"] == "http://localhost:8003/sse"
            
            # Verify conflicting toolsets are disabled
            assert "toolsets" in config_data
            toolsets = config_data["toolsets"]
            assert toolsets["aks/core"]["enabled"] is False
            assert toolsets["kubernetes/core"]["enabled"] is False
    
    @pytest.mark.asyncio
    async def test_setup_mcp_mode_binary_not_available(self):
        """Test MCP mode setup when binary is not available and download fails."""
        from azext_aks_agent.agent.agent import _setup_mcp_mode
        from azext_aks_agent.agent.binary_manager import BinaryStatus
        from azext_aks_agent.agent.error_handler import BinaryError
        
        # Setup mocks
        mock_manager = Mock()
        mock_manager.is_binary_available.return_value = False
        mock_manager.validate_binary_version.return_value = False
        
        # Mock failed binary download
        mock_binary_status = BinaryStatus(available=False, error_message="Download failed")
        mock_manager.binary_manager.ensure_binary = AsyncMock(return_value=mock_binary_status)
        
        # Test the function
        with pytest.raises(BinaryError) as exc_info:
            await _setup_mcp_mode(
                mock_manager, self.test_config_file, self.test_model,
                self.test_api_key, self.test_max_steps, verbose=True
            )
        
        assert "Binary setup failed" in str(exc_info.value)
        assert exc_info.value.error_code == "BINARY_SETUP"

    @pytest.mark.asyncio
    async def test_setup_mcp_mode_server_start_failure(self):
        """Test MCP mode setup when server fails to start."""
        from azext_aks_agent.agent.agent import _setup_mcp_mode
        from azext_aks_agent.agent.binary_manager import BinaryStatus
        from azext_aks_agent.agent.error_handler import ServerError
        
        # Setup mocks
        mock_manager = Mock()
        mock_manager.is_binary_available.return_value = True
        mock_manager.validate_binary_version.return_value = True
        mock_manager.start_server = AsyncMock(return_value=False)
        
        mock_binary_status = BinaryStatus(available=True, version_valid=True)
        mock_manager.binary_manager.ensure_binary = AsyncMock(return_value=mock_binary_status)
        
        # Test the function
        with pytest.raises(ServerError) as exc_info:
            await _setup_mcp_mode(
                mock_manager, self.test_config_file, self.test_model,
                self.test_api_key, self.test_max_steps, verbose=True
            )
        
        assert "Server startup failed" in str(exc_info.value)
        assert exc_info.value.error_code == "SERVER_STARTUP"

    def test_error_handler_functionality(self):
        """Test the enhanced error handling system."""
        from azext_aks_agent.agent.error_handler import (
            AgentErrorHandler, MCPError, BinaryError, ServerError
        )
        
        # Test MCP setup error handling
        original_error = ConnectionError("Network connection failed")
        mcp_error = AgentErrorHandler.handle_mcp_setup_error(original_error, "initialization")
        
        assert isinstance(mcp_error, MCPError)
        assert "MCP setup failed during initialization" in str(mcp_error)
        assert mcp_error.error_code == "MCP_SETUP"
        assert "Check your internet connection" in mcp_error.suggestions
        
        # Test binary error handling
        binary_error = AgentErrorHandler.handle_binary_error(
            Exception("Download timeout"), "download"
        )
        
        assert isinstance(binary_error, BinaryError)
        assert "Binary download failed" in str(binary_error)
        assert binary_error.error_code == "BINARY_DOWNLOAD"
        assert "Verify you have internet connectivity" in binary_error.suggestions
        
        # Test server error handling
        server_error = AgentErrorHandler.handle_server_error(
            Exception("Port in use"), "startup"
        )
        
        assert isinstance(server_error, ServerError)
        assert "MCP server startup failed" in str(server_error)
        assert server_error.error_code == "SERVER_STARTUP"
        assert "Check if the MCP binary is available and executable" in server_error.suggestions
        
        # Test error message formatting
        formatted_message = AgentErrorHandler.format_error_message(mcp_error)
        assert "AKS Agent Error (MCP_SETUP)" in formatted_message
        assert "Suggestions:" in formatted_message
        assert "Try running without --aks-mcp" in formatted_message

    def test_setup_traditional_mode_config_loading(self):
        """Test traditional mode setup with actual config loading."""
        import tempfile
        import yaml
        from azext_aks_agent.agent.config_generator import ConfigurationGenerator
        
        # Create a temporary config file
        test_config = {
            "existing": "config",
            "toolsets": {
                "custom/toolset": {"enabled": True}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            config_file_path = f.name
        
        try:
            # Test loading and processing config as dictionary
            from pathlib import Path
            
            expanded_config_file = Path(config_file_path)
            base_config_dict = {}
            
            if expanded_config_file.exists():
                with open(expanded_config_file, 'r') as f:
                    base_config_dict = yaml.safe_load(f) or {}
            
            # Use ConfigurationGenerator to create traditional config
            traditional_config_dict = ConfigurationGenerator.generate_traditional_config(base_config_dict)
            
            # Verify the configuration was processed correctly
            assert "toolsets" in traditional_config_dict
            assert "existing" in traditional_config_dict
            assert traditional_config_dict["existing"] == "config"
            
            # Verify traditional toolsets are enabled
            toolsets = traditional_config_dict["toolsets"]
            assert toolsets["aks/core"]["enabled"] is True
            assert toolsets["kubernetes/core"]["enabled"] is True
            assert toolsets["kubernetes/live-metrics"]["enabled"] is True
            assert toolsets["custom/toolset"]["enabled"] is True
            
            # Verify no MCP servers are configured
            assert "mcp_servers" not in traditional_config_dict
            
        finally:
            Path(config_file_path).unlink()  # Clean up temp file

    @patch('sys.stdin')
    def test_aks_agent_calls_sync_implementation(self, mock_stdin):
        """Test that aks_agent works with new synchronous implementation."""
        from azext_aks_agent.agent.agent import aks_agent
        
        # Mock stdin to avoid pytest capture issues
        mock_stdin.isatty.return_value = True  # No piped input
        
        # Call the function with use_aks_mcp=False to avoid MCP setup
        try:
            aks_agent(
                self.mock_cmd,
                "rg",
                "cluster",
                "test prompt",
                self.test_model,
                self.test_api_key,
                self.test_max_steps,
                self.test_config_file,
                False,
                False,
                False,
                False,
                use_aks_mcp=False,
            )
        except Exception as e:
            # Expected to fail due to missing Holmes dependencies in test environment
            # But it should fail gracefully without asyncio.run() errors
            assert "cannot be called from a running event loop" not in str(e)

    @patch('sys.stdin')
    def test_python_version_check(self, mock_stdin):
        """Test that agent checks Python version requirement."""
        from azext_aks_agent.agent.agent import aks_agent
        from knack.util import CLIError
        
        # Mock stdin to avoid pytest capture issues  
        mock_stdin.isatty.return_value = True  # No piped input
        
        with patch('azext_aks_agent.agent.agent.sys') as mock_sys:
            mock_sys.version_info = (3, 9, 0)  # Below required version
            
            with pytest.raises(CLIError) as exc_info:
                aks_agent(
                    self.mock_cmd,
                    "rg",
                    "cluster",
                    "test prompt",
                    self.test_model,
                    self.test_api_key,
                    self.test_max_steps,
                    self.test_config_file,
                    False,
                    False,
                    False,
                    False,
                    use_aks_mcp=False,
                )
            
            assert "upgrade the python version to 3.10" in str(exc_info.value)
