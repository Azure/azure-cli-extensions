# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from knack.util import CLIError
import logging
import os
from pathlib import Path
import socket
import sys
import uuid
import typer


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

    # TODO: make log verbose configurable, currently disbled by [].
    return init_logging([])

def aks_agent(
        cmd,
        resource_group_name,
        name,
        prompt,
        model,
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

    if sys.version_info < (3, 10):
        raise CLIError("Please upgrade the python version to 3.10 or above to use aks agent.")

    # reverse the value of the variables so that
    interactive = not no_interactive
    echo = not no_echo_request

    console = init_log()

    # Holmes library allows the user to specify the agent name through environment variable before loading the library.
    os.environ["AGENT_NAME"] = "AKS AGENT"

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

    config_file = Path(config_file)
    config = Config.load_from_file(
        config_file,
        model=model,
        max_steps=max_steps,
    )

    ai = config.create_console_toolcalling_llm(
        dal=None,
        refresh_toolsets=refresh_toolsets,
    )
    template_context = {
        "toolsets": ai.tool_executor.toolsets,
        "runbooks": config.get_runbook_catalog(),
    }

    if not prompt and not interactive and not piped_data:
        raise typer.BadParameter(
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

    # TODO: extend the system prompt with AKS context
    system_prompt = "builtin://generic_ask.jinja2"
    system_prompt_rendered = load_and_render_prompt(system_prompt, template_context)

    subscription_id = get_subscription_id(cmd.cli_ctx)

    aks_template_context = {
        "cluster_name": name,
        "resource_group": resource_group_name,
        "subscription_id": subscription_id,
    }

    aks_context_prompt = """
# Azure Kubernetes Service (AKS)

You are specifically working with Azure Kubernetes Service (AKS) clusters. All investigations and troubleshooting should be performed on the AKS cluster. When troubleshooting AKS, you should consider both Azure resources and Kubernetes resources.

The current provided AKS context is as follow:
cluster_name: {{cluster_name}}
resource_group: {{resource_group}}
subscription_id: {{subscription_id}}

## Prerequisites
### AKS cluster name is under the resource group and subscription specified

You should check if the AKS cluster {{cluster_name}} can be found under resource group {{resource_group}} and subscription {{subscription_id}}.
If not, you should prompt to the user to specify correct cluster name, resource group and subscription ID.

## AKS cluster is in the current kubeconfig context
If the current kubeconfig context is not set to the AKS cluster {{cluster_name}}, you should download the kubeconfig credential with the cluster name {{cluster_name}}, resource group name {{resource_group}} and subscription ID {{subscription_id}}.
If the current kubeconfig context is set to the AKS cluster {{cluster_name}}, you should proceed with the investigation and troubleshooting.
"""
    aks_context_prompt = load_and_render_prompt(aks_context_prompt, aks_template_context)
    system_prompt_rendered += aks_context_prompt

    # Variables not exposed to the user.
    # Adds a prompt for post processing.
    post_processing_prompt = None
    # File to append to prompt
    include_file = None
    # TODO: add refresh-toolset to refresh the toolset if it has changed
    if interactive:
        run_interactive_loop(
            ai,
            console,
            system_prompt_rendered,
            prompt,
            post_processing_prompt,
            include_file,
            show_tool_output=show_tool_output,
        )
        return

    messages = build_initial_ask_messages(
        console,
        system_prompt_rendered,
        prompt,
        include_file,
    )

    response = ai.call(messages)

    messages = response.messages  # type: ignore # Update messages with the full history

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
