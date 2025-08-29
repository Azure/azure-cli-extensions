# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-statements,too-many-lines
import os.path

from azure.cli.core.api import get_config_dir

from azext_aks_agent._consts import CONST_AGENT_CONFIG_FILE_NAME

from azext_aks_agent._validators import validate_agent_config_file


def load_arguments(self, _):
    with self.argument_context("aks agent") as c:
        c.positional(
            "prompt",
            help="Ask any question and answer using available tools.",
        )
        c.argument(
            "resource_group_name",
            options_list=["--resource-group", "-g"],
            help="Name of resource group.",
            required=False,
        )
        c.argument(
            "name",
            options_list=["--name", "-n"],
            help="Name of the managed cluster.",
            required=False,
        )
        c.argument(
            "max_steps",
            type=int,
            default=10,
            required=False,
            help="Maximum number of steps the LLM can take to investigate the issue.",
        )
        c.argument(
            "config_file",
            default=os.path.join(get_config_dir(), CONST_AGENT_CONFIG_FILE_NAME),
            validator=validate_agent_config_file,
            required=False,
            help="Path to the config file.",
        )
        c.argument(
            "model",
            help="The model to use for the LLM.",
            required=False,
            type=str,
        )
        c.argument(
            "api-key",
            help="API key to use for the LLM (if not given, uses environment variables AZURE_API_KEY, OPENAI_API_KEY)",
            required=False,
            type=str,
        )
        c.argument(
            "no_interactive",
            help="Disable interactive mode. When set, the agent will not prompt for input and will run in batch mode.",
            action="store_true",
        )
        c.argument(
            "no_echo_request",
            help="Disable echoing back the question provided to AKS Agent in the output.",
            action="store_true",
        )
        c.argument(
            "show_tool_output",
            help="Show the output of each tool that was called.",
            action="store_true",
        )
        c.argument(
            "refresh_toolsets",
            help="Refresh the toolsets status.",
            action="store_true",
        )
