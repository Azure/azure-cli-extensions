# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for agent status collection functionality.
"""

import os
import json
import tempfile
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from azext_aks_agent.agent.status import AgentStatusManager
from azext_aks_agent.agent.status_models import AgentStatus, BinaryStatus, ServerStatus, ConfigStatus


class TestAgentStatusManager:
    """Test cases for AgentStatusManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.status_manager = AgentStatusManager(config_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_status_manager_init_with_default_config_dir(self):
        """Test initialization with default config directory."""
        with patch('azext_aks_agent.agent.status.get_config_dir') as mock_get_config_dir:
            mock_get_config_dir.return_value = '/mock/config/dir'
            
            manager = AgentStatusManager()
            
            assert manager.config_dir == '/mock/config/dir'
            mock_get_config_dir.assert_called_once()
    
    def test_status_manager_init_with_custom_config_dir(self):
        """Test initialization with custom config directory."""
        custom_dir = '/custom/config/dir'
        manager = AgentStatusManager(config_dir=custom_dir)
        
        assert manager.config_dir == custom_dir
    
    @pytest.mark.asyncio
    @patch('azext_aks_agent.agent.status.psutil')
    async def test_get_status_success(self, mock_psutil):
        """Test successful status collection."""
        # Mock binary manager
        with patch.object(self.status_manager.binary_manager, 'get_binary_path') as mock_path, \
             patch.object(self.status_manager.binary_manager, 'get_binary_version') as mock_version, \
             patch.object(self.status_manager.binary_manager, 'validate_version') as mock_validate, \
             patch('os.path.exists') as mock_exists:
            
            mock_path.return_value = '/mock/binary/path'
            mock_version.return_value = '1.0.0'
            mock_validate.return_value = True
            mock_exists.return_value = True
            
            # Mock process info
            mock_process = Mock()
            mock_process.create_time.return_value = datetime.now().timestamp() - 3600  # 1 hour ago
            mock_psutil.Process.return_value = mock_process
            
            # Mock file stats
            with patch('os.stat') as mock_stat, \
                 patch('os.path.getmtime') as mock_getmtime:
                
                mock_stat.return_value.st_size = 1024
                mock_stat.return_value.st_mtime = datetime.now().timestamp()
                mock_getmtime.return_value = datetime.now().timestamp()
                
                status = await self.status_manager.get_status()
                
                assert isinstance(status, AgentStatus)
                assert isinstance(status.mcp_binary, BinaryStatus)
                assert isinstance(status.server, ServerStatus)
                assert isinstance(status.config, ConfigStatus)
    
    @pytest.mark.asyncio
    async def test_get_status_with_error(self):
        """Test status collection with error."""
        # Mock determine_current_mode to raise exception
        with patch.object(self.status_manager, '_determine_current_mode', side_effect=Exception("Test error")):
            
            status = await self.status_manager.get_status()
            
            assert status.mode == "error"
            assert "Status collection failed" in status.error_message
    
    def test_get_mcp_binary_status_available(self):
        """Test MCP binary status when binary is available."""
        with patch.object(self.status_manager.binary_manager, 'get_binary_path') as mock_path, \
             patch.object(self.status_manager.binary_manager, 'get_binary_version') as mock_version, \
             patch.object(self.status_manager.binary_manager, 'validate_version') as mock_validate, \
             patch('os.path.exists') as mock_exists, \
             patch('azext_aks_agent.agent.status_models.BinaryStatus.from_file_path') as mock_from_path:
            
            mock_path.return_value = '/mock/binary/path'
            mock_version.return_value = '1.0.0'
            mock_validate.return_value = True
            mock_exists.return_value = True
            
            expected_status = BinaryStatus(available=True, version='1.0.0', version_valid=True)
            mock_from_path.return_value = expected_status
            
            result = self.status_manager._get_mcp_binary_status()
            
            assert result == expected_status
            mock_from_path.assert_called_once_with('/mock/binary/path', version='1.0.0', version_valid=True)
    
    def test_get_mcp_binary_status_not_available(self):
        """Test MCP binary status when binary is not available."""
        with patch.object(self.status_manager.binary_manager, 'get_binary_path', return_value='/mock/bin'), \
             patch('os.path.exists', return_value=False):
            
            result = self.status_manager._get_mcp_binary_status()
            
            assert not result.available
            assert result.path == '/mock/bin'
            assert result.error_message == 'Binary not found'
    
    @pytest.mark.asyncio
    @patch('azext_aks_agent.agent.status.MCPManager')
    @patch('azext_aks_agent.agent.status.psutil')
    async def test_get_server_status_running_healthy(self, mock_psutil, mock_mcp_manager_class):
        """Test server status when server is running and healthy."""
        # Mock MCP manager instance
        mock_manager = Mock()
        mock_manager.is_server_running.return_value = True
        mock_manager.is_server_healthy.return_value = True
        mock_manager.get_server_url.return_value = 'http://localhost:8003/sse'
        mock_manager.get_server_port.return_value = 8003
        mock_manager.server_process = Mock()
        mock_manager.server_process.pid = 12345
        
        mock_mcp_manager_class.return_value = mock_manager
        
        # Mock process info
        mock_process = Mock()
        start_time = datetime.now() - timedelta(hours=1)
        mock_process.create_time.return_value = start_time.timestamp()
        mock_psutil.Process.return_value = mock_process
        
        result = await self.status_manager._get_server_status()
        
        assert result.running
        assert result.healthy
        assert result.url == 'http://localhost:8003/sse'
        assert result.port == 8003
        assert result.pid == 12345
        assert result.uptime is not None
    
    @pytest.mark.asyncio
    @patch('azext_aks_agent.agent.status.MCPManager')
    async def test_get_server_status_not_running(self, mock_mcp_manager_class):
        """Test server status when server is not running."""
        # Mock MCP manager instance
        mock_manager = Mock()
        mock_manager.is_server_running.return_value = False
        mock_mcp_manager_class.return_value = mock_manager
        
        result = await self.status_manager._get_server_status()
        
        assert not result.running
        assert not result.healthy
        assert result.url is None
        assert result.port is None
        assert result.pid is None
    
    @pytest.mark.asyncio
    @patch('azext_aks_agent.agent.status.MCPManager')
    async def test_get_server_status_with_exception(self, mock_mcp_manager_class):
        """Test server status collection with exception."""
        mock_mcp_manager_class.side_effect = Exception("Test error")
        
        result = await self.status_manager._get_server_status()
        
        assert not result.running
        assert not result.healthy
        assert "Server status check failed" in result.error_message
    
    def test_get_configuration_status_mcp_mode(self):
        """Test configuration status in MCP mode."""
        # Create mock state file
        state_file_path = os.path.join(self.temp_dir, "aks_agent_mode_state")
        with open(state_file_path, 'w') as f:
            json.dump({"last_mode": "mcp"}, f)
        
        # Create mock config file
        config_file_path = os.path.join(self.temp_dir, "aksAgent.yaml")
        config_data = {
            "toolsets": {
                "aks/core": {"enabled": False},
                "kubernetes/core": {"enabled": False}
            },
            "mcp_servers": {
                "aks-mcp": {"url": "http://localhost:8003/sse"}
            }
        }
        with open(config_file_path, 'w') as f:
            json.dump(config_data, f)
        
        with patch('azext_aks_agent.agent.status.ConfigurationGenerator.validate_mcp_config') as mock_validate:
            mock_validate.return_value = True
            
            result = self.status_manager._get_configuration_status()
            
            assert result.mode == "mcp"
            assert result.config_valid
            assert len(result.mcp_servers) == 1
            assert "aks-mcp" in result.mcp_servers
    
    def test_get_configuration_status_traditional_mode(self):
        """Test configuration status in traditional mode."""
        # Create mock state file
        state_file_path = os.path.join(self.temp_dir, "aks_agent_mode_state")
        with open(state_file_path, 'w') as f:
            json.dump({"last_mode": "traditional"}, f)
        
        with patch('azext_aks_agent.agent.status.ConfigurationGenerator.validate_traditional_config') as mock_validate:
            mock_validate.return_value = True
            
            result = self.status_manager._get_configuration_status()
            
            assert result.mode == "traditional"
            assert result.config_valid
    
    def test_get_configuration_status_with_exception(self):
        """Test configuration status collection with exception."""
        with patch('os.path.exists', side_effect=Exception("Test error")):
            
            result = self.status_manager._get_configuration_status()
            
            assert result.mode == "unknown"
            assert not result.config_valid
            assert "Configuration status check failed" in result.error_message
    
    def test_determine_current_mode_mcp(self):
        """Test mode determination for MCP mode."""
        config_status = ConfigStatus(mode="mcp")
        binary_status = BinaryStatus(available=True, version_valid=True)
        server_status = ServerStatus(running=True)
        
        result = self.status_manager._determine_current_mode(config_status, binary_status, server_status)
        
        assert result == "mcp"
    
    def test_determine_current_mode_traditional(self):
        """Test mode determination for traditional mode."""
        config_status = ConfigStatus(mode="traditional")
        binary_status = BinaryStatus(available=False)
        server_status = ServerStatus(running=False)
        
        result = self.status_manager._determine_current_mode(config_status, binary_status, server_status)
        
        assert result == "traditional"
    
    def test_determine_current_mode_inferred_mcp(self):
        """Test mode determination inferred as MCP from component status."""
        config_status = ConfigStatus(mode="unknown")
        binary_status = BinaryStatus(available=True, version_valid=True)
        server_status = ServerStatus(running=True)
        
        result = self.status_manager._determine_current_mode(config_status, binary_status, server_status)
        
        assert result == "mcp"
    
    def test_determine_current_mode_mcp_available(self):
        """Test mode determination for MCP available but server not running."""
        config_status = ConfigStatus(mode="unknown")
        binary_status = BinaryStatus(available=True)
        server_status = ServerStatus(running=False)
        
        result = self.status_manager._determine_current_mode(config_status, binary_status, server_status)
        
        assert result == "mcp_available"
    
    def test_get_last_mode_from_file(self):
        """Test getting last mode from state file."""
        state_file_path = os.path.join(self.temp_dir, "aks_agent_mode_state")
        with open(state_file_path, 'w') as f:
            json.dump({"last_mode": "mcp"}, f)
        
        result = self.status_manager._get_last_mode()
        
        assert result == "mcp"
    
    def test_get_last_mode_no_file(self):
        """Test getting last mode when file doesn't exist."""
        result = self.status_manager._get_last_mode()
        
        assert result == "unknown"
    
    def test_get_last_mode_invalid_json(self):
        """Test getting last mode with invalid JSON in file."""
        state_file_path = os.path.join(self.temp_dir, "aks_agent_mode_state")
        with open(state_file_path, 'w') as f:
            f.write("invalid json")
        
        result = self.status_manager._get_last_mode()
        
        assert result == "unknown"
    
    def test_get_last_mode_change_time(self):
        """Test getting last mode change time."""
        state_file_path = os.path.join(self.temp_dir, "aks_agent_mode_state")
        with open(state_file_path, 'w') as f:
            json.dump({"last_mode": "mcp"}, f)
        
        result = self.status_manager._get_last_mode_change_time()
        
        assert result is not None
        assert isinstance(result, datetime)
    
    def test_get_last_mode_change_time_no_file(self):
        """Test getting last mode change time when file doesn't exist."""
        result = self.status_manager._get_last_mode_change_time()
        
        assert result is None
    
    def test_get_last_used_timestamp(self):
        """Test getting last used timestamp."""
        # Create some files with different timestamps
        config_file_path = os.path.join(self.temp_dir, "aksAgent.yaml")
        state_file_path = os.path.join(self.temp_dir, "aks_agent_mode_state")
        
        with open(config_file_path, 'w') as f:
            f.write("{}")
        
        with open(state_file_path, 'w') as f:
            f.write("{}")
        
        result = self.status_manager._get_last_used_timestamp()
        
        assert result is not None
        assert isinstance(result, datetime)
    
    def test_get_last_used_timestamp_no_files(self):
        """Test getting last used timestamp when no files exist."""
        result = self.status_manager._get_last_used_timestamp()
        
        assert result is None
    
    def test_load_config_file_json(self):
        """Test loading JSON configuration file."""
        config_file_path = os.path.join(self.temp_dir, "test_config.json")
        config_data = {"test": "data"}
        
        with open(config_file_path, 'w') as f:
            json.dump(config_data, f)
        
        result = self.status_manager._load_config_file(config_file_path)
        
        assert result == config_data
    
    def test_load_config_file_yaml(self):
        """Test loading YAML configuration file."""
        config_file_path = os.path.join(self.temp_dir, "test_config.yaml")
        
        with open(config_file_path, 'w') as f:
            f.write("test: data\n")
        
        with patch('yaml.safe_load') as mock_yaml:
            mock_yaml.return_value = {"test": "data"}
            
            result = self.status_manager._load_config_file(config_file_path)
            
            assert result == {"test": "data"}
    
    def test_load_config_file_nonexistent(self):
        """Test loading nonexistent configuration file."""
        result = self.status_manager._load_config_file("/nonexistent/file.json")
        
        assert result is None
    
    def test_load_config_file_invalid_json_falls_back_to_yaml(self):
        """Test loading invalid JSON configuration file falls back to YAML then fails gracefully."""
        config_file_path = os.path.join(self.temp_dir, "invalid.json")
        
        with open(config_file_path, 'w') as f:
            f.write("invalid json content")
        
        # Mock yaml to also fail, simulating no yaml library or invalid yaml
        with patch('yaml.safe_load', side_effect=Exception("YAML parse error")):
            result = self.status_manager._load_config_file(config_file_path)
            
            assert result is None
