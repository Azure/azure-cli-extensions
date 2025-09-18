# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import sys

from azext_aks_agent._consts import (
    CONST_AGENT_CONFIG_PATH_DIR_ENV_KEY,
    CONST_AGENT_NAME,
    CONST_AGENT_NAME_ENV_KEY,
)
from azure.cli.core.api import get_config_dir
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.util import CLIError

from .prompt import AKS_CONTEXT_PROMPT_MCP, AKS_CONTEXT_PROMPT_TRADITIONAL
from .telemetry import CLITelemetryClient
from .error_handler import MCPError


# NOTE(mainred): holmes leverage the log handler RichHandler to provide colorful, readable and well-formatted logs
# making the interactive mode more user-friendly.
# And we removed exising log handlers to avoid duplicate logs.
# Also make the console log consistent, we remove the telemetry and data logger to skip redundant logs.
def init_log():
    # NOTE(mainred): we need to disable INFO logs from LiteLLM before LiteLLM library is loaded, to avoid logging the
    # debug logs from heading of LiteLLM.
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    logging.getLogger("telemetry.main").setLevel(logging.WARNING)
    logging.getLogger("telemetry.process").setLevel(logging.WARNING)
    logging.getLogger("telemetry.save").setLevel(logging.WARNING)
    logging.getLogger("telemetry.client").setLevel(logging.WARNING)
    logging.getLogger("az_command_data_logger").setLevel(logging.WARNING)

    from holmes.utils.console.logging import init_logging

    # TODO: make log verbose configurable, currently disabled by [].
    return init_logging([])


def _get_mode_state_file() -> str:
    """Get the path to the mode state file."""
    config_dir = get_config_dir()
    return os.path.join(config_dir, "aks_agent_mode_state")


def _get_last_mode() -> str:
    """
    Get the last used mode from state file.

    :return: 'mcp' or 'traditional' or 'unknown' if no state exists
    :rtype: str
    """
    state_file = _get_mode_state_file()
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                mode = f.read().strip()
                return mode if mode in ['mcp', 'traditional'] else 'unknown'
    except (IOError, OSError):
        pass
    return 'unknown'


def _save_current_mode(mode: str) -> None:
    """
    Save the current mode to state file.

    :param mode: 'mcp' or 'traditional'
    :type mode: str
    """
    if mode not in ['mcp', 'traditional']:
        return

    state_file = _get_mode_state_file()
    try:
        # Ensure config directory exists
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        with open(state_file, 'w') as f:
            f.write(mode)
    except (IOError, OSError):
        # Silently ignore state saving errors to avoid breaking the agent
        pass


def _should_refresh_toolsets(requested_mode: str, user_refresh_request: bool) -> bool:
    """
    Determine if toolsets should be refreshed based on mode transition and user request.

    :param requested_mode: The mode being requested ('mcp' or 'traditional')
    :type requested_mode: str
    :param user_refresh_request: Whether user explicitly requested refresh
    :type user_refresh_request: bool
    :return: True if toolsets should be refreshed
    :rtype: bool
    """
    # Always honor explicit user request to refresh
    if user_refresh_request:
        return True

    # Check if we're switching modes
    last_mode = _get_last_mode()

    # Refresh on first run (unknown state) or mode transition
    if last_mode == 'unknown' or last_mode != requested_mode:
        return True

    # Same mode as last time, no refresh needed
    return False


