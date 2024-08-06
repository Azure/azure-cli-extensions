# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core import AzCommandsLoader
from .vendored_sdks.scvmm.models import AllocationMethod
from .scvmm_constants import BusType, VHDType
from ._actions import VmNicAddAction, VmDiskAddAction


def load_arguments(self: AzCommandsLoader, _):
    from azure.cli.core.commands.parameters import (
        tags_type,
        get_enum_type,
        get_three_state_flag,
    )
    from azure.cli.core.commands.validators import (
        get_default_location_from_resource_group,
        validate_file_or_dict,
    )

    scvmm_name_type = CLIArgumentType(
        options_list=['--name', '-n'],
        help='Name of the resource.',
        id_part='name',
    )

    custom_location_type = CLIArgumentType(
        options_list=['--custom-location'],
        help='Name or ID of the custom location that will manage this resource.',
    )

    vmmserver_type = CLIArgumentType(
        options_list=['--vmmserver', '-v'],
        help='Name or ID of the vmmserver that is managing this resource.',
    )

    uuid_type = CLIArgumentType(
        options_list=['--uuid'],
        help="The ID of the resource created in the VMM.",
    )

    inventory_item_type = CLIArgumentType(
        options_list=['--inventory-item', '-i'],
        help='Name or ID of the inventory item.',
    )

    force_delete_type = CLIArgumentType(
        options_list=['--force'],
        help='Force the resource to be deleted from azure.',
        action='store_true',
    )

    virtualmachine_name_type = CLIArgumentType(
        options_list=['--virtual-machine-name'],
        help='Name of the VirtualMachine.',
    )

    with self.argument_context('scvmm') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('resource_name', arg_type=scvmm_name_type)
        c.argument('custom_location', arg_type=custom_location_type)
        c.argument('vmmserver', arg_type=vmmserver_type)
        c.argument('uuid', arg_type=uuid_type)
        c.argument('inventory_item', arg_type=inventory_item_type)
        c.argument('force', arg_type=force_delete_type)

    with self.argument_context('scvmm vmmserver connect') as c:
        c.argument(
            'fqdn', options_list=['--fqdn'], help="FQDN/IP address of the vmmserver."
        )
        c.argument(
            'port', type=int, options_list=['--port'], help="The port of the vmmserver."
        )
        c.argument(
            'username',
            options_list=['--username'],
            help="Username to use for connecting to the vmmserver.",
        )
        c.argument(
            'password',
            options_list=['--password'],
            help="Username password credentials to use for connecting to the vmmserver.",
        )

    with self.argument_context('scvmm vm-template wait') as c:
        c.argument(
            'virtual_machine_template_name',
            options_list=['--vm-template-name'],
            help="Name of the VirtualMachineTemplate.",
        )

    with self.argument_context('scvmm vm wait') as c:
        c.argument('virtual_machine_name', arg_type=virtualmachine_name_type)

    for scope in ['create', 'update']:
        with self.argument_context(f'scvmm vm {scope}') as c:
            c.argument(
                'cpu_count',
                type=int,
                options_list=['--cpu-count'],
                help="Number of desired vCPUs for the vm.",
            )
            c.argument(
                'memory_size',
                type=int,
                options_list=['--memory-size'],
                help="Desired memory size in MBs for the vm.",
            )
            c.argument(
                'dynamic_memory_enabled',
                arg_type=get_three_state_flag(
                    positive_label='true', negative_label='false', return_label=True
                ),
                help='If dynamic memory should be enabled.',
            )
            c.argument(
                'dynamic_memory_min',
                type=int,
                options_list=['--dynamic-memory-min'],
                help="DynamicMemoryMin in MBs for the vm.",
            )
            c.argument(
                'dynamic_memory_max',
                type=int,
                options_list=['--dynamic-memory-max'],
                help="DynamicMemoryMax in MBs for the vm.",
            )
            c.argument(
                'availability_sets',
                options_list=['--availability-sets', '-a'],
                nargs='+',
                help="List of the name or the ID of the availability sets for the vm.",
            )

    with self.argument_context('scvmm vm create') as c:
        c.argument(
            'vm_template',
            options_list=['--vm-template', '-t'],
            help="Name or ID of the vm template for deploying the vm.",
        )
        c.argument(
            'cloud',
            options_list=['--cloud', '-c'],
            help="Name or ID of the cloud for deploying the vm.",
        )
        c.argument(
            'admin_password',
            options_list=['--admin-password'],
            help="Admin password for the vm.",
        )
        c.argument(
            'nics',
            options_list=['--nic'],
            action=VmNicAddAction,
            nargs='+',
            help="Network overrides for the vm."
            "Usage: --nic name=<> network=<> ipv4-address-type=<> "
            "ipv6-address-type=<> mac-address-type=<> mac-address=<>.",
        )
        c.argument(
            'disks',
            options_list=['--disk'],
            action=VmDiskAddAction,
            nargs='+',
            help="Disk overrides for the vm."
            "Usage: --disk name=<> disk-size=<> template-disk-id=<> bus-type=<> "
            "bus=<> lun=<> vhd-type=<> qos-name=<> qos-id=<>.",
        )

    with self.argument_context('scvmm vm stop') as c:
        c.argument(
            'skip_shutdown',
            arg_type=get_three_state_flag(
                positive_label='true', negative_label='false', return_label=True
            ),
            help="Skip shutdown and power-off immediately.",
        )

    with self.argument_context('scvmm vm create-checkpoint') as c:
        c.argument(
            'checkpoint_name',
            help="Name of the checkpoint to be created.",
        )

        c.argument(
            'checkpoint_description',
            help="Description of the checkpoint to be created.",
        )

    with self.argument_context('scvmm vm delete-checkpoint') as c:
        c.argument(
            'checkpoint_id',
            help="Checkpoint UUID.",
        )

    with self.argument_context('scvmm vm restore-checkpoint') as c:
        c.argument(
            'checkpoint_id',
            help="Checkpoint UUID.",
        )

    with self.argument_context('scvmm vm nic') as c:
        c.argument('nic_name', options_list=['--name', '-n'], help="Name of the NIC.")
        c.argument('nic_id', options_list=['--nic-id'], help="UUID of the NIC.")
        c.argument(
            'vm_name', options_list=['--vm-name'], help="Name of the virtual machine."
        )
        c.argument(
            'network',
            options_list=['--network'],
            help="Name or Id of the virtual network.",
        )
        c.argument(
            'disconnect',
            arg_type=get_three_state_flag(),
            help="Disconnect the NIC from any virtual network it is connected to.",
        )
        c.argument(
            'ipv4_address_type',
            arg_type=get_enum_type(AllocationMethod),
            help="The allocation type of the ipv4 address.",
        )
        c.argument(
            'ipv6_address_type',
            arg_type=get_enum_type(AllocationMethod),
            help="The allocation type of the ipv6 address.",
        )
        c.argument(
            'mac_address_type',
            arg_type=get_enum_type(AllocationMethod),
            help="The allocation type of the MAC address.",
        )
        c.argument(
            'mac_address',
            options_list=['--mac-address'],
            help="MAC address of the NIC.",
        )
        c.argument(
            'nic_names', options_list=['--nics'], nargs='+', help="Names of the NICs."
        )
        c.argument('virtual_machine_name', arg_type=virtualmachine_name_type)

    with self.argument_context('scvmm vm disk') as c:
        c.argument('disk_name', options_list=['--name', '-n'], help="Name of the Disk.")
        c.argument('disk_id', options_list=['--disk-id'], help="UUID of the Disk.")
        c.argument(
            'vm_name', options_list=['--vm-name'], help="Name of the virtual machine."
        )
        c.argument(
            'disk_size_gb', options_list=['--disk-size'], help="Size of the disk in GB."
        )
        c.argument('bus', options_list=['--bus'], help="Bus Number for the disk.")
        c.argument('lun', options_list=['--lun'], help="Lun Number for the disk.")
        c.argument(
            'bus_type', arg_type=get_enum_type(BusType), help="Bus Type of the Disk."
        )
        c.argument(
            'vhd_type', arg_type=get_enum_type(VHDType), help="VHD Type of the Disk."
        )
        c.argument(
            'template_disk_id',
            options_list=['--template-disk-id'],
            help="UUID of the corresponding disk in VM Template.",
        )
        c.argument(
            'qos_name',
            options_list=['--qos-name'],
            help="Name of the Storage QoS Policy to be applied on the disk.",
        )
        c.argument(
            'qos_id',
            options_list=['--qos-id'],
            help="UUID of the Storage QoS Policy to be applied on the disk.",
        )
        c.argument(
            'disk_names',
            options_list=['--disks'],
            nargs='+',
            help="Names of the Disks.",
        )
        c.argument('virtual_machine_name', arg_type=virtualmachine_name_type)

    with self.argument_context('scvmm vm delete') as c:
        c.argument(
            'force',
            action='store_true',
            help="Force delete the azure resource.",
        )
        c.argument(
            'retain',
            action='store_true',
            help='Disable the VM from azure but retain the VM in VMM.',
            deprecate_info=c.deprecate(hide=True),
        )
        c.argument(
            'deleteFromHost',
            action='store_true',
            help='Delete the VM from the SCVMM.',
            deprecate_info=c.deprecate(hide=True, redirect='--delete-from-host'),
        )
        c.argument(
            'delete_from_host',
            action='store_true',
            help='Delete the VM from the VMware host.',
        )
        c.argument(
            'delete_machine',
            action='store_true',
            help='Delete the parent Microsoft.HybridCompute Machine resource',
        )

    with self.argument_context('scvmm avset') as c:
        c.argument(
            'avset_name',
            options_list=['--avset-name', '-a'],
            help="Name of the Availabilty Set.",
        )
        c.argument(
            'availability_set_name',
            help="Name of the AvailabilitySet."
        )

    with self.argument_context('scvmm cloud') as c:
        c.argument(
            'cloud_name',
            help="Name of the Cloud."
        )

    with self.argument_context('scvmm vm guest-agent enable') as c:
        c.argument(
            'vm_name', help="Name of the VM."
        )
        c.argument(
            'username',
            options_list=['--username'],
            help="Username to use for connecting to the vm.",
        )
        c.argument(
            'password', options_list=['--password'],
            help="Username password credentials to use for connecting to the VM.",
        )
        c.argument(
            'https_proxy', help="HTTPS proxy server url for the VM.",
        )

    with self.argument_context('scvmm vm guest-agent show') as c:
        c.argument(
            'password', options_list=['--password'],
            help="Username password credentials to use for connecting to the VM.",
        )

    with self.argument_context('scvmm vm guest-agent show') as c:
        c.argument(
            'vm_name', help="Name of the VM.",
        )

    with self.argument_context('scvmm vm extension list') as c:
        c.argument('vm_name', help='The name of the vm containing the extension.')
        c.argument(
            'expand', help='The expand expression to apply on the operation.')

    with self.argument_context('scvmm vm extension show') as c:
        c.argument(
            'vm_name', help='The name of the vm containing the extension.',
            id_part='name')
        c.argument('name', help='The name of the vm extension.', id_part='child_name_1')

    for scope in ['scvmm vm extension update', 'scvmm vm extension create']:
        with self.argument_context(scope) as c:
            c.argument(
                'vm_name', help='The name of the vm where the extension '
                'should be created or updated.')
            c.argument('name', help='The name of the vm extension.')
            c.argument('tags', tags_type)
            c.argument(
                'force_update_tag', help='How the extension handler should be forced to update even if '
                'the extension configuration has not changed.')
            c.argument('publisher', help='The name of the extension handler publisher.')
            c.argument(
                'type_', options_list=['--type'], help='Specify the type of the extension; an example '
                'is "CustomScriptExtension".')
            c.argument('type_handler_version', help='Specifies the version of the script handler.')
            c.argument(
                'enable_auto_upgrade', arg_type=get_three_state_flag(), help='Indicates whether the extension '
                'should be automatically upgraded by the platform if there is a newer version available.')
            c.argument(
                'auto_upgrade_minor', arg_type=get_three_state_flag(), help='Indicate whether the extension should '
                'use a newer minor version if one is available at deployment time. Once deployed, however, the '
                'extension will not upgrade minor versions unless redeployed, even with this property set to true.')
            c.argument(
                'settings', type=validate_file_or_dict, help='Json formatted public settings for the extension. '
                'Expected value: json-string/json-file/@json-file.')
            c.argument(
                'protected_settings', type=validate_file_or_dict, help='The extension can contain either '
                'protectedSettings or protectedSettingsFromKeyVault or no protected settings at all. Expected '
                'value: json-string/json-file/@json-file.')

    with self.argument_context('scvmm vm extension delete') as c:
        c.argument('vm_name', help='The name of the vm where the extension '
                   'should be deleted.', id_part='name')
        c.argument('name', help='The name of the vm extension.', id_part='child_name_1')
