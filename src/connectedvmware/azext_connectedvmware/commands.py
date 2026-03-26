# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, disable=too-many-statements

from azure.cli.core import AzCommandsLoader
from ._client_factory import (
    cf_vcenter,
    cf_resource_pool,
    cf_virtual_network,
    cf_virtual_machine_template,
    cf_virtual_machine_instance,
    cf_inventory_item,
    cf_vminstance_guest_agent,
    cf_cluster,
    cf_datastore,
    cf_host,
    cf_machine_extension,
)


def load_command_table(self: AzCommandsLoader, _):

    with self.command_group('connectedvmware vcenter', client_factory=cf_vcenter) as g:
        g.custom_command('connect', 'connect_vcenter', supports_no_wait=True)
        g.custom_command('delete', 'delete_vcenter', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'show_vcenter')
        g.custom_command('list', 'list_vcenter')

    with self.command_group(
        'connectedvmware vcenter inventory-item', client_factory=cf_inventory_item
    ) as g:
        g.custom_show_command('show', 'show_inventory_item')
        g.custom_command('list', 'list_inventory_item')

    with self.command_group(
        'connectedvmware resource-pool', client_factory=cf_resource_pool
    ) as g:
        g.custom_command('create', 'create_resource_pool', supports_no_wait=True)
        g.custom_command('delete', 'delete_resource_pool', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'show_resource_pool')
        g.custom_command('list', 'list_resource_pool')

    with self.command_group(
        'connectedvmware cluster', client_factory=cf_cluster
    ) as g:
        g.custom_command('create', 'create_cluster', supports_no_wait=True)
        g.custom_command('delete', 'delete_cluster', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'show_cluster')
        g.custom_command('list', 'list_cluster')

    with self.command_group(
        'connectedvmware datastore', client_factory=cf_datastore
    ) as g:
        g.custom_command('create', 'create_datastore', supports_no_wait=True)
        g.custom_command('delete', 'delete_datastore', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'show_datastore')
        g.custom_command('list', 'list_datastore')

    with self.command_group(
        'connectedvmware host', client_factory=cf_host
    ) as g:
        g.custom_command('create', 'create_host', supports_no_wait=True)
        g.custom_command('delete', 'delete_host', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'show_host')
        g.custom_command('list', 'list_host')

    with self.command_group(
        'connectedvmware virtual-network', client_factory=cf_virtual_network
    ) as g:
        g.custom_command('create', 'create_virtual_network', supports_no_wait=True)
        g.custom_command('delete', 'delete_virtual_network', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'show_virtual_network')
        g.custom_command('list', 'list_virtual_network')

    with self.command_group(
        'connectedvmware vm-template', client_factory=cf_virtual_machine_template
    ) as g:
        g.custom_command('create', 'create_vm_template', supports_no_wait=True)
        g.custom_command('delete', 'delete_vm_template', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'show_vm_template')
        g.custom_command('list', 'list_vm_template')

    with self.command_group(
        'connectedvmware vm', client_factory=cf_virtual_machine_instance
    ) as g:
        g.custom_command('create', 'create_vm', supports_no_wait=True)
        g.custom_command('create-from-machines', 'create_from_machines')
        g.custom_command('delete', 'delete_vm', supports_no_wait=True, confirmation=True)
        g.custom_command('update', 'update_vm', supports_no_wait=True)
        g.custom_show_command('show', 'show_vm')
        # g.custom_command('list', 'list_vm')
        g.custom_command('list', 'list_vm',
                         deprecate_info=g.deprecate(redirect='az connectedvmware vm show', hide=True))
        g.custom_command('start', 'start_vm', supports_no_wait=True)
        g.custom_command('stop', 'stop_vm', supports_no_wait=True)
        g.custom_command('restart', 'restart_vm', supports_no_wait=True)

    with self.command_group(
        'connectedvmware vm nic', client_factory=cf_virtual_machine_instance
    ) as g:
        g.custom_command('add', 'add_nic', supports_no_wait=True)
        g.custom_command('update', 'update_nic', supports_no_wait=True)
        g.custom_command('delete', 'delete_nics', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'show_nic')
        g.custom_command('list', 'list_nics')

    with self.command_group(
        'connectedvmware vm disk', client_factory=cf_virtual_machine_instance
    ) as g:
        g.custom_command('add', 'add_disk', supports_no_wait=True)
        g.custom_command('update', 'update_disk', supports_no_wait=True)
        g.custom_command('delete', 'delete_disks', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'show_disk')
        g.custom_command('list', 'list_disks')

    with self.command_group(
        'connectedvmware vm guest-agent', client_factory=cf_vminstance_guest_agent
    ) as g:
        g.custom_command('enable', 'enable_guest_agent', supports_no_wait=True)
        g.custom_show_command('show', 'show_guest_agent')

    with self.command_group(
        'connectedvmware vm extension', client_factory=cf_machine_extension
    ) as g:
        g.custom_command('list', 'connectedvmware_extension_list')
        g.custom_show_command('show', 'connectedvmware_extension_show')
        g.custom_command('create', 'connectedvmware_extension_create', supports_no_wait=True)
        g.custom_command('update', 'connectedvmware_extension_update', supports_no_wait=True)
        g.custom_command('delete', 'connectedvmware_extension_delete', supports_no_wait=True, confirmation=True)

    with self.command_group('connectedvmware', is_preview=False):
        pass
