# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Tests for AKS Agent Smart Refresh Strategy functionality.
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, mock_open


class TestAksAgentSmartRefresh(unittest.TestCase):
    """Test AKS Agent Smart Refresh Strategy functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_cmd = Mock()
        self.mock_cmd.cli_ctx = Mock()
        self.test_config_file = "~/.azure/aksAgent.config"
        self.test_model = "gpt-4"
        self.test_api_key = "test-key"
        self.test_max_steps = 10
        
        # Create temporary state file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_state_file = os.path.join(self.temp_dir, "aks_agent_mode_state")

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        if os.path.exists(self.test_state_file):
            os.unlink(self.test_state_file)
        os.rmdir(self.temp_dir)

    @patch('azext_aks_agent.agent.agent.get_config_dir')
    def test_get_mode_state_file(self, mock_get_config_dir):
        """Test getting the mode state file path."""
        from azext_aks_agent.agent.agent import _get_mode_state_file
        
        mock_get_config_dir.return_value = "/test/config"
        result = _get_mode_state_file()
        
        self.assertEqual(result, "/test/config/aks_agent_mode_state")
        mock_get_config_dir.assert_called_once()

    @patch('azext_aks_agent.agent.agent._get_mode_state_file')
    def test_get_last_mode_unknown(self, mock_get_state_file):
        """Test getting last mode when no state file exists."""
        from azext_aks_agent.agent.agent import _get_last_mode
        
        mock_get_state_file.return_value = "/nonexistent/state/file"
        result = _get_last_mode()
        
        self.assertEqual(result, "unknown")

    @patch('azext_aks_agent.agent.agent._get_mode_state_file')
    def test_get_last_mode_valid(self, mock_get_state_file):
        """Test getting last mode with valid state file."""
        from azext_aks_agent.agent.agent import _get_last_mode
        
        mock_get_state_file.return_value = self.test_state_file
        
        # Create state file with 'mcp' mode
        with open(self.test_state_file, 'w') as f:
            f.write("mcp")
        
        result = _get_last_mode()
        self.assertEqual(result, "mcp")

    @patch('azext_aks_agent.agent.agent._get_mode_state_file')
    def test_get_last_mode_invalid_content(self, mock_get_state_file):
        """Test getting last mode with invalid state file content."""
        from azext_aks_agent.agent.agent import _get_last_mode
        
        mock_get_state_file.return_value = self.test_state_file
        
        # Create state file with invalid content
        with open(self.test_state_file, 'w') as f:
            f.write("invalid_mode")
        
        result = _get_last_mode()
        self.assertEqual(result, "unknown")

    @patch('azext_aks_agent.agent.agent._get_mode_state_file')
    def test_get_last_mode_io_error(self, mock_get_state_file):
        """Test getting last mode handles IO errors gracefully."""
        from azext_aks_agent.agent.agent import _get_last_mode
        
        mock_get_state_file.return_value = self.test_state_file
        
        # Create state file with restricted permissions
        with open(self.test_state_file, 'w') as f:
            f.write("mcp")
        os.chmod(self.test_state_file, 0o000)  # No permissions
        
        try:
            result = _get_last_mode()
            self.assertEqual(result, "unknown")
        finally:
            # Restore permissions for cleanup
            os.chmod(self.test_state_file, 0o644)

    @patch('azext_aks_agent.agent.agent._get_mode_state_file')
    def test_save_current_mode_success(self, mock_get_state_file):
        """Test saving current mode successfully."""
        from azext_aks_agent.agent.agent import _save_current_mode
        
        mock_get_state_file.return_value = self.test_state_file
        
        _save_current_mode("mcp")
        
        # Verify the file was written correctly
        with open(self.test_state_file, 'r') as f:
            content = f.read().strip()
        self.assertEqual(content, "mcp")

    @patch('azext_aks_agent.agent.agent._get_mode_state_file')
    def test_save_current_mode_invalid_mode(self, mock_get_state_file):
        """Test saving invalid mode does nothing."""
        from azext_aks_agent.agent.agent import _save_current_mode
        
        mock_get_state_file.return_value = self.test_state_file
        
        _save_current_mode("invalid_mode")
        
        # Verify no file was created
        self.assertFalse(os.path.exists(self.test_state_file))

    @patch('azext_aks_agent.agent.agent._get_mode_state_file')
    @patch('os.makedirs')
    def test_save_current_mode_creates_directory(self, mock_makedirs, mock_get_state_file):
        """Test saving mode creates directory if needed."""
        from azext_aks_agent.agent.agent import _save_current_mode
        
        state_file_path = "/test/new/dir/aks_agent_mode_state"
        mock_get_state_file.return_value = state_file_path
        
        with patch('builtins.open', mock_open()) as mock_file:
            _save_current_mode("traditional")
            
            # Verify directory creation was attempted
            mock_makedirs.assert_called_once_with("/test/new/dir", exist_ok=True)
            mock_file.assert_called_once_with(state_file_path, 'w')

    @patch('azext_aks_agent.agent.agent._get_last_mode')
    def test_should_refresh_toolsets_first_run(self, mock_get_last_mode):
        """Test refresh decision on first run (unknown state)."""
        from azext_aks_agent.agent.agent import _should_refresh_toolsets
        
        mock_get_last_mode.return_value = "unknown"
        
        result = _should_refresh_toolsets("mcp", False)
        self.assertTrue(result)

    @patch('azext_aks_agent.agent.agent._get_last_mode')
    def test_should_refresh_toolsets_mode_transition(self, mock_get_last_mode):
        """Test refresh decision on mode transition."""
        from azext_aks_agent.agent.agent import _should_refresh_toolsets
        
        mock_get_last_mode.return_value = "traditional"
        
        # Switching from traditional to MCP
        result = _should_refresh_toolsets("mcp", False)
        self.assertTrue(result)

    @patch('azext_aks_agent.agent.agent._get_last_mode')
    def test_should_refresh_toolsets_same_mode(self, mock_get_last_mode):
        """Test refresh decision when staying in same mode."""
        from azext_aks_agent.agent.agent import _should_refresh_toolsets
        
        mock_get_last_mode.return_value = "mcp"
        
        # Staying in MCP mode
        result = _should_refresh_toolsets("mcp", False)
        self.assertFalse(result)

    @patch('azext_aks_agent.agent.agent._get_last_mode')
    def test_should_refresh_toolsets_user_request(self, mock_get_last_mode):
        """Test refresh decision honors explicit user request."""
        from azext_aks_agent.agent.agent import _should_refresh_toolsets
        
        mock_get_last_mode.return_value = "mcp"
        
        # User explicitly requested refresh, even in same mode
        result = _should_refresh_toolsets("mcp", True)
        self.assertTrue(result)

    def test_should_refresh_toolsets_all_scenarios(self):
        """Test all combinations of refresh decision logic."""
        from azext_aks_agent.agent.agent import _should_refresh_toolsets
        
        test_cases = [
            # (last_mode, requested_mode, user_refresh, expected_result, description)
            ("unknown", "mcp", False, True, "First run - MCP"),
            ("unknown", "traditional", False, True, "First run - Traditional"),
            ("mcp", "mcp", False, False, "Same mode - MCP"),
            ("traditional", "traditional", False, False, "Same mode - Traditional"),
            ("mcp", "traditional", False, True, "Mode transition - MCP to Traditional"),
            ("traditional", "mcp", False, True, "Mode transition - Traditional to MCP"),
            ("mcp", "mcp", True, True, "User request - Same mode MCP"),
            ("traditional", "traditional", True, True, "User request - Same mode Traditional"),
            ("mcp", "traditional", True, True, "User request - Mode transition"),
        ]
        
        for last_mode, requested_mode, user_refresh, expected, description in test_cases:
            with self.subTest(description=description):
                with patch('azext_aks_agent.agent.agent._get_last_mode', return_value=last_mode):
                    result = _should_refresh_toolsets(requested_mode, user_refresh)
                    self.assertEqual(result, expected, f"Failed for {description}")


if __name__ == '__main__':
    unittest.main()

