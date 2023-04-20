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
    get_location_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group

from azext_fleet._validators import validate_member_cluster_id, validate_upgrade_type, validate_kubernetes_version


def load_arguments(self, _):

    with self.argument_context('fleet') as c:
        c.argument('name', options_list=['--name', '-n'], help='Specify the fleet name.')
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)

    with self.argument_context('fleet create') as c:
        c.argument('tags', tags_type)
        c.argument('dns_name_prefix', options_list=['--dns-name-prefix', '-p'])

    with self.argument_context('fleet update') as c:
        c.argument('tags', tags_type)

    with self.argument_context('fleet get-credentials') as c:
        c.argument('context_name', options_list=['--context'], help='If specified, overwrite the default context name.')
        c.argument('path', options_list=['--file', '-f'], type=file_type, completer=FilesCompleter(), default=os.path.join(os.path.expanduser('~'), '.kube', 'config'))

    with self.argument_context('fleet member') as c:
        c.argument('name', options_list=['--name', '-n'], help='Specify the fleet member name.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Specify the fleet name.')

    with self.argument_context('fleet member create') as c:
        c.argument('member_cluster_id', validator=validate_member_cluster_id)
        c.argument('update_group')

    with self.argument_context('fleet member update') as c:
        c.argument('update_group')

    with self.argument_context('fleet updaterun') as c:
        c.argument('name', options_list=['--name', '-n'], help='Specify name for the update run.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Specify the fleet name.')

    with self.argument_context('fleet updaterun create') as c:
        c.argument('upgrade_type', validator=validate_upgrade_type)
        c.argument('kubernetes_version', validator=validate_kubernetes_version)
        c.argument('stages', type=file_type, completer=FilesCompleter())
        c.argument('update_group')

    with self.argument_context('fleet member update') as c:
        c.argument('update_group')

    with self.argument_context('fleet member update') as c:
        c.argument('update_group')

    with self.argument_context('fleet updaterun') as c:
        c.argument('name', options_list=['--name', '-n'], help='Specify name for the update run.')
        c.argument('fleet_name', options_list=['--fleet-name', '-f'], help='Specify the fleet name.')

    with self.argument_context('fleet updaterun create') as c:
        c.argument('upgrade_type', validator=validate_upgrade_type)
        c.argument('kubernetes_version', validator=validate_kubernetes_version)
        c.argument('stages', type=file_type, completer=FilesCompleter())
