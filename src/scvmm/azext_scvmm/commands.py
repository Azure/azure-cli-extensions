# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-statements

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import CliCommandType

from ._client_factory import (
    cf_vmmserver,
    cf_cloud,
    cf_virtual_network,
    cf_virtual_machine_template,
    cf_virtual_machine,
    cf_availability_sets,
    cf_inventory_items,
)

from ._validators import (
    validate_param_combos,
    validate_param_combos_for_vm,
    validate_param_combos_for_avset,
)

vmmservers_cmd_type = CliCommandType(
    operations_tmpl='azext_scvmm.vendored_sdks.operations.'
    '_vmm_servers_operations#VmmServersOperations.{}',
    client_factory=cf_vmmserver,
)

clouds_cmd_type = CliCommandType(
    operations_tmpl='azext_scvmm.vendored_sdks.operations.'
    '_clouds_operations#CloudsOperations.{}',
    client_factory=cf_cloud,
)

virtual_networks_cmd_type = CliCommandType(
    operations_tmpl='azext_scvmm.vendored_sdks.operations.'
    '_virtual_networks_operations#VirtualNetworksOperations.{}',
    client_factory=cf_virtual_network,
)

virtual_machine_templates_cmd_type = CliCommandType(
    operations_tmpl='azext_scvmm.vendored_sdks.operations.'
    '_virtual_machine_templates_operations#VirtualMachineTemplatesOperations.{}',
    client_factory=cf_virtual_machine_template,
)

virtual_machines_cmd_type = CliCommandType(
    operations_tmpl='azext_scvmm.vendored_sdks.operations.'
    '_virtual_machines_operations#VirtualMachinesOperations.{}',
    client_factory=cf_virtual_machine,
)


availability_sets_cmd_type = CliCommandType(
    operations_tmpl='azext_scvmm.vendored_sdks.operations.'
    '_availability_sets_operations#AvailabilitySetsOperations.{}',
    client_factory=cf_availability_sets,
)


def load_command_table(self: AzCommandsLoader, _):

    with self.command_group(
        'scvmm vmmserver', vmmservers_cmd_type, client_factory=cf_vmmserver
    ) as g:
        g.custom_command('connect', 'connect_vmmserver', supports_no_wait=True)
        g.custom_command('update', 'update_vmmserver', supports_no_wait=True)
        g.custom_command('delete', 'delete_vmmserver', supports_no_wait=True)
        g.custom_show_command('show', 'show_vmmserver')
        g.custom_command('list', 'list_vmmserver')
        g.wait_command('wait')

    with self.command_group(
        'scvmm cloud', clouds_cmd_type, client_factory=cf_cloud
    ) as g:
        g.custom_command(
            'create',
            'create_cloud',
            supports_no_wait=True,
            validator=validate_param_combos,
        )
        g.custom_command('update', 'update_cloud', supports_no_wait=True)
        g.custom_command(
            'delete', 'delete_cloud', supports_no_wait=True, confirmation=True
        )
        g.custom_show_command('show', 'show_cloud')
        g.custom_command('list', 'list_cloud')
        g.wait_command('wait')

    with self.command_group(
        'scvmm virtual-network',
        virtual_networks_cmd_type,
        client_factory=cf_virtual_network,
    ) as g:
        g.custom_command(
            'create',
            'create_virtual_network',
            supports_no_wait=True,
            validator=validate_param_combos,
        )
        g.custom_command('update', 'update_virtual_network', supports_no_wait=True)
        g.custom_command(
            'delete', 'delete_virtual_network', supports_no_wait=True, confirmation=True
        )
        g.custom_show_command('show', 'show_virtual_network')
        g.custom_command('list', 'list_virtual_network')
        g.wait_command('wait')

    with self.command_group(
        'scvmm vm-template',
        virtual_machine_templates_cmd_type,
        client_factory=cf_virtual_machine_template,
    ) as g:
        g.custom_command(
            'create',
            'create_vm_template',
            supports_no_wait=True,
            validator=validate_param_combos,
        )
        g.custom_command('update', 'update_vm_template', supports_no_wait=True)
        g.custom_command(
            'delete', 'delete_vm_template', supports_no_wait=True, confirmation=True
        )
        g.custom_show_command('show', 'show_vm_template')
        g.custom_command('list', 'list_vm_template')
        g.wait_command('wait')

    with self.command_group(
        'scvmm vm', virtual_machines_cmd_type, client_factory=cf_virtual_machine
    ) as g:
        g.custom_command(
            'create',
            'create_vm',
            supports_no_wait=True,
            validator=validate_param_combos_for_vm,
        )
        g.custom_command(
            'delete', 'delete_vm', supports_no_wait=True, confirmation=True
        )
        g.custom_command('update', 'update_vm', supports_no_wait=True)
        g.custom_show_command('show', 'show_vm')
        g.custom_command('list', 'list_vm')
        g.custom_command('start', 'start_vm', supports_no_wait=True)
        g.custom_command('stop', 'stop_vm', supports_no_wait=True)
        g.custom_command('restart', 'restart_vm', supports_no_wait=True)
        g.custom_command('create-checkpoint', 'create_vm_checkpoint', supports_no_wait=True)
        g.custom_command('delete-checkpoint', 'delete_vm_checkpoint', supports_no_wait=True)
        g.custom_command('restore-checkpoint', 'restore_vm_checkpoint', supports_no_wait=True)
        g.wait_command('wait')

    with self.command_group(
        'scvmm vm nic', virtual_machines_cmd_type, client_factory=cf_virtual_machine
    ) as g:
        g.custom_command('add', 'add_nic', supports_no_wait=True)
        g.custom_command('update', 'update_nic', supports_no_wait=True)
        g.custom_command(
            'delete', 'delete_nics', supports_no_wait=True, confirmation=True
        )
        g.custom_show_command('show', 'show_nic')
        g.custom_command('list', 'list_nics')
        g.wait_command('wait')

    with self.command_group(
        'scvmm vm disk', virtual_machines_cmd_type, client_factory=cf_virtual_machine
    ) as g:
        g.custom_command('add', 'add_disk', supports_no_wait=True)
        g.custom_command('update', 'update_disk', supports_no_wait=True)
        g.custom_command(
            'delete', 'delete_disks', supports_no_wait=True, confirmation=True
        )
        g.custom_show_command('show', 'show_disk')
        g.custom_command('list', 'list_disks')
        g.wait_command('wait')

    with self.command_group(
        'scvmm avset', availability_sets_cmd_type, client_factory=cf_availability_sets
    ) as g:
        g.custom_command(
            'create',
            'create_avset',
            supports_no_wait=True,
            validator=validate_param_combos_for_avset,
        )
        g.custom_command('update', 'update_avset', supports_no_wait=True)
        g.custom_command(
            'delete', 'delete_avset', supports_no_wait=True, confirmation=True
        )
        g.custom_show_command('show', 'show_avset')
        g.custom_command('list', 'list_avsets')
        g.wait_command('wait')

    with self.command_group(
        'scvmm vmmserver inventory-item', client_factory=cf_inventory_items
    ) as g:
        g.custom_show_command('show', 'show_inventory_item')
        g.custom_command('list', 'list_inventory_items')

    with self.command_group('scvmm', is_preview=True):
        pass
