# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (resource_group_name_type, get_location_type,
                                                get_resource_name_completion_list,
                                                get_three_state_flag, get_enum_type, tags_type)
from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):

    name_type = CLIArgumentType(options_list=['--name', '-n'])

    with self.argument_context('containerapp') as c:
        # Base arguments
        c.argument('name', name_type, metavar='NAME', id_part='name')
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))

    with self.argument_context('containerapp env') as c:
        c.argument('name', name_type)
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Location of resource. Examples: Canada Central, North Europe')
        c.argument('logs_destination', options_list=['--logs-dest'])
        c.argument('logs_customer_id', options_list=['--logs-workspace-id'], help='Log analytics workspace ID')
        c.argument('logs_key', options_list=['--logs-workspace-key'], help='Log analytics workspace key')
        # c.argument('instrumentation_key', options_list=['--instrumentation-key'])
        # c.argument('controlplane_subnet_resource_id', options_list=['--controlplane-subnet-resource-id'], help='Resource ID of a subnet for control plane infrastructure components. This subnet must be in the same VNET as the subnet defined in appSubnetResourceId.')
        # c.argument('app_subnet_resource_id', options_list=['--app-subnet-resource-id'], help='Resource ID of a subnet that Container App containers are injected into. This subnet must be in the same VNET as the subnet defined in controlPlaneSubnetResourceId.')
        # c.argument('docker_bridge_cidr', options_list=['--docker-bridge-cidr'], help='CIDR notation IP range assigned to the Docker bridge. It must not overlap with any Subnet IP ranges or the IP range defined in Platform Reserved CIDR, if defined')
        # c.argument('platform_reserved_cidr', options_list=['--platform-reserved-cidr'], help='IP range in CIDR notation that can be reserved for environment infrastructure IP addresses. It must not overlap with any other Subnet IP ranges')
        # c.argument('platform_reserved_dns_ip', options_list=['--platform-reserved-dns-ip'], help='An IP address from the IP range defined by Platform Reserved CIDR that will be reserved for the internal DNS server.')
        # c.argument('internal_only', options_list=['--internal-only'], help='Boolean indicating the environment only has an internal load balancer. These environments do not have a public static IP resource, must provide ControlPlaneSubnetResourceId and AppSubnetResourceId if enabling this property')
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('containerapp env update') as c:
        c.argument('name', name_type, help='Name of the kubernetes environment.')
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('containerapp env delete') as c:
        c.argument('name', name_type, help='Name of the Kubernetes Environment.')

    with self.argument_context('containerapp env show') as c:
        c.argument('name', name_type, help='Name of the Kubernetes Environment.')
