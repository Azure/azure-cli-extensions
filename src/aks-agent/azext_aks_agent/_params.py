# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.commands.parameters import get_enum_type


# pylint: disable=too-many-statements,too-many-lines
def load_arguments(self, _):
    with self.argument_context("aks agent") as c:
        c.positional(
            "prompt",
            nargs='?',
            help="Ask any question and answer using available tools.",
            required=False,
        )
        c.argument(
            "resource_group_name",
            options_list=["--resource-group", "-g"],
            help="Name of resource group.",
        )
        c.argument(
            "cluster_name",
            options_list=["--name", "-n"],
            help="Name of the managed cluster.",
        )
        c.argument(
            "namespace",
            options_list=["--namespace"],
            help="The Kubernetes namespace where the AKS Agent is deployed. Required for cluster mode.",
            required=False,
        )
        c.argument(
            "max_steps",
            type=int,
            default=40,
            required=False,
            help="Maximum number of steps the LLM can take to investigate the issue.",
        )
        c.argument(
            "model",
            help=" Specify the LLM provider and model or deployment to use for the AI assistant.",
            required=False,
            type=str,
        )
        c.argument(
            "no_interactive",
            help="Disable interactive mode. When set, the agent will not prompt for input and will run in batch mode.",
            action="store_true",
        )
        c.argument(
            "mode",
            arg_type=get_enum_type(["cluster", "client"]),
            help="The mode decides how the agent is deployed.",
            default="cluster",
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
        c.argument(
            "status",
            options_list=["--status"],
            action="store_true",
            help="Show AKS agent configuration and status information.",
        )

    with self.argument_context("aks agent-init") as c:
        c.argument(
            "resource_group_name",
            options_list=["--resource-group", "-g"],
            help="Name of resource group.",
        )
        c.argument(
            "cluster_name",
            options_list=["--name", "-n"],
            help="Name of the managed cluster.",
        )

    with self.argument_context("aks agent-cleanup") as c:
        c.argument(
            "resource_group_name",
            options_list=["--resource-group", "-g"],
            help="Name of resource group.",
        )
        c.argument(
            "cluster_name",
            options_list=["--name", "-n"],
            help="Name of the managed cluster.",
        )
        c.argument(
            "namespace",
            options_list=["--namespace"],
            help="The Kubernetes namespace where the AKS Agent is deployed. Required for cluster mode.",
            required=False,
        )
        c.argument(
            "mode",
            arg_type=get_enum_type(["cluster", "client"]),
            help="The mode decides how the agent is deployed.",
            default="cluster",
        )
