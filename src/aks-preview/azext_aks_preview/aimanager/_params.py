# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Argument definitions for the ``az aimanager`` command group."""

from azure.cli.core.commands.parameters import (
    get_location_type, tags_type, get_enum_type, get_resource_name_completion_list)


def load_arguments(self, _):
    with self.argument_context('aimanager') as c:
        c.argument('ai_manager_name', options_list=['--name', '-n'],
                   help='The name of the AI Manager resource.',
                   completer=get_resource_name_completion_list('Microsoft.ContainerService/aiManagers'))

    with self.argument_context('aimanager create') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', arg_type=tags_type)
        c.argument('delete_policy', arg_type=get_enum_type(['Keep', 'Delete']),
                   help="Delete options of the AI Manager. Defaults to Delete.")

    with self.argument_context('aimanager update') as c:
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('aimanager list') as c:
        c.ignore('ai_manager_name')

    with self.argument_context('aimanager namespace') as c:
        c.argument('ai_manager_name', options_list=['--manager', '-m'],
                   help='The name of the AI Manager resource.')
        c.argument('namespace_name', options_list=['--name', '-n'],
                   help='The name of the AI Manager namespace.')

    for scope in ['aimanager namespace add', 'aimanager namespace update']:
        with self.argument_context(scope) as c:
            c.argument('labels', tags_type, help='Labels applied to the Kubernetes namespace.')
            c.argument('annotations', tags_type,
                       help='Annotations applied to the Kubernetes namespace.')
