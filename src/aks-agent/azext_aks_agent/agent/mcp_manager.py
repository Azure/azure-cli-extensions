# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
MCP Manager module for AKS MCP integration.

This module provides the main interface for managing the AKS Model Context Protocol
server lifecycle and integration with the AKS agent.
"""

import os
import asyncio
from typing import Optional
from azure.cli.core.api import get_config_dir

from .binary_manager import AksMcpBinaryManager
from .._consts import CONST_MCP_BINARY_DIR
from .error_handler import ServerError


class MCPManager:
    """MCP lifecycle management with server process control"""

    def __init__(self, config_dir: str = None, verbose: bool = False):
        """
        Initialize MCP manager.

        :param config_dir: Configuration directory path (defaults to Azure CLI config dir)
        :type config_dir: Optional[str]
        :param verbose: Enable verbose output
        :type verbose: bool
        """
        self.config_dir = config_dir or get_config_dir()
        self.binary_manager = AksMcpBinaryManager(
            os.path.join(self.config_dir, CONST_MCP_BINARY_DIR)
        )
        self.verbose = verbose

        # Server process management
        self.server_process = None
        self.server_url = None
        self.server_port = None

    def is_binary_available(self) -> bool:
        """
        Check if MCP binary is available.

        :return: True if binary is available, False otherwise
        :rtype: bool
        """
        return self.binary_manager.is_binary_available()

    def get_binary_version(self) -> Optional[str]:
        """
        Get binary version if available.

        :return: Version string if available, None otherwise
        :rtype: Optional[str]
        """
        return self.binary_manager.get_binary_version()

    def get_binary_path(self) -> str:
        """
        Get the path where the MCP binary should be located.

        :return: Path to the binary
        :rtype: str
        """
        return self.binary_manager.get_binary_path()

    def validate_binary_version(self) -> bool:
        """
        Validate that the binary meets minimum version requirements.

        :return: True if binary meets requirements, False otherwise
        :rtype: bool
        """
        return self.binary_manager.validate_version()

    async def start_server(self) -> bool:
        """
        Start aks-mcp server process.

        :return: True if server started successfully, False otherwise
        :rtype: bool
        :raises: Exception if server cannot be started
        """
        import subprocess
        from .user_feedback import ProgressReporter
        from .._consts import CONST_MCP_DEFAULT_PORT

        # Check if server is already running
        if self.is_server_running():
            if self.is_server_healthy():
                if self.verbose:
                    ProgressReporter.show_status_message("MCP server is already running and healthy", "info")
                return True
            # Server is running but unhealthy, stop it first
            self.stop_server()

        # Ensure binary is available
        if not self.is_binary_available():
            raise ServerError(
                "MCP binary is not available for server startup",
                "BINARY_UNAVAILABLE",
                [
                    "The MCP binary should be automatically downloaded",
                    "Check your internet connection for binary download",
                    "Try running the command again to retry download",
                    "Run without --aks-mcp to stay in traditional mode"
                ]
            )

        # Find available port
        self.server_port = self._find_available_port(CONST_MCP_DEFAULT_PORT)
        self.server_url = f"http://localhost:{self.server_port}/sse"

        # Build command to start server
        binary_path = self.get_binary_path()
        cmd = [binary_path, "--transport", "sse", "--port", str(self.server_port)]

        try:
            if self.verbose:
                ProgressReporter.show_status_message(f"Starting MCP server on port {self.server_port}", "info")

            # Start the server using asyncio subprocess with DEVNULL stdio to avoid
            # transport pipe cleanup on loop shutdown.
            self.server_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            )

            # Wait a moment for server to initialize
            await asyncio.sleep(2)

            # Check if server is healthy
            if self.is_server_healthy():
                if self.verbose:
                    ProgressReporter.show_status_message("MCP server started successfully", "info")
                return True
            # Server failed to start properly
            self.stop_server()
            raise RuntimeError(f"MCP server failed to start or is unhealthy on port {self.server_port}")

        except Exception as e:
            # Clean up on failure
            self.stop_server()
            raise RuntimeError(f"Failed to start MCP server: {str(e)}") from e

    def stop_server(self) -> None:  # pylint: disable=too-many-nested-blocks, too-many-branches
        """
        Stop aks-mcp server process.
        """
        if self.server_process is not None:  # pylint: disable=too-many-nested-blocks
            try:
                # Get process info for debugging
                pid = getattr(self.server_process, 'pid', 'unknown')

                if self.verbose:
                    from .user_feedback import ProgressReporter
                    ProgressReporter.show_status_message(
                        f"Attempting graceful shutdown of MCP server (PID: {pid})", "info"
                    )

                # Gracefully terminate the process
                try:
                    self.server_process.terminate()
                except Exception:  # pylint: disable=broad-exception-caught
                    # Ignore terminate errors and continue with kill path
                    pass

                # Wait up to 8 seconds for graceful shutdown
                import time
                start_time = time.time()
                timeout = 8.0
                check_interval = 0.1
                last_log_time = start_time  # limit verbose logs to once every ~2 seconds

                # Poll for process exit (works for both Popen-like and asyncio Process)
                while (time.time() - start_time) < timeout:
                    time.sleep(check_interval)
                    rc = None
                    try:
                        if hasattr(self.server_process, 'poll'):
                            rc = self.server_process.poll()
                        else:
                            rc = getattr(self.server_process, 'returncode', None)
                    except Exception:  # pylint: disable=broad-exception-caught
                        rc = 0  # Assume exited

                    if rc is not None:
                        if self.verbose:
                            from .user_feedback import ProgressReporter
                            elapsed = time.time() - start_time
                            ProgressReporter.show_status_message(
                                f"MCP server shut down gracefully in {elapsed:.2f}s", "info"
                            )
                        return
                    # Fallback: OS-level existence check (handles asyncio Process without active loop)
                    try:
                        if pid != 'unknown':
                            os.kill(pid, 0)
                        # If no exception, process still exists
                    except (OSError, ProcessLookupError):
                        if self.verbose:
                            from .user_feedback import ProgressReporter
                            elapsed = time.time() - start_time
                            ProgressReporter.show_status_message(
                                f"MCP server shut down gracefully in {elapsed:.2f}s", "info"
                            )
                        return
                    # Debug: emit a message at most once every ~2 seconds in verbose mode
                    if self.verbose:
                        now = time.time()
                        if (now - last_log_time) >= 2.0:
                            elapsed = now - start_time
                            ProgressReporter.show_status_message(
                                f"Waiting for graceful shutdown... {elapsed:.1f}s", "info"
                            )
                            last_log_time = now

                # If we get here, timeout was reached and process might still be running
                try:  # pylint: disable=too-many-nested-blocks
                    # If still running, force kill (support both Popen and asyncio Process)
                    still_running = False
                    try:
                        if hasattr(self.server_process, 'poll'):
                            still_running = self.server_process.poll() is None
                        else:
                            still_running = getattr(self.server_process, 'returncode', None) is None
                    except Exception:  # pylint: disable=broad-exception-caught
                        still_running = False

                    if still_running:
                        if self.verbose:
                            from .user_feedback import ProgressReporter
                            ProgressReporter.show_status_message(
                                f"Graceful shutdown timed out after {timeout}s, using force kill", "warning"
                            )

                        try:
                            # asyncio subprocess has .kill(); Popen has .kill() as well
                            self.server_process.kill()
                        except Exception:  # pylint: disable=broad-exception-caught
                            pass

                        # Wait up to 3 seconds for kill to complete
                        kill_start = time.time()
                        while (time.time() - kill_start) < 3.0:
                            time.sleep(0.1)
                            try:
                                if hasattr(self.server_process, 'poll'):
                                    if self.server_process.poll() is not None:
                                        if self.verbose:
                                            ProgressReporter.show_status_message(
                                                "MCP server force killed successfully",
                                                "info"
                                            )
                                        break
                                else:
                                    if getattr(self.server_process, 'returncode', None) is not None:
                                        if self.verbose:
                                            ProgressReporter.show_status_message(
                                                "MCP server force killed successfully",
                                                "info"
                                            )
                                        break
                            except Exception:  # pylint: disable=broad-exception-caught
                                break

                        # If still running, warn
                        try:
                            still_running = False
                            if hasattr(self.server_process, 'poll'):
                                still_running = self.server_process.poll() is None
                            else:
                                still_running = getattr(self.server_process, 'returncode', None) is None
                            # OS-level last check
                            if pid != 'unknown':
                                try:
                                    os.kill(pid, 0)
                                except (OSError, ProcessLookupError):
                                    still_running = False
                        except Exception:  # pylint: disable=broad-exception-caught
                            still_running = False
                        if still_running and self.verbose:
                            ProgressReporter.show_status_message(
                                f"Warning: MCP server (PID: {pid}) may still be running", "warning"
                            )
                    else:
                        # Already terminated
                        if self.verbose:
                            from .user_feedback import ProgressReporter
                            ProgressReporter.show_status_message(
                                "Process terminated (PID unavailable, assuming success)", "info"
                            )

                except (OSError, ProcessLookupError):
                    # Process no longer exists - it terminated during our timeout check
                    if self.verbose:
                        from .user_feedback import ProgressReporter
                        ProgressReporter.show_status_message(
                            "MCP server terminated successfully (detected late)", "info"
                        )

            except Exception as e:  # pylint: disable=broad-exception-caught
                if self.verbose:
                    from .user_feedback import ProgressReporter
                    ProgressReporter.show_status_message(f"Error stopping server: {str(e)}", "error")
            finally:
                # Explicitly close pipes to avoid lingering file descriptors
                try:
                    stdin_obj = getattr(self.server_process, "stdin", None)
                    if stdin_obj is not None:
                        try:
                            stdin_obj.close()
                        except Exception:  # pylint: disable=broad-exception-caught
                            pass
                    for stream_name in ("stdout", "stderr"):
                        stream_obj = getattr(self.server_process, stream_name, None)
                        # StreamReader doesn't have close(); ignore safely
                        if stream_obj is not None and hasattr(stream_obj, "close"):
                            try:
                                stream_obj.close()
                            except Exception:  # pylint: disable=broad-exception-caught
                                pass
                finally:
                    self.server_process = None
                    self.server_url = None
                    self.server_port = None

    def is_server_running(self) -> bool:
        """
        Check if server process is running.

        :return: True if server process is running, False otherwise
        :rtype: bool
        """
        if self.server_process is None:
            return False

        # Check if process is still alive
        try:
            # Prefer 'returncode' when available (stable for mocks/tests)
            if hasattr(self.server_process, 'returncode'):
                return getattr(self.server_process, 'returncode', None) is None
            # Otherwise use poll() if available
            if hasattr(self.server_process, 'poll'):
                return self.server_process.poll() is None
            return False
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    def is_server_healthy(self) -> bool:
        """
        Health check server via HTTP.

        :return: True if server is healthy and responding, False otherwise
        :rtype: bool
        """
        if not self.is_server_running() or self.server_url is None:
            return False

        try:
            import urllib.request
            import urllib.error

            # Simple HTTP health check with short timeout
            # The SSE endpoint should respond with appropriate headers even for GET requests
            with urllib.request.urlopen(self.server_url, timeout=3) as response:
                # Server is responding - consider it healthy
                # SSE servers typically return 200 OK even for simple GET requests
                return response.status == 200

        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            return False

    def _find_available_port(self, start_port: int = 8003) -> int:
        """
        Find available port for server.

        :param start_port: Port to start searching from (default 8003)
        :type start_port: int
        :return: Available port number
        :rtype: int
        """
        import socket

        # Try the preferred port first
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(('localhost', port))
                    return port
            except OSError:
                continue

        # If no port is available in range, raise an exception
        raise RuntimeError(f"No available ports found in range {start_port}-{start_port + 99}")

    def get_server_url(self) -> Optional[str]:
        """
        Get the current server URL if server is running.

        :return: Server URL if available, None otherwise
        :rtype: Optional[str]
        """
        return self.server_url if self.is_server_running() else None

    def get_server_port(self) -> Optional[int]:
        """
        Get the current server port if server is running.

        :return: Server port if available, None otherwise
        :rtype: Optional[int]
        """
        return self.server_port if self.is_server_running() else None
