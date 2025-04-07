# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (
    get_enum_type,
    get_three_state_flag
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from . import consts

from .action import (
    AddConfigurationSettings,
    AddConfigurationProtectedSettings,
)


def load_arguments(self, _):
    with self.argument_context(consts.EXTENSION_NAME) as c:
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
                   arg_type=get_enum_type(['connectedClusters', 'managedClusters', 'appliances', 'provisionedClusters']),
                   options_list=['--cluster-type', '-t'],
                   help='Specify Arc clusters or AKS managed clusters or Arc appliances or provisionedClusters.')
        c.argument('cluster_resource_provider',
                   options_list=['--cluster-resource-provider', '--cluster-rp'],
                   help='Cluster Resource Provider name for this clusterType (Required for provisionedClusters)')
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
                   options_list=['--configuration-settings', '--config', c.deprecate(target='--config-settings', redirect='--configuration-settings')],
                   action=AddConfigurationSettings,
                   nargs='+',
                   help='Configuration Settings as key=value pair.  Repeat parameter for each setting. Do not use this for secrets, as this value is returned in response.')
        c.argument('configuration_protected_settings',
                   arg_group="Configuration",
                   options_list=['--config-protected-settings', '--config-protected', c.deprecate(target='--configuration-protected-settings', redirect='--config-protected-settings')],
                   action=AddConfigurationProtectedSettings,
                   nargs='+',
                   help='Configuration Protected Settings as key=value pair.  Repeat parameter for each setting.  Only the key is returned in response, the value is not.')
        c.argument('configuration_settings_file',
                   arg_group="Configuration",
                   options_list=['--config-settings-file', '--config-file', c.deprecate(target='--configuration-settings-file', redirect='--config-settings-file')],
                   help='JSON file path for configuration-settings')
        c.argument('configuration_protected_settings_file',
                   arg_group="Configuration",
                   options_list=['--config-protected-settings-file', '--config-protected-file', c.deprecate(target='--configuration-protected-settings-file', redirect='--config-protected-file')],
                   help='JSON file path for configuration-protected-settings')
        c.argument('release_namespace',
                   help='Specify the namespace to install the extension release.')
        c.argument('target_namespace',
                   help='Specify the target namespace to install to for the extension instance. This'
                   ' parameter is required if extension scope is set to \'namespace\'')
        c.argument('plan_name',
                   arg_group="Marketplace",
                   options_list=['--plan-name'],
                   help='The plan name is referring to the Plan ID of the extension that is being taken from Marketplace portal under Usage Information + Support')
        c.argument('plan_product',
                   arg_group="Marketplace",
                   options_list=['--plan-product'],
                   help='The plan product is referring to the Product ID of the extension that is being taken from Marketplace portal under Usage Information + Support. An example of this is the name of the ISV offering used.')
        c.argument('plan_publisher',
                   arg_group="Marketplace",
                   options_list=['--plan-publisher'],
                   help='The plan publisher is referring to the Publisher ID of the extension that is being taken from Marketplace portal under Usage Information + Support')
    with self.argument_context(f"{consts.EXTENSION_NAME} update") as c:
        c.argument('yes',
                   options_list=['--yes', '-y'],
                   help='Ignore confirmation prompts')

    with self.argument_context(f"{consts.EXTENSION_NAME} delete") as c:
        c.argument('yes',
                   options_list=['--yes', '-y'],
                   help='Ignore confirmation prompts')
        c.argument('force',
                   help='Specify whether to force delete the extension from the cluster.')

    with self.argument_context(f"{consts.EXTENSION_NAME} extension-types") as c:
        c.argument('cluster_name',
                   options_list=['--cluster-name', '-c'],
                   help='Name of the Kubernetes cluster')
        c.argument('cluster_type',
                   arg_type=get_enum_type(['connectedClusters', 'managedClusters', 'appliances']),
                   options_list=['--cluster-type', '-t'],
                   help='Specify Arc clusters or AKS managed clusters or Arc appliances.')
        c.argument('extension_type',
                   help='Name of the extension type.')
        c.argument('location',
                   validator=get_default_location_from_resource_group,
                   help='Name of the location. Values from: `az account list-locations`')
        c.argument('version',
                   help='Version for the extension type.')
        c.argument('plan_name',
                   arg_group="Marketplace",
                   options_list=['--plan-name'],
                   help='The plan name is referring to the Marketplace Plan ID of the extension.')
        c.argument('plan_product',
                   arg_group="Marketplace",
                   options_list=['--plan-product'],
                   help='The plan product is referring to the Marketplace Product ID of the extension.')
        c.argument('plan_publisher',
                   arg_group="Marketplace",
                   options_list=['--plan-publisher'],
                   help='The plan publisher is referring to the Marketplace Publisher ID of the extension')
        c.argument('major_version',
                   help='Filter results by only the major version of an extension type. For example if 1 is specified, all versions with major version 1 (1.1, 1.1.2) will be shown. The default value is None')
        c.argument('show_latest',
                   arg_type=get_three_state_flag(),
                   help='Filter results by only the latest version. For example, if this flag is used the latest version of the extensionType will be shown.')