# pylint: disable=too-many-locals
def aks_agent(
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
    use_aks_mcp=False,
):
    """
    Interact with the AKS agent using a prompt or piped input.

    :param prompt: The prompt to send to the agent.
    :type prompt: str
    :param model: The model to use for the LLM.
    :type model: str
    :param max_steps: Maximum number of steps to take.
    :type max_steps: int
    :param config_file: Path to the config file.
    :type config_file: str
    :param no_interactive: Disable interactive mode.
    :type no_interactive: bool
    :param no_echo_request: Disable echoing back the question provided to AKS Agent in the output.
    :type no_echo_request: bool
    :param show_tool_output: Whether to show tool output.
    :type show_tool_output: bool
    :param refresh_toolsets: Refresh the toolsets status.
    :type refresh_toolsets: bool
    :param use_aks_mcp: Enable AKS MCP integration and use enhanced toolsets.
    :type use_aks_mcp: bool
    """

    with CLITelemetryClient():
        if sys.version_info < (3, 10):
            raise CLIError(
                "Please upgrade the python version to 3.10 or above to use aks agent."
            )

        # Initialize variables
        interactive = not no_interactive
        echo = not no_echo_request
        console = init_log()

        # Set environment variables for Holmes
        os.environ[CONST_AGENT_CONFIG_PATH_DIR_ENV_KEY] = get_config_dir()
        os.environ[CONST_AGENT_NAME_ENV_KEY] = CONST_AGENT_NAME

        # Detect and read piped input
        piped_data = None
        if not sys.stdin.isatty():
            piped_data = sys.stdin.read().strip()
            if interactive:
                console.print(
                    "[bold yellow]Interactive mode disabled when reading piped input[/bold yellow]"
                )
                interactive = False

        # Determine MCP mode and smart refresh logic
        use_aks_mcp = bool(use_aks_mcp)
        current_mode = "mcp" if use_aks_mcp else "traditional"
        smart_refresh = _should_refresh_toolsets(current_mode, refresh_toolsets)

        if show_tool_output:
            from .user_feedback import ProgressReporter
            last_mode = _get_last_mode()
            ProgressReporter.show_status_message(
                f"Mode transition check: {last_mode} → {current_mode}, smart_refresh: {smart_refresh}", "info"
            )

        # MCP Lifecycle Manager
        mcp_lifecycle = MCPLifecycleManager()

        try:
            config = None

            if use_aks_mcp:
                try:
                    config_params = {
                        'config_file': config_file,
                        'model': model,
                        'api_key': api_key,
                        'max_steps': max_steps,
                        'verbose': show_tool_output
                    }
                    mcp_info = mcp_lifecycle.setup_mcp_sync(config_params)
                    config = mcp_info['config']

                    if show_tool_output:
                        from .user_feedback import ProgressReporter
                        ProgressReporter.show_status_message("MCP mode active - enhanced capabilities enabled", "info")

                except Exception as e:  # pylint: disable=broad-exception-caught
                    # Fallback to traditional mode on any MCP setup failure
                    from .error_handler import AgentErrorHandler
                    mcp_error = AgentErrorHandler.handle_mcp_setup_error(e, "MCP initialization")
                    if show_tool_output:
                        console.print(f"[yellow]MCP setup failed, using traditional mode: {mcp_error.message}[/yellow]")
                        if mcp_error.suggestions:
                            console.print("[dim]Suggestions for next time:[/dim]")
                            for suggestion in mcp_error.suggestions[:3]:  # Show only first 3 suggestions
                                console.print(f"[dim]  • {suggestion}[/dim]")
                    use_aks_mcp = False
                    current_mode = "traditional"

            # Fallback to traditional mode if MCP setup failed or was disabled
            if not config:
                config = _setup_traditional_mode_sync(config_file, model, api_key, max_steps, show_tool_output)
                if show_tool_output:
                    console.print("[yellow]Traditional mode active (MCP disabled)[/yellow]")

            # Save the current mode to state file for next run
            _save_current_mode(current_mode)

            # Use smart refresh logic
            effective_refresh_toolsets = smart_refresh
            if show_tool_output:
                from .user_feedback import ProgressReporter
                ProgressReporter.show_status_message(
                    f"Toolset refresh: {effective_refresh_toolsets} (Mode: {current_mode})", "info"
                )

            # Create AI client once with proper refresh settings
            ai = config.create_console_toolcalling_llm(
                dal=None,
                refresh_toolsets=effective_refresh_toolsets,
            )

            # Validate inputs
            if not prompt and not interactive and not piped_data:
                raise CLIError(
                    "Either the 'prompt' argument must be provided (unless using --interactive mode)."
                )

            # Handle piped data
            if piped_data:
                if prompt:
                    # User provided both piped data and a prompt
                    prompt = f"Here's some piped output:\n\n{piped_data}\n\n{prompt}"
                else:
                    # Only piped data, no prompt - ask what to do with it
                    prompt = f"Here's some piped output:\n\n{piped_data}\n\nWhat can you tell me about this output?"

            # Phase 2: Holmes Execution (synchronous - no event loop conflicts)
            is_mcp_mode = current_mode == "mcp"
            if interactive:
                _run_interactive_mode_sync(ai, cmd, resource_group_name, name,
                                           prompt, console, show_tool_output, is_mcp_mode)
            else:
                _run_noninteractive_mode_sync(ai, config, cmd, resource_group_name, name,
                                              prompt, console, echo, show_tool_output, is_mcp_mode)

        finally:
            # Phase 3: MCP Cleanup (isolated async if needed)
            mcp_lifecycle.cleanup_mcp_sync()


