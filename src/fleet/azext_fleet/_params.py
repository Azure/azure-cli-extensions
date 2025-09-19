# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
import os
from argcomplete.completers import FilesCompleter
from azure.cli.core.commands.parameters import (
    tags_type,
    file_type,
    get_location_type,
    get_enum_type,
    get_three_state_flag,
    CLIArgumentType
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azext_fleet._validators import (
    validate_member_cluster_id,
    validate_kubernetes_version,
    validate_apiserver_subnet_id,
    validate_agent_subnet_id,
    validate_assign_identity,
    validate_update_strategy_name,
    validate_vm_size,
    validate_targets,
    validate_update_strategy_id,
    validate_labels,
    validate_enable_vnet_integration
)

labels_type = CLIArgumentType(
    metavar='KEY=VALUE',
    type=validate_labels,
    help='Space-separated labels: key[=value] [key[=value] ...]. Example: env=production region=us-west team=devops'
)


def load_arguments(self, _):
    with self.argument_context('fleet') as c:
        c.argument('name', options_list=['--name', '-n'], help='Specify the fleet name.')
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)

    with self.argument_context('fleet create') as c:
        c.argument('tags', tags_type)
        c.argument('dns_name_prefix', options_list=['--dns-name-prefix', '-p'], help='Prefix for host names that are created. If not specified, generate a host name using the managed cluster and resource group names.')
        c.argument('enable_private_cluster', action='store_true', help='Whether to create the Fleet hub as a private cluster or not.')
        c.argument('enable_vnet_integration', validator=validate_enable_vnet_integration, action='store_true', help='Whether to enable apiserver vnet integration for the Fleet hub or not.')
        c.argument('apiserver_subnet_id', validator=validate_apiserver_subnet_id, help='The subnet to be used when apiserver vnet integration is enabled.')
        c.argument('agent_subnet_id', validator=validate_agent_subnet_id, help='The ID of the subnet which the Fleet hub node will join on startup.')
        c.argument('enable_managed_identity', action='store_true', help='Enable system assigned managed identity (MSI) on the Fleet resource.')
        c.argument('assign_identity', validator=validate_assign_identity, help='With --enable-managed-identity, enable user assigned managed identity (MSI) on the Fleet resource by specifying the user assigned identity\'s resource Id.')
        c.argument('enable_hub', action='store_true', help='If set, the Fleet will be created with a hub cluster.')
        c.argument('vm_size', validator=validate_vm_size, help='The virtual machine size of the Fleet hub.')

    with self.argument_context('fleet update') as c:
        c.argument('tags', tags_type)
        c.argument('enable_managed_identity', arg_type=get_three_state_flag(),
                   help='Enable system assigned managed identity (MSI) on the Fleet resource.')
        c.argument('assign_identity', validator=validate_assign_identity,
                   help='With --enable-managed-identity, enable user assigned managed identity (MSI) on the Fleet resource. Specify the existing user assigned identity resource.')

    with self.argument_context('fleet get-credentials') as c:
        c.argument('context_name', options_list=['--context'], help='If specified, overwrite the default context name.')
        c.argument('path', options_list=['--file', '-f'], type=file_type, completer=FilesCompleter(),
                   default=os.path.join(os.path.expanduser('~'), '.kube', 'config'))

    with self.argument_context('fleet member') as c:
        c.argument('name', options_list=['--name', '-n'], help='Specify the fleet member name.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Specify the fleet name.')

    with self.argument_context('fleet member create') as c:
        c.argument('member_cluster_id', validator=validate_member_cluster_id)
        c.argument('update_group')
        c.argument(
            'member_labels',
            labels_type,
            options_list=['--member-labels', '--labels'],
            help='Space-separated labels in key=value format. Example: env=production region=us-west team=devops'
        )

    with self.argument_context('fleet member update') as c:
        c.argument('update_group')
        c.argument(
            'member_labels',
            labels_type,
            options_list=['--member-labels', '--labels'],
            help='Space-separated labels in key=value format. Example: env=production region=us-west team=devops'
        )

    with self.argument_context('fleet updaterun') as c:
        c.argument('name', options_list=['--name', '-n'], help='Specify name for the update run.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Specify the fleet name.')

    with self.argument_context('fleet updaterun create') as c:
        c.argument('upgrade_type', arg_type=get_enum_type(['Full', 'NodeImageOnly', 'ControlPlaneOnly']))
        c.argument('kubernetes_version', validator=validate_kubernetes_version)
        c.argument('node_image_selection', arg_type=get_enum_type(['Latest', 'Consistent']),
                   help='Node Image Selection is an option that lets you choose how your clusters\' nodes are upgraded')
        c.argument('stages',
                   help='Path to a JSON file that defines stages to upgrade a fleet, or a JSON string. See examples for further reference.')
        c.argument('update_strategy_name', validator=validate_update_strategy_name,
                   help='The name of the update strategy to use for this update run. If not specified, the default update strategy will be used.')

    with self.argument_context('fleet updaterun skip', is_preview=True) as c:
        c.argument('targets', nargs="+", validator=validate_targets,
                   help='Space-separated list of targets to skip. Targets must be of the form `targetType:targetName` such as Group:MyGroup. Valid target types are: [`Member`, `Group`, `Stage`, `AfterStageWait`]. The target type is case-sensitive.',
                   is_preview=True)

    with self.argument_context('fleet updatestrategy') as c:
        c.argument('name', options_list=['--name', '-n'], help='Specify name for the fleet update strategy.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Specify the fleet name.')

    with self.argument_context('fleet updatestrategy create') as c:
        c.argument('stages',
                   help='Path to a JSON file that defines an update strategy, or a JSON string.')

    with self.argument_context('fleet autoupgradeprofile') as c:
        c.argument('name', options_list=['--name', '-n'], help='Specify name for the auto upgrade profile.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Specify the fleet name.')

    with self.argument_context('fleet autoupgradeprofile create') as c:
        c.argument('update_strategy_id', validator=validate_update_strategy_id,
                   help='The resource ID of the update strategy that the auto upgrade profile should follow.')
        c.argument('channel', options_list=['--channel', '-c'], arg_type=get_enum_type(['Stable', 'Rapid', 'NodeImage', 'TargetKubernetesVersion']),
                   help='The auto upgrade channel type.')
        c.argument('node_image_selection', arg_type=get_enum_type(['Latest', 'Consistent']),
                   help='Node Image Selection is an option that lets you choose how your clusters\' nodes are upgraded.')
        c.argument(
            'target_kubernetes_version',
            options_list=['--target-kubernetes-version', '--tkv'],
            help=(
                'This is the target Kubernetes version for auto-upgrade. The format must be "{major version}.{minor version}". '
                'For example, "1.30". By default, this is empty. '
                'If the upgrade channel is set to TargetKubernetesVersion, this field must not be empty. '
                'If the upgrade channel is Rapid, Stable, or NodeImage, this field must be empty.'
            )
        )
        c.argument('disabled', action='store_true',
                   help='The disabled flag ensures auto upgrade profile does not run by default.')
        c.argument('long_term_support', action='store_true', options_list=['--long-term-support', '--lts'],
                   help='If upgrade channel is not TargetKubernetesVersion, this field must be False. If set to True: Fleet auto upgrade will generate update runs for patches of minor versions earlier than N-2 (where N is the latest supported minor version) if those minor versions support Long-Term Support (LTS). By default, this is set to False.')

    with self.argument_context('fleet autoupgradeprofile wait') as c:
        c.argument('auto_upgrade_profile_name', options_list=['--auto-upgrade-profile-name', '--profile-name'],
                   help='Specify name for the auto upgrade profile.')

    with self.argument_context('fleet autoupgradeprofile generate-update-run') as c:
        c.argument('resource_group_name', options_list=['--resource-group', '-g'], help='Name of the resource group.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Name of the fleet.')
        c.argument('auto_upgrade_profile_name', options_list=['--auto-upgrade-profile-name', '--profile-name', '--name', '-n'], help='Name of the auto upgrade profile.')

    with self.argument_context('fleet gate list') as c:
        c.argument('resource_group_name', options_list=['--resource-group', '-g'], help='Name of the resource group.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Name of the fleet.')
        c.argument('state_filter', options_list=['--state-filter', '--state'], help='Apply a filter on gate state. Valid values are: Pending, Skipped, Completed')

    with self.argument_context('fleet gate show') as c:
        c.argument('resource_group_name', options_list=['--resource-group', '-g'], help='Name of the resource group.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Name of the fleet.')
        c.argument('gate_name', options_list=['--gate-name', '--gate', '-n', '--name'], help='Name of the gate.')

    with self.argument_context('fleet gate update') as c:
        c.argument('resource_group_name', options_list=['--resource-group', '-g'], help='Name of the resource group.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Name of the fleet.')
        c.argument('gate_name', options_list=['--gate-name', '--gate', '-n'], help='Name of the gate.')
        c.argument(
            'gate_state',
            options_list=['--gate-state', '--gs', '--state'],
            help='The Gate State to patch. Valid values are: Completed.'
        )

    with self.argument_context('fleet gate approve') as c:
        c.argument('resource_group_name', options_list=['--resource-group', '-g'], help='Name of the resource group.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Name of the fleet.')
        c.argument('gate_name', options_list=['--gate-name', '--gate', '-n'], help='Name of the gate.')
