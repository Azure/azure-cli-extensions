# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argparse import _AppendAction  # pylint: disable=protected-access

from knack.util import CLIError

from azure.cli.core.commands.validators import validate_tags
from azure.cli.core.commands.client_factory import get_subscription_id, get_mgmt_service_client
from azure.cli.core.profiles import ResourceType

from .profiles import CUSTOM_NW_CONNECTION_MONITOR


def get_network_watcher_from_location(remove=False, watcher_name='watcher_name',
                                      rg_name='watcher_rg'):
    def _validator(cmd, namespace):
        from msrestazure.tools import parse_resource_id

        location = namespace.location
        network_client = get_mgmt_service_client(cmd.cli_ctx, CUSTOM_NW_CONNECTION_MONITOR).network_watchers
        watcher = next((x for x in network_client.list_all() if x.location.lower() == location.lower()), None)
        if not watcher:
            raise CLIError("network watcher is not enabled for region '{}'.".format(location))
        id_parts = parse_resource_id(watcher.id)
        setattr(namespace, rg_name, id_parts['resource_group'])
        setattr(namespace, watcher_name, id_parts['name'])

        if remove:
            del namespace.location

    return _validator


def process_nw_cm_v1_create_namespace(cmd, namespace):
    from msrestazure.tools import is_valid_resource_id, resource_id, parse_resource_id

    validate_tags(namespace)

    compute_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_COMPUTE).virtual_machines
    vm_name = parse_resource_id(namespace.source_resource)['name']
    rg = namespace.resource_group_name or parse_resource_id(namespace.source_resource).get('resource_group', None)
    if not rg:
        raise CLIError('usage error: --source-resource ID | --source-resource NAME --resource-group NAME')
    vm = compute_client.get(rg, vm_name)
    namespace.location = vm.location  # pylint: disable=no-member
    get_network_watcher_from_location()(cmd, namespace)

    if namespace.source_resource and not is_valid_resource_id(namespace.source_resource):
        kwargs = {
            'subscription': get_subscription_id(cmd.cli_ctx),
            'resource_group': rg,
            'namespace': 'Microsoft.Compute',
            'type': 'virtualMachines',
            'name': namespace.source_resource
        }
        namespace.source_resource = resource_id(**kwargs)

    if namespace.dest_resource and not is_valid_resource_id(namespace.dest_resource):
        kwargs = {
            'subscription': get_subscription_id(cmd.cli_ctx),
            'resource_group': namespace.resource_group_name,
            'namespace': 'Microsoft.Compute',
            'type': 'virtualMachines',
            'name': namespace.dest_resource
        }
        namespace.dest_resource = resource_id(**kwargs)


def process_nw_cm_v2_create_namespace(cmd, namespace):
    if namespace.location is None:
        raise CLIError('usage error: --location is required when create V2 connection monitor')
    return get_network_watcher_from_location()(cmd, namespace)


def process_nw_cm_create_namespace(cmd, namespace):

    if namespace.source_resource is None:
        # V2 parameter set
        return process_nw_cm_v2_create_namespace(cmd, namespace)
    else:
        # V1 parameter set
        return process_nw_cm_v1_create_namespace(cmd, namespace)


def process_nw_cm_v2_endpoint_create_namespace(cmd, namespace):
    filter_type, filter_items = namespace.filter_type, namespace.filter_items
    if (filter_type and not filter_items) or (not filter_type and filter_items):
        raise CLIError('usage error: --filter-type and --filter-item must be present at the same time.')

    dest_test_groups, source_test_groups = namespace.dest_test_groups, namespace.source_test_groups
    if dest_test_groups is None and source_test_groups is None:
        raise CLIError('usage error: endpoint has to be referenced in at least one existing test group '
                       'via --dest-test-groups/--source-test-groups')

    return process_nw_cm_v2_create_namespace(cmd, namespace)


# pylint: disable=protected-access
class NWConnectionMonitorEndpointFilterItemAction(_AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        ConnectionMonitorEndpointFilterItem = namespace._cmd.get_models('ConnectionMonitorEndpointFilterItem')

        if not namespace.filter_items:
            namespace.filter_items = []

        filter_item = ConnectionMonitorEndpointFilterItem()

        for item in values:
            try:
                key, val = item.split('=', 1)

                if hasattr(filter_item, key):
                    setattr(filter_item, key, val)
                else:
                    raise CLIError(
                        "usage error: '{}' is not a valid property of ConnectionMonitorEndpointFilterItem".format(key))
            except ValueError:
                raise CLIError(
                    'usage error: {} PropertyName=PropertyValue [PropertyName=PropertyValue ...]'.format(option_string))

        namespace.filter_items.append(filter_item)
