# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Tests for status data models."""

import os
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from azext_aks_agent.agent.status_models import (
    BinaryStatus,
    ServerStatus,
    ConfigStatus,
    AgentStatus,
)


class TestBinaryStatus(unittest.TestCase):
    """Test BinaryStatus data model."""

    def test_binary_status_default_initialization(self):
        """Test default values are set correctly."""
        status = BinaryStatus()
        
        self.assertFalse(status.available)
        self.assertIsNone(status.version)
        self.assertIsNone(status.path)
        self.assertIsNone(status.last_updated)
        self.assertIsNone(status.size)
        self.assertFalse(status.version_valid)
        self.assertIsNone(status.error_message)
        self.assertFalse(status.ready)

    def test_binary_status_initialization_with_values(self):
        """Test initialization with specific values."""
        now = datetime.now()
        status = BinaryStatus(
            available=True,
            version="1.0.0",
            path="/tmp/binary",
            last_updated=now,
            size=1024,
            version_valid=True
        )
        
        self.assertTrue(status.available)
        self.assertEqual(status.version, "1.0.0")
        self.assertEqual(status.path, "/tmp/binary")
        self.assertEqual(status.last_updated, now)
        self.assertEqual(status.size, 1024)
        self.assertTrue(status.version_valid)
        self.assertTrue(status.ready)

    def test_ready_property(self):
        """Test ready property logic."""
        status = BinaryStatus()
        
        # Not ready when not available
        self.assertFalse(status.ready)
        
        # Not ready when available but version not valid
        status.available = True
        self.assertFalse(status.ready)
        
        # Ready when both available and version valid
        status.version_valid = True
        self.assertTrue(status.ready)

    def test_from_file_path_nonexistent_file(self):
        """Test from_file_path with non-existent file."""
        status = BinaryStatus.from_file_path("/nonexistent/path")
        
        self.assertFalse(status.available)
        self.assertEqual(status.path, "/nonexistent/path")
        self.assertIsNone(status.version)
        self.assertIsNone(status.size)
        self.assertIsNone(status.last_updated)
        self.assertFalse(status.ready)

    def test_from_file_path_existing_file(self):
        """Test from_file_path with existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name
        
        try:
            status = BinaryStatus.from_file_path(
                tmp_path, 
                version="1.0.0", 
                version_valid=True
            )
            
            self.assertTrue(status.available)
            self.assertEqual(status.path, tmp_path)
            self.assertEqual(status.version, "1.0.0")
            self.assertTrue(status.version_valid)
            self.assertGreater(status.size, 0)
            self.assertIsInstance(status.last_updated, datetime)
            self.assertTrue(status.ready)
        finally:
            os.unlink(tmp_path)

    @patch('os.stat')
    def test_from_file_path_os_error(self, mock_stat):
        """Test from_file_path handles OS errors."""
        mock_stat.side_effect = OSError("Permission denied")
        
        # First need to ensure the file exists for the initial check
        with patch('os.path.exists', return_value=True):
            status = BinaryStatus.from_file_path("/test/path")
        
        self.assertFalse(status.available)
        self.assertEqual(status.path, "/test/path")
        self.assertIn("Failed to get file info", status.error_message)


class TestServerStatus(unittest.TestCase):
    """Test ServerStatus data model."""

    def test_server_status_default_initialization(self):
        """Test default values are set correctly."""
        status = ServerStatus()
        
        self.assertFalse(status.running)
        self.assertFalse(status.healthy)
        self.assertIsNone(status.url)
        self.assertIsNone(status.port)
        self.assertIsNone(status.pid)
        self.assertIsNone(status.uptime)
        self.assertIsNone(status.start_time)
        self.assertIsNone(status.error_message)

    def test_status_text_property(self):
        """Test status_text property."""
        status = ServerStatus()
        
        # Stopped
        self.assertEqual(status.status_text, "Stopped")
        
        # Running but unhealthy
        status.running = True
        self.assertEqual(status.status_text, "Running (Unhealthy)")
        
        # Running and healthy
        status.healthy = True
        self.assertEqual(status.status_text, "Running (Healthy)")

    def test_uptime_text_property(self):
        """Test uptime_text property formatting."""
        status = ServerStatus()
        
        # No uptime
        self.assertEqual(status.uptime_text, "N/A")
        
        # Seconds only
        status.uptime = timedelta(seconds=30)
        self.assertEqual(status.uptime_text, "30s")
        
        # Minutes and seconds
        status.uptime = timedelta(minutes=5, seconds=30)
        self.assertEqual(status.uptime_text, "5m 30s")
        
        # Hours, minutes, and seconds
        status.uptime = timedelta(hours=2, minutes=15, seconds=45)
        self.assertEqual(status.uptime_text, "2h 15m 45s")

    def test_full_initialization(self):
        """Test initialization with all values."""
        start_time = datetime.now()
        uptime = timedelta(hours=1)
        
        status = ServerStatus(
            running=True,
            healthy=True,
            url="http://localhost:8003",
            port=8003,
            pid=12345,
            uptime=uptime,
            start_time=start_time
        )
        
        self.assertTrue(status.running)
        self.assertTrue(status.healthy)
        self.assertEqual(status.url, "http://localhost:8003")
        self.assertEqual(status.port, 8003)
        self.assertEqual(status.pid, 12345)
        self.assertEqual(status.uptime, uptime)
        self.assertEqual(status.start_time, start_time)
        self.assertEqual(status.status_text, "Running (Healthy)")


class TestConfigStatus(unittest.TestCase):
    """Test ConfigStatus data model."""

    def test_config_status_default_initialization(self):
        """Test default values and post_init behavior."""
        status = ConfigStatus()
        
        self.assertEqual(status.mode, "unknown")
        self.assertIsNone(status.config_file)
        self.assertEqual(status.toolsets_enabled, [])
        self.assertEqual(status.mcp_servers, [])
        self.assertIsNone(status.last_mode_change)
        self.assertTrue(status.config_valid)
        self.assertIsNone(status.error_message)

    def test_config_status_initialization_with_values(self):
        """Test initialization with specific values."""
        toolsets = ["aks/core", "kubernetes/core"]
        mcp_servers = ["aks-mcp"]
        now = datetime.now()
        
        status = ConfigStatus(
            mode="mcp",
            config_file="/config/file.yaml",
            toolsets_enabled=toolsets,
            mcp_servers=mcp_servers,
            last_mode_change=now,
            config_valid=False
        )
        
        self.assertEqual(status.mode, "mcp")
        self.assertEqual(status.config_file, "/config/file.yaml")
        self.assertEqual(status.toolsets_enabled, toolsets)
        self.assertEqual(status.mcp_servers, mcp_servers)
        self.assertEqual(status.last_mode_change, now)
        self.assertFalse(status.config_valid)

    def test_mode_properties(self):
        """Test mode detection properties."""
        status = ConfigStatus()
        
        # Unknown mode
        self.assertFalse(status.is_mcp_mode)
        self.assertFalse(status.is_traditional_mode)
        
        # MCP mode
        status.mode = "mcp"
        self.assertTrue(status.is_mcp_mode)
        self.assertFalse(status.is_traditional_mode)
        
        # Traditional mode
        status.mode = "traditional"
        self.assertFalse(status.is_mcp_mode)
        self.assertTrue(status.is_traditional_mode)
        
        # Case insensitive
        status.mode = "MCP"
        self.assertTrue(status.is_mcp_mode)
        
        status.mode = "TRADITIONAL"
        self.assertTrue(status.is_traditional_mode)

    def test_count_properties(self):
        """Test count properties."""
        status = ConfigStatus()
        
        self.assertEqual(status.active_toolsets_count, 0)
        self.assertEqual(status.mcp_servers_count, 0)
        
        status.toolsets_enabled = ["toolset1", "toolset2", "toolset3"]
        status.mcp_servers = ["server1", "server2"]
        
        self.assertEqual(status.active_toolsets_count, 3)
        self.assertEqual(status.mcp_servers_count, 2)


class TestAgentStatus(unittest.TestCase):
    """Test AgentStatus data model."""

    def test_agent_status_default_initialization(self):
        """Test default values and component creation."""
        status = AgentStatus()
        
        self.assertEqual(status.mode, "unknown")
        self.assertIsInstance(status.mcp_binary, BinaryStatus)
        self.assertIsInstance(status.server, ServerStatus)
        self.assertIsInstance(status.config, ConfigStatus)
        self.assertIsNone(status.last_used)
        self.assertEqual(status.overall_health, "unknown")
        self.assertIsNone(status.error_message)

    def test_initialization_with_components(self):
        """Test initialization with provided components."""
        binary = BinaryStatus(available=True, version_valid=True)
        server = ServerStatus(running=True, healthy=True)
        config = ConfigStatus(mode="mcp", config_valid=True)
        
        status = AgentStatus(
            mode="mcp",
            mcp_binary=binary,
            server=server,
            config=config
        )
        
        self.assertEqual(status.mode, "mcp")
        self.assertEqual(status.mcp_binary, binary)
        self.assertEqual(status.server, server)
        self.assertEqual(status.config, config)
        self.assertEqual(status.overall_health, "healthy")

    def test_overall_health_mcp_mode(self):
        """Test overall health calculation in MCP mode."""
        status = AgentStatus()
        status.config.mode = "mcp"
        
        # Unhealthy when binary not ready
        status._update_overall_health()
        self.assertEqual(status.overall_health, "degraded")
        
        # Unhealthy when server not running
        status.mcp_binary.available = True
        status.mcp_binary.version_valid = True
        status._update_overall_health()
        self.assertEqual(status.overall_health, "degraded")
        
        # Unhealthy when server not healthy
        status.server.running = True
        status._update_overall_health()
        self.assertEqual(status.overall_health, "degraded")
        
        # Healthy when all components ready
        status.server.healthy = True
        status._update_overall_health()
        self.assertEqual(status.overall_health, "healthy")

    def test_overall_health_traditional_mode(self):
        """Test overall health calculation in traditional mode."""
        status = AgentStatus()
        status.config.mode = "traditional"
        
        # Healthy when config valid
        status._update_overall_health()
        self.assertEqual(status.overall_health, "healthy")
        
        # Degraded when config invalid
        status.config.config_valid = False
        status._update_overall_health()
        self.assertEqual(status.overall_health, "degraded")

    def test_overall_health_error(self):
        """Test overall health with error message."""
        status = AgentStatus()
        status.config.mode = "mcp"
        status.mcp_binary.available = True
        status.mcp_binary.version_valid = True
        status.server.running = True
        status.server.healthy = True
        status.error_message = "Some error occurred"
        
        status._update_overall_health()
        self.assertEqual(status.overall_health, "error")

    def test_health_properties(self):
        """Test health status properties."""
        status = AgentStatus()
        
        # Unknown
        status.overall_health = "unknown"
        self.assertFalse(status.is_healthy)
        self.assertFalse(status.is_operational)
        
        # Healthy
        status.overall_health = "healthy"
        self.assertTrue(status.is_healthy)
        self.assertTrue(status.is_operational)
        
        # Degraded
        status.overall_health = "degraded"
        self.assertFalse(status.is_healthy)
        self.assertTrue(status.is_operational)
        
        # Error
        status.overall_health = "error"
        self.assertFalse(status.is_healthy)
        self.assertFalse(status.is_operational)

    def test_emoji_properties(self):
        """Test emoji representation properties."""
        status = AgentStatus()
        
        # Health emojis
        status.overall_health = "healthy"
        self.assertEqual(status.health_emoji, "✅")
        
        status.overall_health = "degraded"
        self.assertEqual(status.health_emoji, "⚠️")
        
        status.overall_health = "error"
        self.assertEqual(status.health_emoji, "❌")
        
        status.overall_health = "unknown"
        self.assertEqual(status.health_emoji, "❓")
        
        # Mode emojis
        status.config.mode = "mcp"
        self.assertEqual(status.mode_emoji, "🚀")
        
        status.config.mode = "traditional"
        self.assertEqual(status.mode_emoji, "🔧")
        
        status.config.mode = "unknown"
        self.assertEqual(status.mode_emoji, "❓")

    def test_get_summary(self):
        """Test summary string generation."""
        status = AgentStatus()
        status.overall_health = "healthy"
        status.mode = "mcp"
        status.config.mode = "mcp"
        
        summary = status.get_summary()
        expected = "✅ Healthy | 🚀 Mcp Mode"
        self.assertEqual(summary, expected)

    def test_get_recommendations_mcp_mode(self):
        """Test recommendations for MCP mode."""
        status = AgentStatus()
        status.config.mode = "mcp"
        
        # Binary not available
        recommendations = status.get_recommendations()
        self.assertIn("Download the MCP binary", recommendations[0])
        
        # Binary available but version invalid
        status.mcp_binary.available = True
        recommendations = status.get_recommendations()
        self.assertIn("Update the MCP binary", recommendations[0])
        
        # Server not running
        status.mcp_binary.version_valid = True
        recommendations = status.get_recommendations()
        self.assertIn("Start the MCP server", recommendations[0])
        
        # Server not healthy
        status.server.running = True
        recommendations = status.get_recommendations()
        self.assertIn("Check MCP server logs", recommendations[0])

    def test_get_recommendations_traditional_mode(self):
        """Test recommendations for traditional mode."""
        status = AgentStatus()
        status.config.mode = "traditional"
        
        # With ready binary, suggest MCP
        status.mcp_binary.available = True
        status.mcp_binary.version_valid = True
        recommendations = status.get_recommendations()
        self.assertIn("Consider using MCP mode", recommendations[0])

    def test_get_recommendations_error(self):
        """Test recommendations with error."""
        status = AgentStatus()
        status.error_message = "Test error"
        
        recommendations = status.get_recommendations()
        self.assertIn("Resolve error: Test error", recommendations[0])

    def test_get_recommendations_config_invalid(self):
        """Test recommendations with invalid config."""
        status = AgentStatus()
        status.config.config_valid = False
        
        recommendations = status.get_recommendations()
        self.assertIn("Check configuration file", recommendations[0])


if __name__ == "__main__":
    unittest.main()
