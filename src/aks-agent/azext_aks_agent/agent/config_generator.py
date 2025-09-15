# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Configuration generation for AKS Agent with MCP integration support.
"""

from typing import Dict, Any
import copy


class ConfigurationGenerator:
    """Generate Holmes configuration for different modes (MCP vs Traditional)."""

    # Default built-in toolsets that conflict with MCP
    DEFAULT_CONFLICTING_TOOLSETS = {
        "aks/node-health": {"enabled": True},
        "aks/core": {"enabled": True},
        "kubernetes/core": {"enabled": True},
        "kubernetes/logs": {"enabled": True},
        "kubernetes/live-metrics": {"enabled": True},
        "bash": {"enabled": True}
    }

    @staticmethod
    def generate_mcp_config(base_config: Dict[str, Any], server_url: str) -> Dict[str, Any]:
        """
        Generate MCP mode configuration.

        :param base_config: Base Holmes configuration dictionary
        :param server_url: MCP server URL (e.g., "http://localhost:8003/sse")
        :return: Enhanced configuration with MCP server integration
        """
        if not base_config:
            base_config = {}

        if not server_url:
            raise ValueError("server_url is required for MCP configuration")

        # Deep copy to avoid modifying the original
        config = copy.deepcopy(base_config)

        # Disable conflicting built-in toolsets
        toolsets = config.get("toolsets", {})
        for toolset_name in ConfigurationGenerator.DEFAULT_CONFLICTING_TOOLSETS:
            toolsets[toolset_name] = {"enabled": False}

        config["toolsets"] = toolsets

        # Add MCP server configuration
        mcp_servers = config.get("mcp_servers", {})
        mcp_servers["aks-mcp"] = {
            "description": "AKS MCP server",
            "url": server_url
        }
        config["mcp_servers"] = mcp_servers

        return config

    @staticmethod
    def generate_traditional_config(base_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate traditional mode configuration.

        :param base_config: Base Holmes configuration dictionary
        :return: Configuration with traditional built-in toolsets enabled
        """
        if not base_config:
            base_config = {}

        # Deep copy to avoid modifying the original
        config = copy.deepcopy(base_config)

        # Ensure all built-in toolsets are enabled (default behavior)
        toolsets = config.get("toolsets", {})

        for toolset_name, toolset_config in ConfigurationGenerator.DEFAULT_CONFLICTING_TOOLSETS.items():
            toolsets[toolset_name] = copy.deepcopy(toolset_config)

        config["toolsets"] = toolsets

        # Remove any MCP server configurations if they exist
        if "mcp_servers" in config:
            del config["mcp_servers"]

        return config

    @staticmethod
    def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge configuration dictionaries with deep merge for nested structures.

        :param base: Base configuration dictionary
        :param override: Override configuration dictionary
        :return: Merged configuration with override values taking precedence
        """
        if not base:
            return copy.deepcopy(override) if override else {}

        if not override:
            return copy.deepcopy(base)

        result = copy.deepcopy(base)

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Deep merge nested dictionaries
                result[key] = ConfigurationGenerator.merge_configs(result[key], value)
            else:
                # Override value
                result[key] = copy.deepcopy(value)

        return result

    @staticmethod
    def validate_mcp_config(config: Dict[str, Any]) -> bool:
        """
        Validate that MCP configuration is properly structured.

        :param config: Configuration dictionary to validate
        :return: True if valid MCP configuration
        """
        if not isinstance(config, dict):
            return False

        # Check MCP servers exist
        mcp_servers = config.get("mcp_servers")
        if not isinstance(mcp_servers, dict):
            return False

        # Check aks-mcp server configuration
        aks_mcp = mcp_servers.get("aks-mcp")
        if not isinstance(aks_mcp, dict):
            return False

        required_fields = ["description", "url"]
        for field in required_fields:
            if field not in aks_mcp:
                return False

        # Check conflicting toolsets are disabled
        toolsets = config.get("toolsets", {})
        for toolset_name in ConfigurationGenerator.DEFAULT_CONFLICTING_TOOLSETS:
            toolset_config = toolsets.get(toolset_name, {})
            if toolset_config.get("enabled", True):  # Default enabled if not specified
                return False

        return True

    @staticmethod
    def validate_traditional_config(config: Dict[str, Any]) -> bool:
        """
        Validate that traditional configuration is properly structured.

        :param config: Configuration dictionary to validate
        :return: True if valid traditional configuration
        """
        if not isinstance(config, dict):
            return False

        # Check that MCP servers are not configured
        if "mcp_servers" in config:
            return False

        # Check that traditional toolsets are enabled
        toolsets = config.get("toolsets", {})
        for toolset_name in ConfigurationGenerator.DEFAULT_CONFLICTING_TOOLSETS:
            toolset_config = toolsets.get(toolset_name, {})
            if not toolset_config.get("enabled", False):
                return False

        return True
