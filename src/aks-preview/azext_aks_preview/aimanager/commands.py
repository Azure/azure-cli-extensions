# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Command registration for the ``az aimanager`` command group.

Mirrors the ``aks namespace`` registration: each command group is anchored on the vendored
SDK operations class, while the individual commands are wired to the custom handlers.
This module is loaded from the extension's top-level ``commands.py``.
"""

from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_ai_managers, cf_ai_manager_namespaces


def load_command_table(self, _):
    aimanager_custom = CliCommandType(
        operations_tmpl='azext_aks_preview.aimanager.custom#{}',
    )

    ai_managers_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.aimanager.vendored_sdk.operations.'
        '_operations#AIManagersOperations.{}',
        client_factory=cf_ai_managers,
    )

    ai_manager_namespaces_sdk = CliCommandType(
        operations_tmpl='azext_aks_preview.aimanager.vendored_sdk.operations.'
        '_operations#AIManagerNamespacesOperations.{}',
        client_factory=cf_ai_manager_namespaces,
    )

    with self.command_group('aimanager', ai_managers_sdk,
                            custom_command_type=aimanager_custom,
                            client_factory=cf_ai_managers, is_preview=True) as g:
        g.custom_command('create', 'aimanager_create', supports_no_wait=True)
        g.custom_command('update', 'aimanager_update', supports_no_wait=True)
        g.custom_show_command('show', 'aimanager_show')
        g.custom_command('list', 'aimanager_list')
        g.custom_command('delete', 'aimanager_delete', supports_no_wait=True, confirmation=True)

    with self.command_group('aimanager namespace', ai_manager_namespaces_sdk,
                            custom_command_type=aimanager_custom,
                            client_factory=cf_ai_manager_namespaces, is_preview=True) as g:
        g.custom_command('add', 'aimanager_namespace_add', supports_no_wait=True)
        g.custom_command('update', 'aimanager_namespace_update', supports_no_wait=True)
        g.custom_show_command('show', 'aimanager_namespace_show')
        g.custom_command('list', 'aimanager_namespace_list')
        g.custom_command('delete', 'aimanager_namespace_delete',
                         supports_no_wait=True, confirmation=True)
