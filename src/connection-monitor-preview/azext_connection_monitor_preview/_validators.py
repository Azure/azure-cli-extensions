# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argparse import _AppendAction  # pylint: disable=protected-access

from knack.util import CLIError

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType


def get_network_watcher_from_location(remove=False, watcher_name='watcher_name',
                                      rg_name='watcher_rg'):
    def _validator(cmd, namespace):
        from msrestazure.tools import parse_resource_id

        location = namespace.location
        network_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_NETWORK).network_watchers
        watcher = next((x for x in network_client.list_all() if x.location.lower() == location.lower()), None)
        if not watcher:
            raise CLIError("network watcher is not enabled for region '{}'.".format(location))
        id_parts = parse_resource_id(watcher.id)
        setattr(namespace, rg_name, id_parts['resource_group'])
        setattr(namespace, watcher_name, id_parts['name'])

        if remove:
            del namespace.location

    return _validator


# pylint: disable=protected-access
class NWConnectionMonitorEndpointFilterItemAction(_AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        ConnectionMonitorEndpointFilterItem = namespace._cmd.get_models('ConnectionMonitorEndpointFilterItem')

        if not namespace.filter_items:
            namespace.filter_items = []

        print(option_string)
        kwargs = {}
        for item in values:
            try:
                key, val = item.split('=', 1)
                kwargs[key] = val
            except ValueError:
                raise CLIError(
                    'usage error: {} PropertyName=PropertyValue [PropertyName=PropertyValue ...]'.format(option_string))

        filter_item = ConnectionMonitorEndpointFilterItem(**kwargs)
        namespace.filter_items.append(filter_item)
