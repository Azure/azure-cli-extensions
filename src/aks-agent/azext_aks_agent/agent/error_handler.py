# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Centralized error handling and user-friendly message generation for AKS Agent.
Provides consistent error formatting and actionable guidance for common failure scenarios.
"""

from typing import Dict, Any, List
from knack.util import CLIError


class AgentError(Exception):
    """Base exception for AKS Agent errors with enhanced user messaging."""

    def __init__(self, message: str, error_code: str = None, suggestions: List[str] = None):
        """
        Initialize agent error with user-friendly message and suggestions.

        :param message: Primary error message
        :param error_code: Unique error code for debugging
        :param suggestions: List of actionable suggestions for the user
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GENERAL"
        self.suggestions = suggestions or []


class MCPError(AgentError):
    """MCP-specific errors with fallback guidance."""

    def __init__(self, message: str, error_code: str = None, suggestions: List[str] = None):
        default_suggestions = [
            "Try running without --aks-mcp to stay in traditional mode",
            "Check your internet connection for MCP binary download",
            "Verify that port 8003 is available for MCP server"
        ]
        combined_suggestions = (suggestions or []) + default_suggestions
        super().__init__(message, error_code or "MCP", combined_suggestions)


class BinaryError(MCPError):
    """Binary download and management errors."""

    def __init__(self, message: str, error_code: str = None, suggestions: List[str] = None):
        default_suggestions = [
            "Ensure you have internet connectivity to download the MCP binary",
            "Check if your firewall allows connections to GitHub releases",
            "Try running the command again - downloads may be temporarily unavailable"
        ]
        combined_suggestions = (suggestions or []) + default_suggestions
        super().__init__(message, error_code or "BINARY", combined_suggestions)


class ServerError(MCPError):
    """MCP server lifecycle and communication errors."""

    def __init__(self, message: str, error_code: str = None, suggestions: List[str] = None):
        default_suggestions = [
            "Check if another process is using the MCP server port",
            "Ensure the MCP binary has execute permissions",
            "Try restarting the agent command"
        ]
        combined_suggestions = (suggestions or []) + default_suggestions
        super().__init__(message, error_code or "SERVER", combined_suggestions)


class ConfigurationError(AgentError):
    """Configuration generation and validation errors."""

    def __init__(self, message: str, error_code: str = None, suggestions: List[str] = None):
        default_suggestions = [
            "Check that your configuration file is valid YAML",
            "Verify all required configuration fields are present",
            "Try removing custom configuration to use defaults"
        ]
        combined_suggestions = (suggestions or []) + default_suggestions
        super().__init__(message, error_code or "CONFIG", combined_suggestions)


