# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_k8sconfiguration._client_factory import (cf_k8sconfiguration, cf_k8sconfiguration_operation)


def load_command_table(self, _):

    k8sconfiguration_sdk = CliCommandType(
        operations_tmpl='azext_k8sconfiguration.vendored_sdks.operations#SourceControlConfigurationsOperations.{}',
        client_factory=cf_k8sconfiguration)

    with self.command_group('k8sconfiguration', k8sconfiguration_sdk, client_factory=cf_k8sconfiguration_operation,
                            is_preview=True) \
            as g:
        g.custom_command('create', 'create_k8sconfiguration')
        g.custom_command('update', 'update_k8sconfiguration')
        g.custom_command('delete', 'delete_k8sconfiguration', confirmation=True)
        g.custom_command('list', 'list_k8sconfiguration')
        g.custom_show_command('show', 'show_k8sconfiguration')
