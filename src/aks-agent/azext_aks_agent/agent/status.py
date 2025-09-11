# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Status collection and management for AKS Agent.

This module provides comprehensive status collection for the AKS Agent,
including MCP binary status, server status, and configuration status.
"""

import os
import json
import psutil
from datetime import datetime
from typing import Optional, Dict, Any

from azure.cli.core.api import get_config_dir

from .status_models import AgentStatus, BinaryStatus, ServerStatus, ConfigStatus
from .binary_manager import AksMcpBinaryManager
from .mcp_manager import MCPManager
from .config_generator import ConfigurationGenerator
from .._consts import (
    CONST_MCP_BINARY_DIR,
    CONST_AGENT_CONFIG_FILE_NAME
)


class AgentStatusManager:  # pylint: disable=too-few-public-methods
    """Manages agent status collection and reporting."""

    def __init__(self, config_dir: str = None):
        """
        Initialize status manager.

        :param config_dir: Configuration directory path (defaults to Azure CLI config dir)
        :type config_dir: Optional[str]
        """
        self.config_dir = config_dir or get_config_dir()
        self.binary_manager = AksMcpBinaryManager(
            os.path.join(self.config_dir, CONST_MCP_BINARY_DIR)
        )

    async def get_status(self) -> AgentStatus:
        """
        Get comprehensive agent status.

        :param verbose: Include verbose information in status
        :type verbose: bool
        :return: Complete agent status information
        :rtype: AgentStatus
        """
        try:
            # Collect status from all components
            binary_status = self._get_mcp_binary_status()
            server_status = await self._get_server_status()
            config_status = self._get_configuration_status()

            # Determine current mode
            current_mode = self._determine_current_mode(config_status, binary_status, server_status)

            # Get last used timestamp
            last_used = self._get_last_used_timestamp()

            # Create comprehensive status
            status = AgentStatus(
                mode=current_mode,
                mcp_binary=binary_status,
                server=server_status,
                config=config_status,
                last_used=last_used
            )

            return status

        except Exception as e:  # pylint: disable=broad-exception-caught
            return AgentStatus(
                mode="error",
                error_message=f"Status collection failed: {str(e)}"
            )

    def _get_mcp_binary_status(self) -> BinaryStatus:
        """
        Collect MCP binary status.

        :return: Binary status information
        :rtype: BinaryStatus
        """
        try:
            binary_path = self.binary_manager.get_binary_path()

            if not os.path.exists(binary_path):
                return BinaryStatus(
                    available=False,
                    path=binary_path,
                    error_message="Binary not found"
                )

            # Get version and validate
            version = self.binary_manager.get_binary_version()
            version_valid = self.binary_manager.validate_version()

            # Create status from file information
            return BinaryStatus.from_file_path(
                binary_path,
                version=version,
                version_valid=version_valid
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            return BinaryStatus(
                available=False,
                error_message=f"Binary status check failed: {str(e)}"
            )

    async def _get_server_status(self) -> ServerStatus:
        """
        Collect MCP server status.

        :return: Server status information
        :rtype: ServerStatus
        """
        try:
            # Create temporary MCP manager to check server status
            mcp_manager = MCPManager(config_dir=self.config_dir, verbose=False)

            # Check if server process is running
            is_running = mcp_manager.is_server_running()
            is_healthy = False
            server_url = None
            server_port = None
            server_pid = None
            uptime = None
            start_time = None
            error_message = None

            if is_running:
                # Get server details
                server_url = mcp_manager.get_server_url()
                server_port = mcp_manager.get_server_port()

                # Try to get process information
                if hasattr(mcp_manager, 'server_process') and mcp_manager.server_process:
                    try:
                        server_pid = mcp_manager.server_process.pid

                        # Get process start time and calculate uptime
                        if server_pid:
                            process = psutil.Process(server_pid)
                            start_time = datetime.fromtimestamp(process.create_time())
                            uptime = datetime.now() - start_time
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # Process might have died or no access
                        is_running = False
                        error_message = "Server process not accessible"

                # Check server health
                if is_running:
                    is_healthy = mcp_manager.is_server_healthy()
                    if not is_healthy:
                        error_message = "Server health check failed"

            return ServerStatus(
                running=is_running,
                healthy=is_healthy,
                url=server_url,
                port=server_port,
                pid=server_pid,
                uptime=uptime,
                start_time=start_time,
                error_message=error_message
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            return ServerStatus(
                running=False,
                healthy=False,
                error_message=f"Server status check failed: {str(e)}"
            )

    def _get_configuration_status(self) -> ConfigStatus:
        """
        Collect configuration status.

        :return: Configuration status information
        :rtype: ConfigStatus
        """
        try:
            # Get current mode from state file
            current_mode = self._get_last_mode()

            # Get configuration file path
            config_file_path = os.path.join(self.config_dir, CONST_AGENT_CONFIG_FILE_NAME)
            config_file = config_file_path if os.path.exists(config_file_path) else None

            # Initialize status
            toolsets_enabled = []
            mcp_servers = []
            config_valid = True
            error_message = None
            last_mode_change = self._get_last_mode_change_time()

            # Try to parse configuration if it exists
            if config_file:
                try:
                    config_data = self._load_config_file(config_file)
                    if config_data:
                        # Extract toolsets information
                        toolsets = config_data.get("toolsets", {})
                        toolsets_enabled = [
                            name for name, config in toolsets.items()
                            if config.get("enabled", True)
                        ]

                        # Extract MCP servers information
                        mcp_servers_config = config_data.get("mcp_servers", {})
                        mcp_servers = list(mcp_servers_config.keys())

                        # Validate configuration based on mode
                        if current_mode == "mcp":
                            config_valid = ConfigurationGenerator.validate_mcp_config(config_data)
                        elif current_mode == "traditional":
                            config_valid = ConfigurationGenerator.validate_traditional_config(config_data)

                except Exception as e:  # pylint: disable=broad-exception-caught
                    config_valid = False
                    error_message = f"Configuration parsing failed: {str(e)}"

            return ConfigStatus(
                mode=current_mode,
                config_file=config_file,
                toolsets_enabled=toolsets_enabled,
                mcp_servers=mcp_servers,
                last_mode_change=last_mode_change,
                config_valid=config_valid,
                error_message=error_message
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            return ConfigStatus(
                mode="unknown",
                config_valid=False,
                error_message=f"Configuration status check failed: {str(e)}"
            )

    def _determine_current_mode(self, config_status: ConfigStatus,
                                binary_status: BinaryStatus,
                                server_status: ServerStatus) -> str:
        """
        Determine the current operational mode based on component status.

        :param config_status: Configuration status
        :param binary_status: Binary status
        :param server_status: Server status
        :return: Current mode string
        :rtype: str
        """
        # Check configuration mode first
        if config_status.is_mcp_mode:
            return "mcp"
        if config_status.is_traditional_mode:
            return "traditional"

        # Infer mode from component status
        if binary_status.ready and server_status.running:
            return "mcp"
        if binary_status.available and not server_status.running:
            return "mcp_available"
        return "traditional"

    def _get_last_mode(self) -> str:
        """
        Get the last used mode from state file.

        :return: Last mode string or 'unknown' if not found
        :rtype: str
        """
        try:
            state_file_path = os.path.join(self.config_dir, "aks_agent_mode_state")
            if os.path.exists(state_file_path):
                with open(state_file_path, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                    return state_data.get('last_mode', 'unknown')
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        return 'unknown'

    def _get_last_mode_change_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the last mode change.

        :return: Last mode change timestamp or None if not available
        :rtype: Optional[datetime]
        """
        try:
            state_file_path = os.path.join(self.config_dir, "aks_agent_mode_state")
            if os.path.exists(state_file_path):
                # Use file modification time as proxy for mode change time
                mod_time = os.path.getmtime(state_file_path)
                return datetime.fromtimestamp(mod_time)
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        return None

    def _get_last_used_timestamp(self) -> Optional[datetime]:
        """
        Get the timestamp when the agent was last used.

        :return: Last used timestamp or None if not available
        :rtype: Optional[datetime]
        """
        try:
            # Check various files to determine last usage
            potential_files = [
                os.path.join(self.config_dir, CONST_AGENT_CONFIG_FILE_NAME),
                os.path.join(self.config_dir, "aks_agent_mode_state"),
                os.path.join(self.config_dir, CONST_MCP_BINARY_DIR, "aks-mcp")
            ]

            latest_time = None
            for file_path in potential_files:
                if os.path.exists(file_path):
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if latest_time is None or mod_time > latest_time:
                        latest_time = mod_time

            return latest_time

        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def _load_config_file(self, config_file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load and parse configuration file.

        :param config_file_path: Path to configuration file
        :type config_file_path: str
        :return: Parsed configuration data or None if failed
        :rtype: Optional[Dict[str, Any]]
        """
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                # Try JSON first, then YAML if available
                content = f.read().strip()
                if content.startswith('{'):
                    return json.loads(content)
                # Try YAML parsing if content doesn't look like JSON
                try:
                    import yaml
                    return yaml.safe_load(content)
                except ImportError:
                    # YAML not available, assume it's JSON-like
                    return json.loads(content)
        except Exception:  # pylint: disable=broad-exception-caught
            return None