def _initialize_mcp_manager(verbose: bool = False):
    """
    Initialize MCP manager for the current session.

    :param verbose: Enable verbose output
    :return: Initialized MCP manager
    :raises: Exception if initialization fails
    """
    try:
        from .mcp_manager import MCPManager
        return MCPManager(verbose=verbose)
    except ImportError as e:
        raise MCPError(
            f"MCP manager initialization failed: {str(e)}",
            "MCP_IMPORT",
            [
                "Ensure all required dependencies are installed",
                "Try reinstalling the aks-preview extension",
                "Use --aks-mcp flag to enable MCP integration"
            ]
        )


async def _setup_mcp_mode(mcp_manager, config_file: str, model: str, api_key: str,
                          max_steps: int, verbose: bool = False):
    """
    Setup MCP mode configuration and start server.

    :param mcp_manager: Initialized MCP manager
    :param config_file: Path to configuration file
    :param model: Model name
    :param api_key: API key
    :param max_steps: Maximum steps
    :param verbose: Enable verbose output
    :return: Enhanced Holmes configuration
    :raises: Exception if MCP setup fails
    """
    from pathlib import Path
    import yaml
    import tempfile
    from holmes.config import Config
    from .config_generator import ConfigurationGenerator
    from .user_feedback import ProgressReporter
    from .error_handler import AgentErrorHandler

    # Ensure binary is available (download if needed)
    if not mcp_manager.is_binary_available() or not mcp_manager.validate_binary_version():
        if verbose:
            ProgressReporter.show_status_message("Downloading MCP binary...", "info")

        # This will raise an exception if download fails
        binary_status = await mcp_manager.binary_manager.ensure_binary()
        if not binary_status.ready:
            error_msg = binary_status.error_message or "Unknown error during binary setup"
            raise AgentErrorHandler.handle_binary_error(Exception(error_msg), "setup")

    # Start MCP server
    if verbose:
        ProgressReporter.show_status_message("Starting MCP server...", "info")

    server_started = await mcp_manager.start_server()
    if not server_started:
        raise AgentErrorHandler.handle_server_error(Exception("Server startup failed"), "startup")

    # Get MCP server URL
    server_url = mcp_manager.get_server_url()
    if not server_url:
        raise AgentErrorHandler.handle_server_error(Exception("Server URL unavailable after startup"), "configuration")

    # Load base configuration as dictionary
    expanded_config_file = Path(os.path.expanduser(config_file))
    base_config_dict = {}

    if expanded_config_file.exists():
        try:
            with open(expanded_config_file, 'r') as f:
                base_config_dict = yaml.safe_load(f) or {}
        except Exception as e:  # pylint: disable=broad-exception-caught
            if verbose:
                ProgressReporter.show_status_message(f"Warning: Could not load config file: {e}", "warning")
            # Continue with empty dict if config file cannot be loaded
            base_config_dict = {}

    # Generate enhanced MCP config
    mcp_config_dict = ConfigurationGenerator.generate_mcp_config(base_config_dict, server_url)

    # Create temporary config file with MCP settings
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
        yaml.dump(mcp_config_dict, temp_file)
        temp_config_path = temp_file.name

    try:
        # Load config from temporary file using Holmes API
        enhanced_config = Config.load_from_file(
            Path(temp_config_path),
            model=model,
            api_key=api_key,
            max_steps=max_steps,
        )
        return enhanced_config
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_config_path)
        except OSError:
            pass  # Ignore cleanup errors


