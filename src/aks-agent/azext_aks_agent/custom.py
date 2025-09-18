# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines, disable=broad-except
import os
from azext_aks_agent.agent.agent import aks_agent as aks_agent_internal

from knack.log import get_logger


logger = get_logger(__name__)


# pylint: disable=unused-argument
def aks_agent(
    cmd,
    prompt,
    model,
    max_steps,
    config_file,
    resource_group_name=None,
    name=None,
    api_key=None,
    no_interactive=False,
    no_echo_request=False,
    show_tool_output=False,
    refresh_toolsets=False,
    status=False,
    use_aks_mcp=False,
):
    # If only status is requested, display and return early
    if status:
        return aks_agent_status(cmd)

    aks_agent_internal(
        cmd,
        resource_group_name,
        name,
        prompt,
        model,
        api_key,
        max_steps,
        config_file,
        no_interactive,
        no_echo_request,
        show_tool_output,
        refresh_toolsets,
        use_aks_mcp=use_aks_mcp,
    )


def aks_agent_status(cmd):
    """
    Show AKS agent configuration and status.

    :param cmd: Azure CLI command context
    :return: None (displays status via console output)
    """
    try:
        from azext_aks_agent.agent.binary_manager import AksMcpBinaryManager
        from azext_aks_agent.agent.mcp_manager import MCPManager
        from azure.cli.core.api import get_config_dir
        from azext_aks_agent._consts import CONST_MCP_BINARY_DIR

        # Initialize status information
        status_info = {
            "mode": "unknown",
            "mcp_binary": {
                "available": False,
                "path": None,
                "version": None
            },
            "server": {
                "running": False,
                "healthy": False,
                "url": None,
                "port": None
            }
        }

        try:
            # Check MCP binary status
            config_dir = get_config_dir()
            binary_manager = AksMcpBinaryManager(
                os.path.join(config_dir, CONST_MCP_BINARY_DIR)
            )

            # Binary information
            binary_available = binary_manager.is_binary_available()
            binary_version = binary_manager.get_binary_version() if binary_available else None
            binary_path = binary_manager.get_binary_path()

            status_info["mcp_binary"] = {
                "available": binary_available,
                "path": binary_path,
                "version": binary_version,
                "version_valid": binary_manager.validate_version() if binary_available else False
            }

            # Determine mode based on binary availability
            if binary_available and status_info["mcp_binary"]["version_valid"]:
                status_info["mode"] = "mcp_ready"

                # Check server status if binary is available
                try:
                    mcp_manager = MCPManager(config_dir, verbose=False)

                    status_info["server"] = {
                        "running": mcp_manager.is_server_running(),
                        "healthy": mcp_manager.is_server_healthy(),
                        "url": mcp_manager.get_server_url(),
                        "port": mcp_manager.get_server_port()
                    }

                except Exception as e:
                    logger.debug("Failed to get server status: %s", str(e))
                    status_info["server"]["error"] = str(e)
            else:
                status_info["mode"] = "traditional"

        except Exception as e:
            logger.debug("Failed to get binary status: %s", str(e))
            status_info["mcp_binary"]["error"] = str(e)
            status_info["mode"] = "traditional"

        # Display status with enhanced formatting
        _display_agent_status(status_info)

        # Return None to avoid CLI framework printing the return value
        return None

    except Exception as e:
        from knack.util import CLIError
        raise CLIError(f"Failed to get agent status: {str(e)}")


