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


def _resolve_api_version(rcf, resource_provider_namespace, parent_resource_path, resource_type):
    """
    This is copied from src/azure-cli/azure/cli/command_modules/resource/custom.py in Azure/azure-cli
    """
    from azure.cli.core.parser import IncorrectUsageError

    provider = rcf.providers.get(resource_provider_namespace)

    # If available, we will use parent resource's api-version
    resource_type_str = (parent_resource_path.split('/')[0] if parent_resource_path else resource_type)

    rt = [t for t in provider.resource_types
          if t.resource_type.lower() == resource_type_str.lower()]
    if not rt:
        raise IncorrectUsageError('Resource type {} not found.'.format(resource_type_str))
    if len(rt) == 1 and rt[0].api_versions:
        npv = [v for v in rt[0].api_versions if 'preview' not in v.lower()]
        return npv[0] if npv else rt[0].api_versions[0]
    raise IncorrectUsageError(
        'API version is required and could not be resolved for resource {}'.format(resource_type))


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

    if namespace.location is None:  # location is None only occurs in creating a V2 connection monitor
        endpoint_source_resource_id = namespace.endpoint_source_resource_id

        from msrestazure.tools import is_valid_resource_id, parse_resource_id
        from azure.mgmt.resource import ResourceManagementClient

        # parse and verify endpoint_source_resource_id
        if endpoint_source_resource_id is None:
            raise CLIError('usage error: '
                           '--location/--endpoint-source-resource-id is required to create a V2 connection monitor')
        if is_valid_resource_id(endpoint_source_resource_id) is False:
            raise CLIError('usage error: "{}" is not a valid resource id'.format(endpoint_source_resource_id))

        resource = parse_resource_id(namespace.endpoint_source_resource_id)
        resource_client = get_mgmt_service_client(cmd.cli_ctx, ResourceManagementClient)
        resource_api_version = _resolve_api_version(resource_client,
                                                    resource['namespace'],
                                                    resource['resource_parent'],
                                                    resource['resource_type'])
        resource = resource_client.resources.get_by_id(namespace.endpoint_source_resource_id, resource_api_version)

        namespace.location = resource.location
        if namespace.location is None:
            raise CLIError("Can not get location from --endpoint-source-resource-id")

    v2_required_parameter_set = ['endpoint_source_name', 'endpoint_dest_name', 'test_config_name']
    for p in v2_required_parameter_set:
        if not hasattr(namespace, p) or getattr(namespace, p) is None:
            raise CLIError(
                'usage error: --{} is required to create a V2 connection monitor'.format(p.replace('_', '-')))
    if namespace.test_config_protocol is None:
        raise CLIError('usage error: --protocol is required to create a test configuration for V2 connection monitor')

    v2_optional_parameter_set = ['workspace_ids']
    if namespace.output_type is not None:
        tmp = [p for p in v2_optional_parameter_set if getattr(namespace, p) is None]
        if v2_optional_parameter_set == tmp:
            raise CLIError('usage error: --output-type is specified but no other resource id provided')

    return get_network_watcher_from_location()(cmd, namespace)


def process_nw_cm_create_namespace(cmd, namespace):
    # V2 parameter set
    if namespace.source_resource is None:
        return process_nw_cm_v2_create_namespace(cmd, namespace)

    # V1 parameter set
    return process_nw_cm_v1_create_namespace(cmd, namespace)


def process_nw_cm_v2_endpoint_namespace(cmd, namespace):
    if hasattr(namespace, 'filter_type') or hasattr(namespace, 'filter_items'):
        filter_type, filter_items = namespace.filter_type, namespace.filter_items
        if (filter_type and not filter_items) or (not filter_type and filter_items):
            raise CLIError('usage error: --filter-type and --filter-item must be present at the same time.')

    if hasattr(namespace, 'dest_test_groups') or hasattr(namespace, 'source_test_groups'):
        dest_test_groups, source_test_groups = namespace.dest_test_groups, namespace.source_test_groups
        if dest_test_groups is None and source_test_groups is None:
            raise CLIError('usage error: endpoint has to be referenced from at least one existing test group '
                           'via --dest-test-groups/--source-test-groups')

    return get_network_watcher_from_location()(cmd, namespace)


def process_nw_cm_v2_output_namespace(cmd, namespace):
    v2_output_optional_parameter_set = ['workspace_id']
    if hasattr(namespace, 'out_type') and namespace.out_type is not None:
        tmp = [p for p in v2_output_optional_parameter_set if getattr(namespace, p) is None]
        if v2_output_optional_parameter_set == tmp:
            raise CLIError('usage error: --type is specified but no other resource id provided')

    return get_network_watcher_from_location()(cmd, namespace)


# pylint: disable=protected-access,too-few-public-methods
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


# pylint: disable=protected-access,too-few-public-methods
class NWConnectionMonitorTestConfigurationHTTPRequestHeaderAction(_AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        HTTPHeader = namespace._cmd.get_models('HTTPHeader')

        if not namespace.http_request_headers:
            namespace.http_request_headers = []

        request_header = HTTPHeader()

        for item in values:
            try:
                key, val = item.split('=', 1)
                if hasattr(request_header, key):
                    setattr(request_header, key, val)
                else:
                    raise CLIError("usage error: '{}' is not a value property of HTTPHeader".format(key))
            except ValueError:
                raise CLIError(
                    'usage error: {} name=HTTPHeader value=HTTPHeaderValue'.format(option_string))

        namespace.http_request_headers.append(request_header)
