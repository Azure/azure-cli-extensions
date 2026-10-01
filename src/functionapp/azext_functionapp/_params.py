# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.local_context import LocalContextAttribute, LocalContextAction
from azure.cli.core.commands.parameters import get_three_state_flag

from ._validators import (
    validate_dotnet_ten_linux_fx_version_for_config_set,
    validate_dotnet_ten_runtime_for_create
)


def load_arguments(self, _):
    # pylint: disable=line-too-long
    # PARAMETER REGISTRATION

    with self.argument_context('functionapp devops-pipeline') as c:
        c.argument('functionapp_name', help="Name of the Azure Function App that you want to use", required=False,
                   local_context_attribute=LocalContextAttribute(name='functionapp_name',
                                                                 actions=[LocalContextAction.GET]))
        c.argument('organization_name', help="Name of the Azure DevOps organization that you want to use",
                   required=False)
        c.argument('project_name', help="Name of the Azure DevOps project that you want to use", required=False)
        c.argument('repository_name', help="Name of the Azure DevOps repository that you want to use", required=False)
        c.argument('overwrite_yaml', help="If you have an existing yaml, should it be overwritten?",
                   arg_type=get_three_state_flag(return_label=True), required=False)
        c.argument('allow_force_push',
                   help="If Azure DevOps repository is not clean, should it overwrite remote content?",
                   arg_type=get_three_state_flag(return_label=True), required=False)
        c.argument('github_pat', help="Github personal access token for creating pipeline from Github repository",
                   required=False)
        c.argument('github_repository', help="Fullname of your Github repository (e.g. Azure/azure-cli)",
                   required=False)

    with self.argument_context('functionapp config set') as c:
        c.argument('linux_fx_version', validator=validate_dotnet_ten_linux_fx_version_for_config_set)

    with self.argument_context('functionapp create') as c:
        c.argument('runtime_version', validator=validate_dotnet_ten_runtime_for_create)