def _display_agent_status(status_info):
    """Display formatted status with rich console output."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    console = Console()

    # Title with emoji
    mode_emoji = _get_mode_emoji(status_info.get("mode", "unknown"))
    health_emoji = _get_health_emoji(status_info)

    title = f"{health_emoji} AKS Agent Status {mode_emoji}"
    console.print(Panel.fit(title, style="bold blue"))

    # Create status table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=15)
    table.add_column("Status", style="green", width=20)
    table.add_column("Details", style="white", width=40)

    # Mode row
    mode_text = status_info.get("mode", "unknown").replace("_", " ").title()
    table.add_row("Mode", f"{mode_emoji} {mode_text}", "")

    # MCP Binary status
    binary_info = status_info.get("mcp_binary", {})
    binary_status = "✅ Available" if binary_info.get("available") else "❌ Not available"
    binary_details = []

    if binary_info.get("version"):
        version_valid = binary_info.get("version_valid", True)
        version_indicator = "✅" if version_valid else "⚠️"
        binary_details.append(f"{version_indicator} v{binary_info['version']}")

    if binary_info.get("error"):
        binary_details.append(f"❌ {binary_info['error']}")

    table.add_row("MCP Binary", binary_status, " | ".join(binary_details))

    # Server status (only if binary is available)
    if binary_info.get("available") and status_info.get("mode") in ["mcp_ready", "mcp"]:
        server_info = status_info.get("server", {})
        server_status = ""
        server_details = []

        if server_info.get("running"):
            if server_info.get("healthy"):
                server_status = "✅ Running & Healthy"
            else:
                server_status = "⚠️ Running (Unhealthy)"
        else:
            server_status = "❌ Not Running"

        if server_info.get("port"):
            server_details.append(f"Port: {server_info['port']}")

        if server_info.get("error"):
            server_details.append(f"❌ {server_info['error']}")

        table.add_row("MCP Server", server_status, " | ".join(server_details))

    console.print(table)

    # Display recommendations
    _display_recommendations(console, status_info)


def _display_recommendations(console, status_info):
    """Display status-based recommendations using rich console."""
    recommendations = _get_recommendations(status_info)

    if not recommendations:
        return

    console.print("\n💡 Recommendations:", style="bold yellow")
    for rec in recommendations:
        console.print(f"  • {rec}", style="yellow")


def _get_recommendations(status_info):
    """Get status-based recommendations for the user."""
    recommendations = []
    binary_info = status_info.get("mcp_binary", {})
    server_info = status_info.get("server", {})
    mode = status_info.get("mode", "unknown")

    if not binary_info.get("available"):
        recommendations.append("Run 'az aks agent' to automatically download the MCP binary for enhanced capabilities")
    elif not binary_info.get("version_valid", True):
        recommendations.append("Update the MCP binary by running 'az aks agent --refresh-toolsets'")
    elif mode == "mcp_ready" and not server_info.get("running"):
        recommendations.append("MCP binary is ready - run 'az aks agent' to start using enhanced capabilities")
    elif mode == "mcp_ready" and server_info.get("running") and not server_info.get("healthy"):
        recommendations.append("MCP server is running but unhealthy - it will be automatically restarted on next use")
    elif mode in ["mcp_ready", "mcp"] and server_info.get("running") and server_info.get("healthy"):
        recommendations.append("✅ AKS agent is ready with enhanced MCP capabilities")
    elif mode == "traditional":
        if binary_info.get("available"):
            recommendations.append(
                "Consider using MCP mode for enhanced capabilities by running 'az aks agent' "
                "(run again with --aks-mcp to switch modes)"
            )
        else:
            recommendations.append("✅ AKS agent is ready in traditional mode")
    else:
        recommendations.append("✅ AKS agent is operational")

    return recommendations


def _get_mode_emoji(mode):
    """Get emoji representation of mode."""
    mode_emojis = {
        "mcp": "🚀",
        "mcp_ready": "🚀",
        "traditional": "🔧",
        "unknown": "❓"
    }
    return mode_emojis.get(mode, "❓")


def _get_health_emoji(status_info):
    """Get emoji representation of overall health status."""
    binary_info = status_info.get("mcp_binary", {})
    server_info = status_info.get("server", {})
    mode = status_info.get("mode", "unknown")

    # Determine health based on mode and component status
    if mode == "traditional":
        return "✅"  # Traditional mode is always healthy if working
    if mode in ["mcp_ready", "mcp"]:
        if binary_info.get("available") and binary_info.get("version_valid", True):
            if server_info.get("running") and server_info.get("healthy"):
                return "✅"  # Fully healthy
            if server_info.get("running"):
                return "⚠️"   # Running but not healthy
            return "⚠️"   # Binary ready but server not running
        return "❌"  # Binary issues
    return "❓"  # Unknown state
