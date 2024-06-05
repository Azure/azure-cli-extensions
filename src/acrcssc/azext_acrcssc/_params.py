# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core import AzCommandsLoader

from azure.cli.core.commands.parameters import (
    # tags_type,
    get_resource_name_completion_list,
    # quotes,
    get_three_state_flag,
    get_enum_type
)

from azure.cli.command_modules.acr._constants import (
    REGISTRY_RESOURCE_TYPE
)

from azure.cli.command_modules.acr._validators import validate_registry_name

def load_arguments(self: AzCommandsLoader, _):
    from .helper._constants import CSSCTaskTypes
    with self.argument_context("acr supply-chain task") as c:
        c.argument(
            'resource_group',
            options_list=['--resource-group', '-g'],
            help='Name of resource group. \
                You can configure the default group using `az configure --defaults group=<name>`',
            completer=get_resource_name_completion_list(REGISTRY_RESOURCE_TYPE),
            configured_default='acr',
            validator=validate_registry_name
        )
        c.argument(
            'registry_name',
            options_list=['--registry', '-r'],
            help='The name of the container registry. It should be specified in lower case. \
                You can configure the default registry name using `az configure --defaults acr=<registry name>`',
            completer=get_resource_name_completion_list(REGISTRY_RESOURCE_TYPE),
            configured_default='acr',
            validator=validate_registry_name)
        c.argument(
            "task_type",
            arg_type=get_enum_type(CSSCTaskTypes),
            options_list=['--task-type', '-t'],
            help='Allowed values: ContinuousPatchV1'
        )
        # Overwrite default shorthand of cmd to make availability for acr usage
        c.argument(
            'cmd',
            options_list=['--__cmd__'],
            required=False
        )
    with self.argument_context("acr supply-chain task create") as c:
        c.argument(
            "config",
            options_list=["--config"],
            help="Configuration file path containing the json schema for the \
                list of repositories and tags to filter within the registry. \
                Schema example:\
                {\"repositories\":[{\"repository\":\"alpine\",\"tags\":[\"tag1\",\"tag2\"],\
                \"enabled\":true},{\"repository\":\"python\",\"tags\":[\"*\"],\"enabled\":false}]}",
            required=True,
        )
        c.argument( # this is the timespan for the task, not taking cron as input right now
            "cadence",
            options_list=["--cadence"],
            help="Cadence to run the scan and patching task. \
                E.g. `<n>d` where <n> is the number of days between each run.",
            required=True
        )
        c.argument(
            "dryrun",
            options_list=["--dry-run"],
            help="Use this flag to see the qualifying repositories and tags that would be affected by the task.",
            arg_type=get_three_state_flag(),
            required=False
        )
    with self.argument_context("acr supply-chain task update") as c:
        c.argument(
            "config",
            options_list=["--config"],
            help="Configuration file path containing the json schema for \
                the list of repositories and tags to filter within the registry. \
                Example: {\"repositories\":[{\"repository\":\"alpine\",\"tags\":[\"tag1\",\"tag2\"]}]}",
            required=True,
        )
        c.argument( # this is the timespan for the task, not taking cron as input right now
            "cadence",
            options_list=["--cadence"],
            help="Cadence to run the scan and patching task. \
                E.g. `<n>d` where n is the number of days between each run.",
            required=True
        )
        c.argument(
            "dryrun",
            options_list=["--dry-run"],
            help="Use this flag to see the qualifying repositories \
                and tags that would be affected by the task.",
            arg_type=get_three_state_flag(),
            required=False
        )
    with self.argument_context("acr supply-chain task delete") as c:
         c.argument(
            "task_type",
            arg_type=get_enum_type(CSSCTaskTypes),
            options_list=["--task-type", "-t"],
            help="Type of task to be created. E.g. ContinuousPatch",
         )
    with self.argument_context("acr supply-chain task show") as c:
         c.argument(
            "task_type",
            arg_type=get_enum_type(CSSCTaskTypes),
            options_list=["--task-type", "-t"],
            help="Type of task to be created. E.g. ContinuousPatch",
         )
         