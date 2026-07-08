# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Command registration — the classic equivalent of the wiring in `commands.py:102`.

This maps CLI commands to the custom functions and the SDK client factory. It is
NOT auto-loaded; to activate, call `load_command_table(self, _)` from the
extension's real `commands.py` and `load_arguments` from `_params.py`.
"""

from azure.cli.core.commands import CliCommandType
from .custom import (
    aks_inference_create, aks_inference_show, aks_inference_delete, aks_inference_list)
from ._client_factory import cf_ai_managers, cf_ai_manager_namespaces


def load_command_table(self, _):
    aimanager_custom = CliCommandType(
        operations_tmpl='azext_aks_preview.aks_inference.custom#{}',
        client_factory=cf_ai_managers,
    )

    with self.command_group('aks inference', aimanager_custom,
                            custom_command_type=aimanager_custom,
                            client_factory=cf_ai_managers, is_preview=True) as g:
        g.custom_command('create', 'aks_inference_create', supports_no_wait=True)
        g.custom_show_command('show', 'aks_inference_show')
        g.custom_command('delete', 'aks_inference_delete', supports_no_wait=True, confirmation=True)
        g.custom_command('list', 'aks_inference_list')

    namespace_custom = CliCommandType(
        operations_tmpl='azext_aks_preview.aks_inference.custom#{}',
        client_factory=cf_ai_manager_namespaces,
    )

    with self.command_group('aks inference namespace', namespace_custom,
                            custom_command_type=namespace_custom,
                            client_factory=cf_ai_manager_namespaces, is_preview=True) as g:
        g.custom_command('create', 'aks_inference_namespace_create', supports_no_wait=True)
        g.custom_show_command('show', 'aks_inference_namespace_show')
        g.custom_command('delete', 'aks_inference_namespace_delete',
                         supports_no_wait=True, confirmation=True)
        g.custom_command('list', 'aks_inference_namespace_list')
