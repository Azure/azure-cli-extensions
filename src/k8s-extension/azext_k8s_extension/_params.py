# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    get_enum_type,
    get_three_state_flag,
    tags_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group

from azext_k8s_extension.action import (
    AddConfigurationSettings,
    AddConfigurationProtectedSettings
)


def load_arguments(self, _):
    k8s_extension_type = CLIArgumentType(options_list='--k8s-extension-name', help='Name of the K8s-extension.',
                                         id_part='name')

    with self.argument_context('k8s-extension') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('k8s-extension', k8s_extension_type, options_list=['--name', '-n'])
        c.argument('cluster_name', options_list=['--cluster-name', '-c'], help='Name of the Kubernetes cluster')
        c.argument('cluster_type', arg_type=get_enum_type(['connectedClusters', 'managedClusters']),
                   help='Specify Arc clusters or AKS managed clusters.')
        c.argument('scope', arg_type=get_enum_type(['cluster', 'namespace']),
                   help='Specify the extension scope.')
        c.argument('auto_upgrade_minor_version', arg_type=get_three_state_flag(),
                   help='Automatically upgrade minor version of the extension instance.')
        c.argument('configuration_settings', action=AddConfigurationSettings, nargs='+',
                   help='Configuration Settings as key=value pair.  Repeat parameter for each setting')
        c.argument('configuration_protected_settings', action=AddConfigurationProtectedSettings, nargs='+',
                   help='Configuration Protected Settings as key=value pair.  Repeat parameter for each setting')
        c.argument('configuration_settings_file', help='JSON file path for configuration-settings')
        c.argument('configuration_protected_settings_file',
                   help='JSON file path for configuration-protected-settings')

    with self.argument_context('k8s-extension list') as c:
        c.argument('k8s-extension', k8s_extension_type, id_part=None)