class AgentErrorHandler:
    """Centralized error handling and message formatting for AKS Agent."""

    @staticmethod
    def format_error_message(error: Exception, show_suggestions: bool = True) -> str:
        """
        Format error message with consistent styling and suggestions.

        :param error: Exception to format
        :param show_suggestions: Whether to include suggestions in output
        :return: Formatted error message
        """
        if isinstance(error, AgentError):
            message = f"AKS Agent Error ({error.error_code}): {error.message}"

            if show_suggestions and error.suggestions:
                message += "\n\nSuggestions:"
                for i, suggestion in enumerate(error.suggestions, 1):
                    message += f"\n  {i}. {suggestion}"

            return message

        # Handle non-AgentError exceptions
        return f"AKS Agent Error: {str(error)}"

    @staticmethod
    def create_cli_error(agent_error: AgentError, show_suggestions: bool = True) -> CLIError:
        """
        Convert AgentError to CLIError with formatted message.

        :param agent_error: AgentError instance
        :param show_suggestions: Whether to include suggestions
        :return: CLIError with formatted message
        """
        formatted_message = AgentErrorHandler.format_error_message(agent_error, show_suggestions)
        return CLIError(formatted_message)

    @staticmethod
    def handle_mcp_setup_error(original_error: Exception, context: str = "") -> MCPError:
        """
        Handle MCP setup errors with contextual suggestions.

        :param original_error: Original exception that occurred
        :param context: Context of the operation (e.g., "initialization")
        :return: Enhanced MCPError with specific guidance
        """
        error_message = "MCP setup failed"
        if context:
            error_message += f" during {context}"
        error_message += f": {str(original_error)}"

        suggestions = []
        error_str = str(original_error).lower()

        # Provide specific suggestions based on error content
        if "network" in error_str or "connection" in error_str:
            suggestions.extend([
                "Check your internet connection",
                "Verify firewall settings allow GitHub access",
                "Try again after a few minutes if GitHub is temporarily unavailable"
            ])
        elif "permission" in error_str or "access" in error_str:
            suggestions.extend([
                "Check file system permissions in your Azure CLI config directory",
                "Ensure you have write access to download the MCP binary",
                "Try running with elevated permissions if necessary"
            ])
        elif "port" in error_str or "address" in error_str:
            suggestions.extend([
                "Check if port 8003 is already in use by another application",
                "Close other applications that might be using network ports",
                "Restart your terminal/command prompt and try again"
            ])

        return MCPError(error_message, "MCP_SETUP", suggestions)

    @staticmethod
    def handle_binary_error(original_error: Exception, operation: str) -> BinaryError:
        """
        Handle binary-related errors with operation-specific guidance.

        :param original_error: Original exception that occurred
        :param operation: Operation being performed (e.g., "download", "validation")
        :return: Enhanced BinaryError with specific guidance
        """
        error_message = f"Binary {operation} failed: {str(original_error)}"

        suggestions = []

        if operation == "download":
            suggestions.extend([
                "Verify you have internet connectivity",
                "Check if GitHub.com is accessible from your network",
                "Try using a VPN if you're behind a corporate firewall"
            ])
        elif operation == "validation":
            suggestions.extend([
                "The downloaded binary may be corrupted - try downloading again",
                "Check if your antivirus software is interfering with the binary",
                "Ensure you have sufficient disk space for the binary"
            ])
        elif operation == "execution":
            suggestions.extend([
                "Check if the binary has execute permissions",
                "Verify the binary is compatible with your platform",
                "Try downloading a fresh copy of the binary"
            ])

        return BinaryError(error_message, f"BINARY_{operation.upper()}", suggestions)

    @staticmethod
    def handle_server_error(original_error: Exception, operation: str) -> ServerError:
        """
        Handle server-related errors with operation-specific guidance.

        :param original_error: Original exception that occurred
        :param operation: Operation being performed (e.g., "startup", "health_check")
        :return: Enhanced ServerError with specific guidance
        """
        error_message = f"MCP server {operation} failed: {str(original_error)}"

        suggestions = []

        if operation == "startup":
            suggestions.extend([
                "Check if the MCP binary is available and executable",
                "Verify no other process is using the MCP server port",
                "Check system resources (memory, CPU) availability"
            ])
        elif operation == "health_check":
            suggestions.extend([
                "The MCP server may have crashed - it will be automatically restarted",
                "Check system logs for any server error messages",
                "Try restarting the agent command if issues persist"
            ])
        elif operation == "communication":
            suggestions.extend([
                "Check if the MCP server is still running",
                "Verify network connectivity to the server port",
                "Try restarting the agent to reinitialize the server"
            ])

        return ServerError(error_message, f"SERVER_{operation.upper()}", suggestions)

    @staticmethod
    def create_context_error(context_info: Dict[str, Any]) -> AgentError:
        """
        Create user-friendly error for AKS context validation failures.

        :param context_info: Dictionary with detected context information
        :return: AgentError with context validation guidance
        """
        cluster_name = context_info.get("cluster_name", "None")
        resource_group = context_info.get("resource_group", "None")
        subscription_id = context_info.get("subscription_id", "None")

        message = "AKS cluster context validation failed.\n\nDetected context:"
        message += f"\n- Cluster name: {cluster_name}"
        message += f"\n- Resource group: {resource_group}"
        message += f"\n- Subscription ID: {subscription_id}"

        suggestions = [
            "Provide the cluster context in your prompt (cluster name, resource group, subscription ID)",
            (
                "Restart with explicit flags: --name <cluster_name> --resource-group <resource_group> "
                "--subscription <subscription_id>"
            ),
            "Ensure you're logged into the correct Azure account with 'az login'",
            "Verify the AKS cluster exists and you have access to it",
        ]

        return AgentError(message, "CONTEXT_VALIDATION", suggestions)
