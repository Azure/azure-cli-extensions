# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Status data models for AKS agent components."""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class BinaryStatus:
    """MCP binary status information."""

    available: bool = False
    version: Optional[str] = None
    path: Optional[str] = None
    last_updated: Optional[datetime] = None
    size: Optional[int] = None
    version_valid: bool = False
    error_message: Optional[str] = None

    @property
    def ready(self) -> bool:
        """Check if binary is ready for use."""
        return self.available and self.version_valid

    @classmethod
    def from_file_path(
        cls,
        file_path: str,
        version: Optional[str] = None,
        version_valid: bool = False
    ) -> "BinaryStatus":
        """Create BinaryStatus from file path with metadata."""
        if not file_path or not os.path.exists(file_path):
            return cls(available=False, path=file_path)

        try:
            stat = os.stat(file_path)
            size = stat.st_size
            last_updated = datetime.fromtimestamp(stat.st_mtime)

            return cls(
                available=True,
                version=version,
                path=file_path,
                last_updated=last_updated,
                size=size,
                version_valid=version_valid
            )
        except OSError as e:
            return cls(
                available=False,
                path=file_path,
                error_message=f"Failed to get file info: {str(e)}"
            )


@dataclass
class ServerStatus:  # pylint: disable=too-many-instance-attributes
    """MCP server status information."""

    running: bool = False
    healthy: bool = False
    url: Optional[str] = None
    port: Optional[int] = None
    pid: Optional[int] = None
    uptime: Optional[timedelta] = None
    start_time: Optional[datetime] = None
    error_message: Optional[str] = None

    @property
    def status_text(self) -> str:
        """Get human-readable status text."""
        if not self.running:
            return "Stopped"
        if not self.healthy:
            return "Running (Unhealthy)"
        return "Running (Healthy)"

    @property
    def uptime_text(self) -> str:
        """Get human-readable uptime text."""
        if not self.uptime:
            return "N/A"

        total_seconds = int(self.uptime.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"


@dataclass
class ConfigStatus:
    """Configuration status information."""

    mode: str = "unknown"
    config_file: Optional[str] = None
    toolsets_enabled: List[str] = None
    mcp_servers: List[str] = None
    last_mode_change: Optional[datetime] = None
    config_valid: bool = True
    error_message: Optional[str] = None

    def __post_init__(self):
        """Initialize mutable default values."""
        if self.toolsets_enabled is None:
            self.toolsets_enabled = []
        if self.mcp_servers is None:
            self.mcp_servers = []

    @property
    def is_mcp_mode(self) -> bool:
        """Check if currently in MCP mode."""
        return self.mode.lower() == "mcp"

    @property
    def is_traditional_mode(self) -> bool:
        """Check if currently in traditional mode."""
        return self.mode.lower() == "traditional"

    @property
    def active_toolsets_count(self) -> int:
        """Get count of active toolsets."""
        return len(self.toolsets_enabled)

    @property
    def mcp_servers_count(self) -> int:
        """Get count of configured MCP servers."""
        return len(self.mcp_servers)


@dataclass
class AgentStatus:
    """Complete agent status information."""

    mode: str = "unknown"
    mcp_binary: Optional[BinaryStatus] = None
    server: Optional[ServerStatus] = None
    config: Optional[ConfigStatus] = None
    last_used: Optional[datetime] = None
    overall_health: str = "unknown"
    error_message: Optional[str] = None

    def __post_init__(self):
        """Initialize default status objects if not provided."""
        if self.mcp_binary is None:
            self.mcp_binary = BinaryStatus()
        if self.server is None:
            self.server = ServerStatus()
        if self.config is None:
            self.config = ConfigStatus()

        # Update overall health based on component status
        self._update_overall_health()

    def _update_overall_health(self):
        """Update overall health status based on component status."""
        if self.error_message:
            self.overall_health = "error"
            return

        # In MCP mode, check all components
        if self.config.is_mcp_mode:
            if not self.mcp_binary.ready:
                self.overall_health = "degraded"
            elif not self.server.running:
                self.overall_health = "degraded"
            elif not self.server.healthy:
                self.overall_health = "degraded"
            else:
                self.overall_health = "healthy"
        # In traditional mode, only check config
        elif self.config.is_traditional_mode:
            if self.config.config_valid:
                self.overall_health = "healthy"
            else:
                self.overall_health = "degraded"
        else:
            self.overall_health = "unknown"

    @property
    def is_healthy(self) -> bool:
        """Check if agent is in healthy state."""
        return self.overall_health == "healthy"

    @property
    def is_operational(self) -> bool:
        """Check if agent is operational (healthy or degraded)."""
        return self.overall_health in ["healthy", "degraded"]

    @property
    def health_emoji(self) -> str:
        """Get emoji representation of health status."""
        health_map = {
            "healthy": "✅",
            "degraded": "⚠️",
            "error": "❌",
            "unknown": "❓"
        }
        return health_map.get(self.overall_health, "❓")

    @property
    def mode_emoji(self) -> str:
        """Get emoji representation of mode."""
        if self.config.is_mcp_mode:
            return "🚀"  # MCP mode - enhanced
        if self.config.is_traditional_mode:
            return "🔧"  # Traditional mode - tools
        return "❓"  # Unknown mode

    def get_summary(self) -> str:
        """Get a one-line status summary."""
        health_text = self.overall_health.title()
        mode_text = self.mode.title()
        return f"{self.health_emoji} {health_text} | {self.mode_emoji} {mode_text} Mode"

    def get_recommendations(self) -> List[str]:
        """Get status-based recommendations for the user."""
        recommendations = []

        # MCP mode specific recommendations
        if self.config.is_mcp_mode:
            if not self.mcp_binary.available:
                recommendations.append("Download the MCP binary to enable enhanced capabilities")
            elif not self.mcp_binary.version_valid:
                recommendations.append("Update the MCP binary to the latest version")
            elif not self.server.running:
                recommendations.append("Start the MCP server for enhanced functionality")
            elif not self.server.healthy:
                recommendations.append("Check MCP server logs for health issues")

        # Traditional mode specific recommendations
        elif self.config.is_traditional_mode:
            if self.mcp_binary.ready:
                recommendations.append("Consider using MCP mode for enhanced capabilities (run with --aks-mcp)")

        # General recommendations
        if not self.config.config_valid:
            recommendations.append("Check configuration file for syntax errors")

        if self.error_message:
            recommendations.append(f"Resolve error: {self.error_message}")

        return recommendations
