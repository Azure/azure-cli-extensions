# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_functionapp._client_factory import cf_functionapp


def load_command_table(self, _):

    functionapp_sdk = CliCommandType(
        operations_tmpl='azext_functionapp.vendored_sdks.operations#WebAppsOperations.{}',
        client_factory=cf_functionapp)


    with self.command_group('functionapp devops-pipeline', functionapp_sdk, client_factory=cf_functionapp) as g:
        g.custom_command('create', 'create_devops_pipeline')


    with self.command_group('functionapp', is_preview=True):
        pass

