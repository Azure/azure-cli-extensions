# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (
    get_enum_type,
    get_three_state_flag,
    tags_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from . import consts

from .action import (
    AddConfigurationSettings,
    AddConfigurationProtectedSettings
)


def load_arguments(self, _):
    with self.argument_context(consts.EXTENSION_NAME) as c:
        c.argument('tags', tags_type)
        c.argument('location',
                   validator=get_default_location_from_resource_group)
        c.argument('name',
                   options_list=['--name', '-n'],
                   help='Name of the extension instance')
        c.argument('extension_type',
                   help='Name of the extension type.')
        c.argument('cluster_name',
                   options_list=['--cluster-name', '-c'],
                   help='Name of the Kubernetes cluster')
        c.argument('cluster_type',
                   arg_type=get_enum_type(['connectedClusters', 'managedClusters', 'appliances']),
                   help='Specify Arc clusters or AKS managed clusters or Arc appliances.')
        c.argument('scope',
                   arg_type=get_enum_type(['cluster', 'namespace']),
                   help='Specify the extension scope.')
        c.argument('auto_upgrade_minor_version',
                   arg_group="Version",
                   options_list=['--auto-upgrade-minor-version', '--auto-upgrade'],
                   arg_type=get_three_state_flag(),
                   help='Automatically upgrade minor version of the extension instance.')
        c.argument('version',
                   arg_group="Version",
                   help='Specify the version to install for the extension instance if'
                   ' --auto-upgrade-minor-version is not enabled.')
        c.argument('release_train',
                   arg_group="Version",
                   help='Specify the release train for the extension type.')
        c.argument('configuration_settings',
                   arg_group="Configuration",
                   options_list=['--configuration-settings', '--config'],
                   action=AddConfigurationSettings,
                   nargs='+',
                   help='Configuration Settings as key=value pair.  Repeat parameter for each setting')
        c.argument('configuration_protected_settings',
                   arg_group="Configuration",
                   options_list=['--configuration-protected-settings', '--config-protected'],
                   action=AddConfigurationProtectedSettings,
                   nargs='+',
                   help='Configuration Protected Settings as key=value pair.  Repeat parameter for each setting')
        c.argument('configuration_settings_file',
                   arg_group="Configuration",
                   options_list=['--configuration-settings-file', '--config-file'],
                   help='JSON file path for configuration-settings')
        c.argument('configuration_protected_settings_file',
                   arg_group="Configuration",
                   options_list=['--configuration-protected-settings-file', '--config-protected-file'],
                   help='JSON file path for configuration-protected-settings')
        c.argument('release_namespace',
                   help='Specify the namespace to install the extension release.')
        c.argument('target_namespace',
                   help='Specify the target namespace to install to for the extension instance. This'
                   ' parameter is required if extension scope is set to \'namespace\'')
