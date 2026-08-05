# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Command registration for the ``az aimanager`` command group.

This module is not auto-loaded; ``load_command_table`` is invoked from the extension's
top-level ``commands.py``.
"""

from azure.cli.core.commands import CliCommandType

from ._client_factory import cf_ai_managers, cf_ai_manager_namespaces


def load_command_table(self, _):
    aimanager_custom = CliCommandType(
        operations_tmpl='azext_aks_preview.aimanager.custom#{}',
        client_factory=cf_ai_managers,
    )

    with self.command_group('aimanager', aimanager_custom,
                            custom_command_type=aimanager_custom,
                            client_factory=cf_ai_managers, is_preview=True) as g:
        g.custom_command('create', 'aimanager_create', supports_no_wait=True)
        g.custom_command('update', 'aimanager_update')
        g.custom_show_command('show', 'aimanager_show')
        g.custom_command('delete', 'aimanager_delete', supports_no_wait=True, confirmation=True)
        g.custom_command('list', 'aimanager_list')

    namespace_custom = CliCommandType(
        operations_tmpl='azext_aks_preview.aimanager.custom#{}',
        client_factory=cf_ai_manager_namespaces,
    )

    with self.command_group('aimanager namespace', namespace_custom,
                            custom_command_type=namespace_custom,
                            client_factory=cf_ai_manager_namespaces, is_preview=True) as g:
        g.custom_command('add', 'aimanager_namespace_add', supports_no_wait=True)
        g.custom_command('update', 'aimanager_namespace_update', supports_no_wait=True)
        g.custom_show_command('show', 'aimanager_namespace_show')
        g.custom_command('delete', 'aimanager_namespace_delete',
                         supports_no_wait=True, confirmation=True)
        g.custom_command('list', 'aimanager_namespace_list')
