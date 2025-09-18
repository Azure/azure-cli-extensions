# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Tests for AKS Agent Error Handler functionality.
"""

from knack.util import CLIError


class TestAksAgentErrorHandler:
    """Test AKS Agent Error Handler functionality."""

    def test_agent_error_base_class(self):
        """Test AgentError base class functionality."""
        from azext_aks_agent.agent.error_handler import AgentError
        
        # Test basic error creation
        error = AgentError("Test error", "TEST_CODE", ["Suggestion 1", "Suggestion 2"])
        
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.error_code == "TEST_CODE"
        assert error.suggestions == ["Suggestion 1", "Suggestion 2"]
        
        # Test defaults
        error_minimal = AgentError("Minimal error")
        assert error_minimal.error_code == "GENERAL"
        assert error_minimal.suggestions == []

    def test_mcp_error_inheritance(self):
        """Test MCPError extends AgentError with default suggestions."""
        from azext_aks_agent.agent.error_handler import MCPError
        
        error = MCPError("MCP failed")
        
        assert error.error_code == "MCP"
        assert len(error.suggestions) > 0
        assert any("--aks-mcp" in suggestion for suggestion in error.suggestions)
        assert any("internet connection" in suggestion.lower() for suggestion in error.suggestions)

    def test_binary_error_inheritance(self):
        """Test BinaryError extends MCPError with specific suggestions."""
        from azext_aks_agent.agent.error_handler import BinaryError
        
        error = BinaryError("Binary download failed", "BINARY_TEST", ["Custom suggestion"])
        
        assert error.error_code == "BINARY_TEST"
        # Should have both custom and default suggestions
        assert "Custom suggestion" in error.suggestions
        assert any("internet connectivity" in suggestion.lower() for suggestion in error.suggestions)

    def test_server_error_inheritance(self):
        """Test ServerError extends MCPError with server-specific suggestions."""
        from azext_aks_agent.agent.error_handler import ServerError
        
        error = ServerError("Server startup failed")
        
        assert error.error_code == "SERVER"
        assert any("port" in suggestion.lower() for suggestion in error.suggestions)
        assert any("execute permissions" in suggestion.lower() for suggestion in error.suggestions)

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError extends AgentError with config-specific suggestions."""
        from azext_aks_agent.agent.error_handler import ConfigurationError
        
        error = ConfigurationError("Invalid config")
        
        assert error.error_code == "CONFIG"
        assert any("YAML" in suggestion for suggestion in error.suggestions)
        assert any("configuration" in suggestion.lower() for suggestion in error.suggestions)

    def test_error_message_formatting(self):
        """Test error message formatting functionality."""
        from azext_aks_agent.agent.error_handler import AgentErrorHandler, MCPError
        
        # Test with AgentError
        error = MCPError("Test MCP error", "TEST_MCP", ["Suggestion 1", "Suggestion 2"])
        formatted = AgentErrorHandler.format_error_message(error, show_suggestions=True)
        
        assert "AKS Agent Error (TEST_MCP): Test MCP error" in formatted
        assert "Suggestions:" in formatted
        assert "1. Suggestion 1" in formatted
        assert "2. Suggestion 2" in formatted
        
        # Test without suggestions
        formatted_no_suggestions = AgentErrorHandler.format_error_message(error, show_suggestions=False)
        assert "AKS Agent Error (TEST_MCP): Test MCP error" in formatted_no_suggestions
        assert "Suggestions:" not in formatted_no_suggestions
        
        # Test with non-AgentError
        regular_error = Exception("Regular error")
        formatted_regular = AgentErrorHandler.format_error_message(regular_error)
        assert "AKS Agent Error: Regular error" in formatted_regular

    def test_cli_error_creation(self):
        """Test CLIError creation from AgentError."""
        from azext_aks_agent.agent.error_handler import AgentErrorHandler, MCPError
        
        agent_error = MCPError("Test error", "TEST", ["Test suggestion"])
        cli_error = AgentErrorHandler.create_cli_error(agent_error)
        
        assert isinstance(cli_error, CLIError)
        assert "AKS Agent Error (TEST): Test error" in str(cli_error)
        assert "Test suggestion" in str(cli_error)

    def test_mcp_setup_error_handling(self):
        """Test MCP setup error handling with context-specific guidance."""
        from azext_aks_agent.agent.error_handler import AgentErrorHandler, MCPError, BinaryError, ServerError
        
        # Simulate network error
        original_error = ConnectionError("Network failure")
        mcp_error = AgentErrorHandler.handle_mcp_setup_error(original_error, "initialization")
        
        assert isinstance(mcp_error, MCPError)
        assert "MCP setup failed during initialization" in str(mcp_error)
        assert any("internet" in s.lower() for s in mcp_error.suggestions)
        
        # Binary error cases
        download_error = Exception("Download failed")
        binary_error = AgentErrorHandler.handle_binary_error(download_error, "download")
        
        assert isinstance(binary_error, BinaryError)
        assert "Binary download failed" in str(binary_error)
        assert binary_error.error_code == "BINARY_DOWNLOAD"
        assert any("internet connectivity" in suggestion.lower() for suggestion in binary_error.suggestions)
        
        # Validation
        validation_error = Exception("Checksum mismatch")
        binary_error_val = AgentErrorHandler.handle_binary_error(validation_error, "validation")
        
        assert binary_error_val.error_code == "BINARY_VALIDATION"
        assert any("corrupted" in suggestion.lower() for suggestion in binary_error_val.suggestions)
        
        # Execution
        execution_error = Exception("Permission denied")
        binary_error_exec = AgentErrorHandler.handle_binary_error(execution_error, "execution")
        
        assert binary_error_exec.error_code == "BINARY_EXECUTION"
        assert any("execute permissions" in suggestion.lower() for suggestion in binary_error_exec.suggestions)

    def test_server_error_handling(self):
        """Test server error handling with operation-specific guidance."""
        from azext_aks_agent.agent.error_handler import AgentErrorHandler, ServerError
        
        # Startup
        startup_error = Exception("Startup failed")
        server_error = AgentErrorHandler.handle_server_error(startup_error, "startup")
        
        assert isinstance(server_error, ServerError)
        assert "MCP server startup failed" in str(server_error)
        assert server_error.error_code == "SERVER_STARTUP"
        assert any("binary is available" in suggestion.lower() for suggestion in server_error.suggestions)
        
        # Health check
        health_error = Exception("Health check timeout")
        server_error_health = AgentErrorHandler.handle_server_error(health_error, "health_check")
        
        assert server_error_health.error_code == "SERVER_HEALTH_CHECK"
        assert any("automatically restarted" in suggestion.lower() for suggestion in server_error_health.suggestions)
        
        # Communication
        comm_error = Exception("Connection refused")
        server_error_comm = AgentErrorHandler.handle_server_error(comm_error, "communication")
        
        assert server_error_comm.error_code == "SERVER_COMMUNICATION"
        assert any("still running" in suggestion.lower() for suggestion in server_error_comm.suggestions)

    def test_context_error_creation(self):
        """Test AKS context validation error creation."""
        from azext_aks_agent.agent.error_handler import AgentErrorHandler, AgentError
        
        context_info = {
            "cluster_name": "test-cluster",
            "resource_group": "test-rg",
            "subscription_id": "test-sub-id"
        }
        
        context_error = AgentErrorHandler.create_context_error(context_info)
        
        assert isinstance(context_error, AgentError)
        assert context_error.error_code == "CONTEXT_VALIDATION"
        assert "test-cluster" in str(context_error)
        assert "test-rg" in str(context_error)
        assert "test-sub-id" in str(context_error)
        assert any("--name <cluster_name>" in suggestion for suggestion in context_error.suggestions)
        assert any("az login" in suggestion for suggestion in context_error.suggestions)
        
        # Test with None values
        context_info_none = {
            "cluster_name": None,
            "resource_group": None,
            "subscription_id": None
        }
        
        context_error_none = AgentErrorHandler.create_context_error(context_info_none)
        assert "None" in str(context_error_none)

    def test_error_codes_uniqueness(self):
        """Test that error codes are unique and descriptive."""
        from azext_aks_agent.agent.error_handler import (
            MCPError, BinaryError, ServerError, ConfigurationError, AgentErrorHandler
        )
        
        # Different error types
        mcp_error = MCPError("Test")
        binary_error = BinaryError("Test")
        server_error = ServerError("Test")
        config_error = ConfigurationError("Test")
        
        error_codes = {mcp_error.error_code, binary_error.error_code, 
                      server_error.error_code, config_error.error_code}
        
        assert len(error_codes) >= 3
        
        # Handler-generated errors have specific codes
        binary_download = AgentErrorHandler.handle_binary_error(Exception(), "download")
        binary_validation = AgentErrorHandler.handle_binary_error(Exception(), "validation")
        
        assert binary_download.error_code == "BINARY_DOWNLOAD"
        assert binary_validation.error_code == "BINARY_VALIDATION"
