# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_k8s_configuration._client_factory import (cf_k8s_configuration, cf_k8s_configuration_operation)
from ._format import k8s_configuration_show_table_format, k8s_configuration_list_table_format


def load_command_table(self, _):

    k8s_configuration_sdk = CliCommandType(
        operations_tmpl='azext_k8s_configuration.vendored_sdks.operations#SourceControlConfigurationsOperations.{}',
        client_factory=cf_k8s_configuration)

    with self.command_group('k8s-configuration', k8s_configuration_sdk, client_factory=cf_k8s_configuration_operation) as g:
        g.custom_command('create', 'create_k8s_configuration')
        g.custom_command('update', 'update_k8s_configuration')
        g.custom_command('delete', 'delete_k8s_configuration', confirmation=True)
        g.custom_command('list', 'list_k8s_configuration', table_transformer=k8s_configuration_list_table_format)
        g.custom_show_command('show', 'show_k8s_configuration', table_transformer=k8s_configuration_show_table_format)
