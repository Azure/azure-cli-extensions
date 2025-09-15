# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""User feedback module for AKS Agent operations."""

import sys


class ProgressReporter:
    """Provides user feedback for long-running operations like binary downloads."""

    @staticmethod
    def show_download_progress(downloaded: int, total: int, filename: str, console=None) -> None:
        """
        Show download progress with progress bar.

        :param downloaded: Bytes downloaded so far
        :param total: Total bytes to download
        :param filename: Name of file being downloaded
        :param console: Console object for output (optional, will use Holmes console if available)
        """
        if total <= 0:
            return

        percentage = min(100, (downloaded / total) * 100)

        # If no console provided, try to get Holmes console, otherwise fall back to print
        if console is None:
            try:
                from holmes.utils.console.logging import init_logging
                console = init_logging([])
            except ImportError:
                # Fallback to simple print if Holmes not available
                print(f"Downloading {filename}: {percentage:.1f}% ({downloaded}/{total} bytes)")
                return

        # Only show progress if we have a TTY (interactive terminal)
        if not sys.stdout.isatty():
            return

        # Create a simple progress bar using rich console formatting
        bar_width = 40
        filled_width = int(bar_width * percentage / 100)
        progress_bar = "█" * filled_width + "░" * (bar_width - filled_width)

        console.print(f"\r[cyan]Downloading {filename}[/cyan] [{progress_bar}] {percentage:.1f}%", end="")

        # Print newline when download is complete
        if percentage >= 100:
            console.print("")  # New line after completion

    @staticmethod
    def show_status_message(message: str, level: str = "info", console=None) -> None:
        """
        Show status message with appropriate styling.

        :param message: Message to display
        :param level: Message level ('info', 'warning', 'error', 'success')
        :param console: Console object for output (optional, will use Holmes console if available)
        """
        # If no console provided, try to get Holmes console, otherwise fall back to print
        if console is None:
            try:
                from holmes.utils.console.logging import init_logging
                console = init_logging([])
            except ImportError:
                # Fallback to simple print if Holmes not available
                print(f"[{level.upper()}] {message}")
                return

        # Map levels to rich console styles
        level_styles = {
            "info": "[cyan]",
            "warning": "[yellow]",
            "error": "[red]",
            "success": "[green]"
        }

        style = level_styles.get(level.lower(), "[cyan]")
        console.print(f"{style}{message}[/{style[1:-1]}]")

    @staticmethod
    def show_binary_setup_status(status: str, console=None) -> None:
        """
        Show binary setup status message.

        :param status: Status message to display
        :param console: Console object for output (optional, will use Holmes console if available)
        """
        ProgressReporter.show_status_message(f"MCP Binary: {status}", "info", console)

    @staticmethod
    def show_server_status(status: str, silent_mode: bool = True, console=None) -> None:
        """
        Show server status (only in verbose mode by default).

        :param status: Server status message
        :param silent_mode: If True, only show in verbose mode
        :param console: Console object for output (optional, will use Holmes console if available)
        """
        if silent_mode:
            # Only show server status in verbose mode - implementation depends on verbose flag
            # For now, we'll show it as it's useful for debugging
            pass

        ProgressReporter.show_status_message(f"MCP Server: {status}", "info", console)
