# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
from azure.cli.command_modules.acr._constants import REGISTRY_RESOURCE_TYPE
from azure.cli.command_modules.acr._validators import validate_registry_name
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list,
    get_three_state_flag, get_enum_type,
    resource_group_name_type
)
from .helper._constants import CONTINUOUSPATCH_SCHEDULE_MAX_DAYS


def load_arguments(self: AzCommandsLoader, _):
    from .helper._constants import CSSCTaskTypes
    from .helper._workflow_status import WorkflowTaskState

    with self.argument_context("acr supply-chain workflow") as c:
        c.argument('resource_group', arg_type=resource_group_name_type, completer=get_resource_name_completion_list(REGISTRY_RESOURCE_TYPE))
        c.argument('registry_name', options_list=['--registry', '-r'], help='The name of the container registry. It should be specified in lower case. You can configure the default registry name using `az configure --defaults acr=<registry name>`', completer=get_resource_name_completion_list(REGISTRY_RESOURCE_TYPE), configured_default='acr', validator=validate_registry_name)
        c.argument("workflow_type", arg_type=get_enum_type(CSSCTaskTypes), options_list=['--type', '-t'], help="Type of workflow task.", required=True)

    with self.argument_context("acr supply-chain workflow create") as c:
        c.argument("config", help="Configuration file path containing the json schema for the list of repositories and tags to filter within the registry. Schema example:{\"repositories\":[{\"repository\":\"alpine\",\"tags\":[\"tag1\",\"tag2\"],\"enabled\":true},{\"repository\":\"python\",\"tags\":[\"*\"],\"enabled\":false}], \"version\": \"v1\", \"tag-convention\": \"floating\"}. \"tag-convention\" is an optional property, values can be \"incremental\" (the default behavior, will increase the patch version of the tag, for example \"{repository}:{original-tag}-1\", \"{repository}:{original-tag}-2\", etc), or \"floating\" (will reuse the tag \"{repository}:{original-tag}-patched\" for patching)", required=True)
        c.argument("schedule", help=f"schedule to run the scan and patching task. E.g. `<n>d` where <n> is the number of days between each run. Max value is {CONTINUOUSPATCH_SCHEDULE_MAX_DAYS}d.", required=True)
        c.argument("run_immediately", help="Set this flag to trigger the immediate run of the selected workflow task. Default value: false.", arg_type=get_three_state_flag())
        c.argument("dryrun", options_list=["--dry-run"], help="Use this flag to see the qualifying repositories and tags that would be affected by the workflow. Default value: false. 'config' parameter is mandatory to provide with dry-run", arg_type=get_three_state_flag())

    with self.argument_context("acr supply-chain workflow update") as c:
        c.argument("config", help="Configuration file path containing the json schema for the list of repositories and tags to filter within the registry. Schema example:{\"repositories\":[{\"repository\":\"alpine\",\"tags\":[\"tag1\",\"tag2\"],\"enabled\":true},{\"repository\":\"python\",\"tags\":[\"*\"],\"enabled\":false}], \"version\": \"v1\", \"tag-convention\": \"floating\"}. \"tag-convention\" is an optional property, values can be \"incremental\" (the default behavior, will increase the patch version of the tag, for example \"{repository}:{original-tag}-1\", \"{repository}:{original-tag}-2\", etc), or \"floating\" (will reuse the tag \"{repository}:{original-tag}-patched\" for patching)")
        c.argument("schedule", help=f"schedule to run the scan and patching task. E.g. `<n>d` where n is the number of days between each run. Max value is {CONTINUOUSPATCH_SCHEDULE_MAX_DAYS}d.")
        c.argument("run_immediately", help="Set this flag to trigger the immediate run of the selected workflow task. Default value: false.", arg_type=get_three_state_flag())
        c.argument("dryrun", options_list=["--dry-run"], help="Use this flag to see the qualifying repositories and tags that would be affected by the workflow. Default value: false. 'config' parameter is mandatory to provide with dry-run", arg_type=get_three_state_flag())

    with self.argument_context("acr supply-chain workflow list") as c:
        c.argument("status", arg_type=get_enum_type(WorkflowTaskState), options_list=["--run-status"], help="Status to filter the supply-chain workflow image status.")

    with self.argument_context("acr supply-chain workflow delete") as c:
        c.argument("yes", options_list=["--yes", "-y"], help="Proceed with the deletion without user confirmation")
