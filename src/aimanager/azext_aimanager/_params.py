# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
from azure.cli.core.commands.parameters import (
    tags_type,
    get_location_type,
    get_enum_type,
    get_resource_name_completion_list,
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azext_aimanager.constants import DELETE_POLICIES
from azext_aimanager._validators import (
    validate_ai_manager_name,
    validate_namespace_name,
    validate_labels,
    validate_annotations,
)


def load_arguments(self, _):
    with self.argument_context('aimanager') as c:
        c.argument('ai_manager_name', options_list=['--name', '-n'],
                   validator=validate_ai_manager_name,
                   help='The name of the AI Manager resource.',
                   completer=get_resource_name_completion_list('Microsoft.ContainerService/aiManagers'))

    for scope in ['aimanager create', 'aimanager update']:
        with self.argument_context(scope) as c:
            c.argument('tags', arg_type=tags_type, help='The tags to set to the AI Manager.')
            c.argument('delete_policy', arg_type=get_enum_type(DELETE_POLICIES),
                       help='Delete options of the AI Manager. Defaults to Delete.')
            c.argument('aks_custom_headers', options_list=['--aks-custom-headers'],
                       help='Comma-separated key=value pairs to specify custom headers.')

    with self.argument_context('aimanager create') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)

    with self.argument_context('aimanager list') as c:
        c.ignore('ai_manager_name')

    with self.argument_context('aimanager get-credentials') as c:
        c.argument('path', options_list=['--file', '-f'],
                   help='Kubernetes configuration file to update. Use "-" to print YAML to stdout instead.')
        c.argument('overwrite_existing', action='store_true',
                   help='Overwrite any existing cluster entry with the same name.')
        c.argument('context_name',
                   help='If specified, overwrite the default context name.')
        c.argument('aks_custom_headers', options_list=['--aks-custom-headers'],
                   help='Comma-separated key=value pairs to specify custom headers.')

    with self.argument_context('aimanager namespace') as c:
        c.argument('ai_manager_name', options_list=['--manager', '-m'],
                   validator=validate_ai_manager_name,
                   help='The name of the AI Manager resource.')
        c.argument('namespace_name', options_list=['--name', '-n'],
                   validator=validate_namespace_name,
                   help='The name of the AI Manager namespace.')

    for scope in ['aimanager namespace add', 'aimanager namespace update']:
        with self.argument_context(scope) as c:
            c.argument('labels', nargs='*', validator=validate_labels,
                       help='Space-separated labels (key=value) applied to the Kubernetes namespace.')
            c.argument('annotations', nargs='*', validator=validate_annotations,
                       help='Space-separated annotations (key=value) applied to the Kubernetes namespace.')
            c.argument('aks_custom_headers', options_list=['--aks-custom-headers'],
                       help='Comma-separated key=value pairs to specify custom headers.')

    with self.argument_context('aimanager namespace get-credentials') as c:
        c.argument('path', options_list=['--file', '-f'],
                   help='Kubernetes configuration file to update. Use "-" to print YAML to stdout instead.')
        c.argument('overwrite_existing', action='store_true',
                   help='Overwrite any existing cluster entry with the same name.')
        c.argument('context_name',
                   help='If specified, overwrite the default context name.')
        c.argument('aks_custom_headers', options_list=['--aks-custom-headers'],
                   help='Comma-separated key=value pairs to specify custom headers.')