def _run_async_operation(async_func, *args, **kwargs):
    """
    Run async operation in isolated event loop to avoid nested loop conflicts.

    This helper safely executes async operations by:
    1. First attempting to use asyncio.run() (normal case)
    2. If that fails due to existing event loop, using concurrent execution

    :param async_func: Async function to execute
    :param args: Positional arguments for the function
    :param kwargs: Keyword arguments for the function
    :return: Result of the async function execution
    :raises: Exception if the async operation fails
    """
    import asyncio
    import concurrent.futures

    try:
        # Normal case: no existing event loop
        return asyncio.run(async_func(*args, **kwargs))
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            # Nested case: run in separate thread with new event loop
            def run_in_thread():
                # Create new event loop in this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(async_func(*args, **kwargs))
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)

            # Execute in thread pool to avoid blocking
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_in_thread)
                return future.result(timeout=300)  # 5 minute timeout
        else:
            # Re-raise other RuntimeErrors
            raise


class MCPLifecycleManager:
    """
    Manages MCP (Model Context Protocol) lifecycle with isolated async operations.

    This class decouples MCP lifecycle management (setup/cleanup) from main execution
    to prevent asyncio event loop conflicts. It provides synchronous wrappers for
    async operations that can be safely called from any context.
    """

    def __init__(self):
        """Initialize MCP lifecycle manager."""
        self.mcp_manager = None
        self.config = None
        self._setup_params = None
        self._loop = None  # dedicated loop for MCP subprocess lifecycle

    def _ensure_loop(self):
        """Ensure a dedicated event loop exists for MCP lifecycle."""
        import asyncio
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()

    def setup_mcp_sync(self, config_params):
        """
        Synchronous wrapper for MCP setup phase.

        This method handles:
        - MCP manager initialization
        - Binary download and validation
        - MCP server startup
        - Configuration generation

        :param config_params: Dictionary containing config parameters:
            - config_file: Path to configuration file
            - model: Model name
            - api_key: API key
            - max_steps: Maximum steps
            - verbose: Enable verbose output
        :type config_params: dict
        :return: Dictionary with setup results including config and server info
        :rtype: dict
        :raises: Exception if MCP setup fails
        """
        self._setup_params = config_params
        self._ensure_loop()
        try:
            return self._loop.run_until_complete(self._setup_mcp_async(config_params))
        except RuntimeError as e:
            # In rare cases if a conflicting loop is running in this thread, fall back to thread execution
            if "This event loop is already running" in str(e):
                import concurrent.futures

                def run_in_thread():
                    self._ensure_loop()
                    return self._loop.run_until_complete(self._setup_mcp_async(config_params))
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(run_in_thread)
                    return future.result(timeout=300)
            raise

    def cleanup_mcp_sync(self):
        """
        Synchronous wrapper for MCP cleanup phase.

        Gracefully shuts down MCP server and cleans up resources.
        Safe to call even if setup failed or was never called.
        """
        if self.mcp_manager:
            try:
                self._ensure_loop()
                self._loop.run_until_complete(self._cleanup_mcp_async())
            except Exception as e:  # pylint: disable=broad-exception-caught
                # Log cleanup errors but don't re-raise to avoid masking original errors
                try:
                    from .user_feedback import ProgressReporter
                    ProgressReporter.show_status_message(
                        f"Warning: Error during MCP cleanup: {str(e)}", "warning"
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    # Fallback to basic logging if ProgressReporter fails
                    print(f"Warning: Error during MCP cleanup: {str(e)}")
            finally:
                # Close the dedicated loop after cleanup
                try:
                    if self._loop is not None and not self._loop.is_closed():
                        self._loop.close()
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
                self._loop = None

    async def _setup_mcp_async(self, config_params):
        """
        Async MCP setup: binary download, server start, config generation.

        :param config_params: Configuration parameters dictionary
        :return: Setup results including config and server information
        :raises: Exception if any setup step fails
        """
        verbose = config_params.get('verbose', False)

        # Initialize MCP manager
        self.mcp_manager = _initialize_mcp_manager(verbose)

        # Setup MCP mode using existing function
        self.config = await _setup_mcp_mode(
            self.mcp_manager,
            config_params['config_file'],
            config_params['model'],
            config_params['api_key'],
            config_params['max_steps'],
            verbose
        )

        # Return setup results
        return {
            'config': self.config,
            'server_url': self.mcp_manager.get_server_url(),
            'server_port': self.mcp_manager.get_server_port(),
            'manager': self.mcp_manager
        }

    async def _cleanup_mcp_async(self):
        """
        Async MCP cleanup: graceful server shutdown.
        """
        if self.mcp_manager:
            self.mcp_manager.stop_server()  # Now synchronous, no await needed
            self.mcp_manager = None
        self.config = None
        self._setup_params = None

    def is_mcp_active(self):
        """
        Check if MCP is currently active.

        :return: True if MCP manager is initialized and server is running
        :rtype: bool
        """
        return (self.mcp_manager is not None and
                self.mcp_manager.is_server_running())

    def get_config(self):
        """
        Get the current configuration object.

        :return: Holmes configuration object if setup succeeded, None otherwise
        :rtype: object or None
        """
        return self.config


def _build_aks_context(cluster_name, resource_group_name, subscription_id, is_mcp_mode):
    """
    Build AKS context prompt for the AI agent.

    :param cluster_name: AKS cluster name
    :param resource_group_name: Resource group name
    :param subscription_id: Azure subscription ID
    :param is_mcp_mode: Whether running in MCP mode (affects toolset instructions)
    :return: Rendered AKS context prompt
    """
    from holmes.plugins.prompts import load_and_render_prompt

    aks_template_context = {
        "cluster_name": cluster_name,
        "resource_group": resource_group_name,
        "subscription_id": subscription_id,
        "is_mcp_mode": is_mcp_mode,
    }

    # Select the appropriate prompt template based on mode
    prompt_template = AKS_CONTEXT_PROMPT_MCP if is_mcp_mode else AKS_CONTEXT_PROMPT_TRADITIONAL

    return load_and_render_prompt(prompt_template, aks_template_context)


def _run_interactive_mode_sync(ai, cmd, resource_group_name, name,
                               prompt, console, show_tool_output, is_mcp_mode):
    """
    Run interactive mode synchronously - no event loop conflicts.

    This function runs Holmes interactive loop without any async context,
    preventing the nested event loop conflicts that were causing failures.

    :param ai: Holmes AI client (pre-configured with toolsets)
    :param cmd: Azure CLI command context
    :param resource_group_name: AKS resource group name
    :param name: AKS cluster name
    :param prompt: Initial prompt (optional)
    :param console: Console object for output
    :param show_tool_output: Whether to show tool output
    :param is_mcp_mode: Whether running in MCP mode (affects prompt selection)
    """
    from holmes.interactive import run_interactive_loop

    # Prepare AKS context with mode-specific prompt
    subscription_id = get_subscription_id(cmd.cli_ctx)
    aks_context = _build_aks_context(name, resource_group_name, subscription_id, is_mcp_mode)

    console.print(
        "[bold yellow]This tool uses AI to generate responses and may not always be accurate.[bold yellow]"
    )

    # Holmes interactive loop - runs synchronously ✅
    run_interactive_loop(
        ai, console, prompt, None, None,
        show_tool_output=show_tool_output,
        system_prompt_additions=aks_context,
        check_version=False
    )


def _run_noninteractive_mode_sync(ai, config, cmd, resource_group_name, name,
                                  prompt, console, echo, show_tool_output, is_mcp_mode):
    """
    Run non-interactive mode synchronously.

    :param ai: Holmes AI client (pre-configured with toolsets)
    :param config: Holmes configuration object (for runbook catalog)
    :param cmd: Azure CLI command context
    :param resource_group_name: AKS resource group name
    :param name: AKS cluster name
    :param prompt: User prompt
    :param console: Console object for output
    :param echo: Whether to echo prompts
    :param show_tool_output: Whether to show tool output
    :param is_mcp_mode: Whether running in MCP mode (affects prompt selection)
    """
    import uuid
    import socket
    from holmes.core.prompt import build_initial_ask_messages
    from holmes.plugins.destinations import DestinationType
    from holmes.plugins.interfaces import Issue
    from holmes.utils.console.result import handle_result

    # Prepare AKS context with mode-specific prompt
    subscription_id = get_subscription_id(cmd.cli_ctx)
    aks_context = _build_aks_context(name, resource_group_name, subscription_id, is_mcp_mode)

    console.print(
        "[bold yellow]This tool uses AI to generate responses and may not always be accurate.[bold yellow]"
    )

    if echo and prompt:
        console.print("[bold yellow]User:[/bold yellow] " + prompt)

    # Build and execute the conversation
    messages = build_initial_ask_messages(
        console, prompt, None, ai.tool_executor,
        config.get_runbook_catalog(), system_prompt_additions=aks_context
    )

    response = ai.call(messages)

    # Handle the result
    issue = Issue(
        id=str(uuid.uuid4()), name=prompt, source_type="holmes-ask",
        raw={"prompt": prompt, "full_conversation": response.messages},
        source_instance_id=socket.gethostname()
    )

    handle_result(response, console, DestinationType.CLI, config,
                  issue, show_tool_output, False)


def _setup_traditional_mode_sync(config_file: str, model: str, api_key: str,
                                 max_steps: int, verbose: bool = False):
    """
    Synchronous wrapper for traditional mode setup.

    :param config_file: Path to configuration file
    :param model: Model name
    :param api_key: API key
    :param max_steps: Maximum steps
    :param verbose: Enable verbose output
    :return: Traditional Holmes configuration
    """
    from pathlib import Path
    import yaml
    import tempfile
    from holmes.config import Config
    from .config_generator import ConfigurationGenerator

    # Load base config
    expanded_config_file = Path(os.path.expanduser(config_file))
    base_config_dict = {}

    if expanded_config_file.exists():
        try:
            with open(expanded_config_file, 'r') as f:
                base_config_dict = yaml.safe_load(f) or {}
        except Exception as e:  # pylint: disable=broad-exception-caught
            if verbose:
                print(f"Warning: Could not load config file: {e}")
            base_config_dict = {}

    # Generate traditional config
    traditional_config_dict = ConfigurationGenerator.generate_traditional_config(base_config_dict)

    # Create temporary config and load
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
        yaml.dump(traditional_config_dict, temp_file)
        temp_config_path = temp_file.name

    try:
        return Config.load_from_file(Path(temp_config_path), model=model,
                                     api_key=api_key, max_steps=max_steps)
    finally:
        try:
            os.unlink(temp_config_path)
        except OSError:
            pass
