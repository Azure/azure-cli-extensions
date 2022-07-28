# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list,
    tags_type
)
from azext_fleet._validators import validate_member_cluster_id


def load_arguments(self, _):

    with self.argument_context('fleet') as c:
        c.argument('name', options_list=['--name', '-n'], help='Specify the fleet name.', completer=get_resource_name_completion_list('Microsoft.ContainerService/ManagedClusters'))

    with self.argument_context('fleet create') as c:
        c.argument('tags', tags_type)
        c.argument('dns_name_prefix', options_list=['--dns-name-prefix', '-p'])

    with self.argument_context('fleet member') as c:
        c.argument('member_name', help='Specify a member name. Default value is name of the managed cluster.')

    with self.argument_context('fleet member join') as c:
        c.argument('member_cluster_id', validator=validate_member_cluster_id)
