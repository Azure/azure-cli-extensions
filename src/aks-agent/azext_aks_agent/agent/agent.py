# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import socket
import sys
import uuid
from pathlib import Path

from azext_aks_agent._consts import (
    CONST_AGENT_CONFIG_PATH_DIR_ENV_KEY,
    CONST_AGENT_NAME,
    CONST_AGENT_NAME_ENV_KEY,
)
from azure.cli.core.api import get_config_dir
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.util import CLIError

from .prompt import AKS_CONTEXT_PROMPT
from .telemetry import CLITelemetryClient


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
    """
    with CLITelemetryClient():

        if sys.version_info < (3, 10):
            raise CLIError(
                "Please upgrade the python version to 3.10 or above to use aks agent."
            )

        # reverse the value of the variables so that
        interactive = not no_interactive
        echo = not no_echo_request

        console = init_log()

        os.environ[CONST_AGENT_CONFIG_PATH_DIR_ENV_KEY] = get_config_dir()
        # Holmes library allows the user to specify the agent name through environment variable
        # before loading the library.

        os.environ[CONST_AGENT_NAME_ENV_KEY] = CONST_AGENT_NAME

        from holmes.config import Config
        from holmes.core.prompt import build_initial_ask_messages
        from holmes.interactive import run_interactive_loop
        from holmes.plugins.destinations import DestinationType
        from holmes.plugins.interfaces import Issue
        from holmes.plugins.prompts import load_and_render_prompt
        from holmes.utils.console.result import handle_result

        # Detect and read piped input
        piped_data = None
        if not sys.stdin.isatty():
            piped_data = sys.stdin.read().strip()
            if interactive:
                console.print(
                    "[bold yellow]Interactive mode disabled when reading piped input[/bold yellow]"
                )
                interactive = False

        expanded_config_file = Path(os.path.expanduser(config_file))

        config = Config.load_from_file(
            expanded_config_file,
            model=model,
            api_key=api_key,
            max_steps=max_steps,
        )

        ai = config.create_console_toolcalling_llm(
            dal=None,
            refresh_toolsets=refresh_toolsets,
        )
        console.print(
            "[bold yellow]This tool uses AI to generate responses and may not always be accurate.[bold yellow]"
        )

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

        if echo and not interactive and prompt:
            console.print("[bold yellow]User:[/bold yellow] " + prompt)

        subscription_id = get_subscription_id(cmd.cli_ctx)

        aks_template_context = {
            "cluster_name": name,
            "resource_group": resource_group_name,
            "subscription_id": subscription_id,
        }

        aks_context_prompt = load_and_render_prompt(
            AKS_CONTEXT_PROMPT, aks_template_context
        )

        # Variables not exposed to the user.
        # Adds a prompt for post processing.
        post_processing_prompt = None
        # File to append to prompt

        include_file = None
        if interactive:
            run_interactive_loop(
                ai,
                console,
                prompt,
                include_file,
                post_processing_prompt,
                show_tool_output=show_tool_output,
                system_prompt_additions=aks_context_prompt,
            )
            return

        messages = build_initial_ask_messages(
            console,
            prompt,
            include_file,
            ai.tool_executor,
            config.get_runbook_catalog(),
            system_prompt_additions=aks_context_prompt,
        )

        response = ai.call(messages)

        messages = response.messages

        issue = Issue(
            id=str(uuid.uuid4()),
            name=prompt,
            source_type="holmes-ask",
            raw={"prompt": prompt, "full_conversation": messages},
            source_instance_id=socket.gethostname(),
        )
        handle_result(
            response,
            console,
            DestinationType.CLI,
            config,
            issue,
            show_tool_output,
            False,
        )
