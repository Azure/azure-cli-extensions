# pylint: disable=line-too-long
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.core.commands.parameters import (
    resource_group_name_type,
    get_location_type,
    get_resource_name_completion_list,
    tags_type
)

from knack.log import get_logger

from ._constants import (
    MAINTENANCE_RESOURCE_TYPE
)


logger = get_logger(__name__)


def load_arguments(self, _):
    with self.argument_context('maintenance configuration') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location',
                   arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('resource_name', options_list=['--name', '-n'],
                   completer=get_resource_name_completion_list(MAINTENANCE_RESOURCE_TYPE),
                   help='Name of resource.')
        c.argument('maintenanceScope', help='Maintenance Scope e.g. Host, Guest or All')
        c.argument('provider_name', help='Maintenance resource provider - Microsoft.Maintenance')
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('maintenance applyupdate') as c:
        c.argument('apply_update_name', help='Name of apply update resource e.g. default')
        c.argument('provider_name', help='Maintenance resource provider - Microsoft.Maintenance')
        c.argument('resource_parent_name', help="Name of the parent resource e.g. for dedicated hosts this would be the name of the dedicated host group, for VMSS VMs this would be the VMSS name")
        c.argument('resource_parent_type', help="Type of the parent resource e.g. for dedicated hosts this would be hostGroups, for VMSS VMs this would be virtualmachinescalesets")
        c.argument('resource_name', completer=get_resource_name_completion_list(MAINTENANCE_RESOURCE_TYPE), help='Name of resource.')
        c.argument('resource_type', help="Type of the azure resource e.g. virtualmachines, hosts etc.")

    with self.argument_context('maintenance update') as c:
        c.argument('provider_name', help='Maintenance resource provider - Microsoft.Maintenance')
        c.argument('resource_parent_name', help="Name of the parent resource e.g. for dedicated hosts this would be the name of the dedicated host group, for VMSS VMs this would be the VMSS name")
        c.argument('resource_parent_type', help="Type of the parent resource e.g. for dedicated hosts this would be hostGroups, for VMSS VMs this would be virtualmachinescalesets")
        c.argument('resource_name', completer=get_resource_name_completion_list(MAINTENANCE_RESOURCE_TYPE),
                   help='Name of resource.')
        c.argument('resource_type', help="Type of the azure resource e.g. virtualmachines, hosts etc.")

    with self.argument_context('maintenance assignment') as c:
        c.argument('provider_name', help='Maintenance resource provider - Microsoft.Maintenance')
        c.argument('resource_id', help="Fully qualified identifier of the Azure resource.")
        c.argument('resource_parent_name', help="Name of the parent resource e.g. for dedicated hosts this would be the name of the dedicated host group, for VMSS VMs this would be the VMSS name")
        c.argument('resource_parent_type', help="Type of the parent resource e.g. for dedicated hosts this would be hostGroups, for VMSS VMs this would be virtualmachinescalesets")
        c.argument('resource_name', completer=get_resource_name_completion_list(MAINTENANCE_RESOURCE_TYPE),
                   help='Name of resource.')
        c.argument('resource_type', help="Type of the azure resource e.g. virtualmachines, hosts etc.")
        c.argument('provider_name', help='Maintenance resource provider - Microsoft.Maintenance')
        c.argument('maintenance_configuration_id', help='Fully qualified id of the maintenance configuration e.g. /subscriptions/2b4ce620-bb0f-4964-8428-dea4aefec295/resourceGroups/smdtest/providers/Microsoft.Maintenance/maintenanceConfigurations/config1')
        c.argument('configuration_assignment_name', help='Configuration assignment name. Same as the configuration name')
