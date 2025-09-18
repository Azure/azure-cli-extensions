# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import IsolatedAsyncioTestCase
import os
import tempfile
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from azext_aks_agent.agent.mcp_manager import MCPManager


class TestMCPManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config_dir = tempfile.mkdtemp()
        # Create the bin subdirectory that would be expected
        self.test_bin_dir = os.path.join(self.test_config_dir, 'bin')
        os.makedirs(self.test_bin_dir, exist_ok=True)
        
        # Set up event loop for async tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        # Clean up async tasks
        try:
            self.loop.close()
        except Exception:
            pass
        shutil.rmtree(self.test_config_dir, ignore_errors=True)
    
    @patch('azext_aks_agent.agent.mcp_manager.get_config_dir')
    def test_mcp_manager_init_with_default_config_dir(self, mock_get_config_dir):
        """Test MCP manager initialization with default config directory."""
        mock_get_config_dir.return_value = '/mock/config/dir'
        
        manager = MCPManager()
        
        self.assertEqual(manager.config_dir, '/mock/config/dir')
        self.assertFalse(manager.verbose)
        self.assertIsNotNone(manager.binary_manager)
        # Check server process management initialization
        self.assertIsNone(manager.server_process)
        self.assertIsNone(manager.server_url)
        self.assertIsNone(manager.server_port)
        mock_get_config_dir.assert_called_once()
    
    def test_mcp_manager_init_with_custom_config_dir(self):
        """Test MCP manager initialization with custom config directory."""
        manager = MCPManager(config_dir=self.test_config_dir, verbose=True)
        
        self.assertEqual(manager.config_dir, self.test_config_dir)
        self.assertTrue(manager.verbose)
        self.assertIsNotNone(manager.binary_manager)
        # Check server process management initialization
        self.assertIsNone(manager.server_process)
        self.assertIsNone(manager.server_url)
        self.assertIsNone(manager.server_port)
        # Check that binary manager was initialized with correct path
        expected_bin_path = os.path.join(self.test_config_dir, 'bin')
        self.assertEqual(manager.binary_manager.install_dir, expected_bin_path)
    
    def test_is_binary_available_true(self):
        """Test binary availability check when binary is available."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        with patch.object(manager.binary_manager, 'is_binary_available', return_value=True):
            self.assertTrue(manager.is_binary_available())
    
    def test_is_binary_available_false(self):
        """Test binary availability check when binary is not available."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        with patch.object(manager.binary_manager, 'is_binary_available', return_value=False):
            self.assertFalse(manager.is_binary_available())
    
    def test_get_binary_version_with_version(self):
        """Test getting binary version when version is available."""
        manager = MCPManager(config_dir=self.test_config_dir)
        expected_version = "0.1.0"
        
        with patch.object(manager.binary_manager, 'get_binary_version', return_value=expected_version):
            version = manager.get_binary_version()
            self.assertEqual(version, expected_version)
    
    def test_get_binary_version_none(self):
        """Test getting binary version when no version is available."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        with patch.object(manager.binary_manager, 'get_binary_version', return_value=None):
            version = manager.get_binary_version()
            self.assertIsNone(version)
    
    def test_get_binary_path(self):
        """Test getting binary path."""
        manager = MCPManager(config_dir=self.test_config_dir)
        expected_path = os.path.join(self.test_bin_dir, 'aks-mcp')
        
        with patch.object(manager.binary_manager, 'get_binary_path', return_value=expected_path):
            path = manager.get_binary_path()
            self.assertEqual(path, expected_path)
    
    def test_validate_binary_version_valid(self):
        """Test binary version validation when version is valid."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        with patch.object(manager.binary_manager, 'validate_version', return_value=True):
            self.assertTrue(manager.validate_binary_version())
    
    def test_validate_binary_version_invalid(self):
        """Test binary version validation when version is invalid."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        with patch.object(manager.binary_manager, 'validate_version', return_value=False):
            self.assertFalse(manager.validate_binary_version())


class TestMCPManagerServerLifecycle(IsolatedAsyncioTestCase):
    """Test server lifecycle management functionality."""
    
    def setUp(self):
        """Set up test fixtures for server tests."""
        self.test_config_dir = tempfile.mkdtemp()
        self.test_bin_dir = os.path.join(self.test_config_dir, 'bin')
        os.makedirs(self.test_bin_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_config_dir, ignore_errors=True)
    
    def test_initial_server_state(self):
        """Test initial server state after initialization."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        self.assertIsNone(manager.server_process)
        self.assertIsNone(manager.server_url)
        self.assertIsNone(manager.server_port)
        self.assertFalse(manager.is_server_running())
        self.assertFalse(manager.is_server_healthy())
        self.assertIsNone(manager.get_server_url())
        self.assertIsNone(manager.get_server_port())
    
    def test_find_available_port_default(self):
        """Test finding available port starting from default."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        port = manager._find_available_port(8003)
        self.assertGreaterEqual(port, 8003)
        self.assertLess(port, 8103)  # Should be within 100 port range
    
    def test_find_available_port_custom_start(self):
        """Test finding available port with custom start port."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        port = manager._find_available_port(9000)
        self.assertGreaterEqual(port, 9000)
        self.assertLess(port, 9100)  # Should be within 100 port range
    
    @patch('socket.socket')
    def test_find_available_port_no_ports_available(self, mock_socket):
        """Test exception when no ports are available."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        # Mock all sockets to fail binding
        mock_socket.return_value.__enter__.return_value.bind.side_effect = OSError("Port in use")
        
        with self.assertRaises(Exception) as cm:
            manager._find_available_port(8003)
        
        self.assertIn("No available ports found", str(cm.exception))
    
    def test_is_server_running_no_process(self):
        """Test is_server_running when no process exists."""
        manager = MCPManager(config_dir=self.test_config_dir)
        self.assertFalse(manager.is_server_running())
    
    def test_is_server_running_with_process(self):
        """Test is_server_running with active process."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        # Mock an active process
        mock_process = Mock()
        mock_process.returncode = None  # Process is still running
        manager.server_process = mock_process
        
        self.assertTrue(manager.is_server_running())
    
    def test_is_server_running_with_terminated_process(self):
        """Test is_server_running with terminated process."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        # Mock a terminated process
        mock_process = Mock()
        mock_process.returncode = 0  # Process has exited
        manager.server_process = mock_process
        
        self.assertFalse(manager.is_server_running())
    
    @patch('urllib.request.urlopen')
    def test_is_server_healthy_success(self, mock_urlopen):
        """Test server health check success."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        # Setup server state
        manager.server_process = Mock()
        manager.server_process.returncode = None
        manager.server_url = "http://localhost:8003/sse"
        
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        self.assertTrue(manager.is_server_healthy())
        mock_urlopen.assert_called_once_with("http://localhost:8003/sse", timeout=3)
    
    @patch('urllib.request.urlopen')
    def test_is_server_healthy_http_error(self, mock_urlopen):
        """Test server health check HTTP error."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        # Setup server state
        manager.server_process = Mock()
        manager.server_process.returncode = None
        manager.server_url = "http://localhost:8003/sse"
        
        # Mock HTTP error
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "http://localhost:8003/sse", 500, "Server Error", {}, None
        )
        
        self.assertFalse(manager.is_server_healthy())
    
    def test_is_server_healthy_no_url(self):
        """Test server health check when no URL is set."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        # Setup server process but no URL
        manager.server_process = Mock()
        manager.server_process.returncode = None
        # manager.server_url remains None
        
        self.assertFalse(manager.is_server_healthy())
    
    def test_is_server_healthy_not_running(self):
        """Test server health check when server is not running."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        # No server process
        self.assertFalse(manager.is_server_healthy())
    
    @patch('azext_aks_agent.agent.mcp_manager.asyncio.create_subprocess_exec')
    @patch('azext_aks_agent.agent.mcp_manager.asyncio.sleep')
    async def test_start_server_success(self, mock_sleep, mock_create_subprocess):
        """Test successful server start."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        # Mock binary availability
        with patch.object(manager, 'is_binary_available', return_value=True):
            with patch.object(manager, 'get_binary_path', return_value='/fake/aks-mcp'):
                with patch.object(manager, '_find_available_port', return_value=8003):
                    with patch.object(manager, 'is_server_healthy', return_value=True):
                        
                        # Mock subprocess creation
                        mock_process = AsyncMock()
                        mock_create_subprocess.return_value = mock_process
                        
                        result = await manager.start_server()
                        
                        self.assertTrue(result)
                        self.assertEqual(manager.server_process, mock_process)
                        self.assertEqual(manager.server_url, "http://localhost:8003/sse")
                        self.assertEqual(manager.server_port, 8003)
                        
                        # Verify subprocess was called correctly
                        mock_create_subprocess.assert_called_once()
                        args = mock_create_subprocess.call_args[0]
                        self.assertEqual(args, ('/fake/aks-mcp', '--transport', 'sse', '--port', '8003'))
    
    @patch('azext_aks_agent.agent.mcp_manager.asyncio.create_subprocess_exec')
    @patch('azext_aks_agent.agent.mcp_manager.asyncio.sleep')
    async def test_start_server_already_running_and_healthy(self, mock_sleep, mock_create_subprocess):
        """Test start_server when server is already running and healthy."""
        manager = MCPManager(config_dir=self.test_config_dir, verbose=True)
        
        with patch.object(manager, 'is_binary_available', return_value=True):
            with patch.object(manager, 'is_server_running', return_value=True):
                with patch.object(manager, 'is_server_healthy', return_value=True):
                    with patch('azext_aks_agent.agent.user_feedback.ProgressReporter.show_status_message') as mock_progress:
                        
                        result = await manager.start_server()
                        
                        self.assertTrue(result)
                        # Should not create new subprocess
                        mock_create_subprocess.assert_not_called()
                        # Should show status message in verbose mode
                        mock_progress.assert_called_with("MCP server is already running and healthy", "info")
    
    async def test_start_server_unhealthy_restart(self):
        """Test start_server restarts unhealthy running server."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        with patch.object(manager, 'is_binary_available', return_value=True):
            with patch.object(manager, 'is_server_running', return_value=True):
                with patch.object(manager, 'is_server_healthy', return_value=False):
                    with patch.object(manager, 'stop_server') as mock_stop:
                        with patch.object(manager, '_find_available_port', return_value=8003):
                            with patch.object(manager, 'get_binary_path', return_value='/fake/aks-mcp'):
                                with patch('azext_aks_agent.agent.mcp_manager.asyncio.create_subprocess_exec') as mock_create:
                                    with patch('azext_aks_agent.agent.mcp_manager.asyncio.sleep'):
                                        
                                        # Mock the health check to fail first time, succeed second time
                                        health_calls = [False, True]
                                        
                                        def side_effect(*args, **kwargs):
                                            return health_calls.pop(0) if health_calls else True
                                        
                                        with patch.object(manager, 'is_server_healthy', side_effect=side_effect):
                                            mock_process = AsyncMock()
                                            mock_create.return_value = mock_process
                                            
                                            result = await manager.start_server()
                                            
                                            self.assertTrue(result)
                                            mock_stop.assert_called_once()
    
    def test_stop_server_no_process(self):
        """Test stop_server when no process exists."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        # Should not raise exception
        manager.stop_server()
        
        self.assertIsNone(manager.server_process)
        self.assertIsNone(manager.server_url)
        self.assertIsNone(manager.server_port)
    
    def test_get_server_url_running(self):
        """Test get_server_url when server is running."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        # Mock running server
        manager.server_process = Mock()
        manager.server_process.returncode = None
        manager.server_url = "http://localhost:8003/sse"
        
        self.assertEqual(manager.get_server_url(), "http://localhost:8003/sse")
    
    def test_get_server_url_not_running(self):
        """Test get_server_url when server is not running."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        self.assertIsNone(manager.get_server_url())
    
    def test_get_server_port_running(self):
        """Test get_server_port when server is running."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        # Mock running server
        manager.server_process = Mock()
        manager.server_process.returncode = None
        manager.server_port = 8003
        
        self.assertEqual(manager.get_server_port(), 8003)
    
    def test_get_server_port_not_running(self):
        """Test get_server_port when server is not running."""
        manager = MCPManager(config_dir=self.test_config_dir)
        
        self.assertIsNone(manager.get_server_port())


if __name__ == '__main__':
    # Run tests including async tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add regular test cases
    suite.addTests(loader.loadTestsFromTestCase(TestMCPManager))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPManagerServerLifecycle))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
