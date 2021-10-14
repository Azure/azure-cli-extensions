# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable= too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import tags_type
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from ._actions import VmNicAddAction, VmDiskAddAction


def load_arguments(self, _):
    resource_name = CLIArgumentType(
        options_list='--resource-name', help='Name of the resource.', id_part='name'
    )

    custom_location = CLIArgumentType(
        options_list=['--custom-location', '-c'],
        help='Name or ID of the custom location that will manage this resource.',
    )

    vcenter = CLIArgumentType(
        options_list=['--vcenter', '-v'],
        help='Name or ID of the vCenter that is managing this resource.',
    )

    mo_ref_id = CLIArgumentType(
        options_list=['--mo-ref-id', '-m'],
        help='VCenter MoRef (Managed Object Reference) ID for the existing resource.',
    )

    inventory_item = CLIArgumentType(
        options_list=['--inventory-item', '-i'],
        help='Name or ID of the inventory item.',
    )

    with self.argument_context('connectedvmware') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument(
            'resource_name', resource_name, options_list=['--name', '-n']
        )
        c.argument(
            'custom_location', custom_location, options_list=['--custom-location', '-c']
        )
        c.argument(
            'vcenter', vcenter, options_list=['--vcenter', '-v']
        )
        c.argument(
            'mo_ref_id', mo_ref_id, options_list=['--mo-ref-id', '-m']
        )
        c.argument(
            'inventory_item', inventory_item, options_list=['--inventory-item', '-i']
        )

    with self.argument_context('connectedvmware vcenter connect') as c:
        c.argument(
            'fqdn', options_list=['--fqdn'], help="FQDN/IP address of the vCenter."
        )
        c.argument(
            'port', type=int, options_list=['--port'], help="The port of the vCenter."
        )
        c.argument(
            'username',
            options_list=['--username'],
            help="Username to use for connecting to the vCenter.",
        )
        c.argument(
            'password',
            options_list=['--password'],
            help="Username password credentials to use for connecting to the vCenter.",
        )

    with self.argument_context('connectedvmware vcenter delete') as c:
        c.argument('force', action='store_true', help="Whether force delete or not.")

    self.argument_context('connectedvmware vcenter inventory-item list')

    self.argument_context('connectedvmware vcenter inventory-item show')

    self.argument_context('connectedvmware resource-pool create')

    with self.argument_context('connectedvmware resource-pool delete') as c:
        c.argument('force', action='store_true', help="Whether force delete or not.")

    self.argument_context('connectedvmware cluster create')

    with self.argument_context('connectedvmware cluster delete') as c:
        c.argument('force', action='store_true', help="Whether force delete or not.")

    self.argument_context('connectedvmware datastore create')

    with self.argument_context('connectedvmware datastore delete') as c:
        c.argument('force', action='store_true', help="Whether force delete or not.")

    self.argument_context('connectedvmware host create')

    with self.argument_context('connectedvmware host delete') as c:
        c.argument('force', action='store_true', help="Whether force delete or not.")

    self.argument_context('connectedvmware virtual-network create')

    with self.argument_context('connectedvmware virtual-network delete') as c:
        c.argument('force', action='store_true', help="Whether force delete or not.")

    self.argument_context('connectedvmware vm-template create')

    with self.argument_context('connectedvmware vm-template delete') as c:
        c.argument('force', action='store_true', help="Whether force delete or not.")

    with self.argument_context('connectedvmware vm create') as c:
        c.argument(
            'vm_template',
            options_list=['--vm-template'],
            help="Name or ID of the vm template for deploying the vm.",
        )
        c.argument(
            'resource_pool',
            options_list=['--resource-pool'],
            help="Name or ID of the resource pool for deploying the vm.",
        )
        c.argument(
            'cluster',
            options_list=['--cluster'],
            help="Name or ID of the cluster for deploying the vm.",
        )
        c.argument(
            'host',
            options_list=['--host'],
            help="Name or ID of the host for deploying the vm.",
        )
        c.argument(
            'datastore',
            options_list=['--datastore'],
            help="Name or ID of the datastore for deploying the vm.",
        )
        c.argument(
            'admin_username',
            options_list=['--admin-username'],
            help="Admin username for the vm.",
        )
        c.argument(
            'admin_password',
            options_list=['--admin-password'],
            help="Admin password for the vm.",
        )
        c.argument(
            'num_CPUs',
            type=int,
            options_list=['--num-CPUs'],
            help="Number of desired vCPUs for the vm.",
        )
        c.argument(
            'num_cores_per_socket',
            type=int,
            options_list=['--num-cores-per-socket'],
            help="Number of desired cores per socket for the vm.",
        )
        c.argument(
            'memory_size',
            type=int,
            options_list=['--memory-size'],
            help="Desired memory size in MBs for the vm.",
        )
        c.argument(
            'nics',
            options_list=['--nic'],
            action=VmNicAddAction,
            nargs='+',
            help="Network overrides for the vm. "
            "Usage: --nic name=<> network=<> nic-type=<> power-on-boot=<> "
            "allocation-method=<> ip-address=<> subnet-mask=<> device-key=<> "
            "gateway=<command separated list of gateways>.",
        )
        c.argument(
            'disks',
            options_list=['--disk'],
            action=VmDiskAddAction,
            nargs='+',
            help="Disk overrides for the vm. "
            "Usage: --disk name=<> disk_size=<> disk_mode=<> controller_key=<> "
            "device-key=<> unit_number=<>.",
        )

    with self.argument_context('connectedvmware vm update') as c:
        c.argument(
            'num_CPUs',
            type=int,
            options_list=['--num-CPUs'],
            help="Number of desired vCPUs for the vm.",
        )
        c.argument(
            'num_cores_per_socket',
            type=int,
            options_list=['--num-cores-per-socket'],
            help="Number of desired cores per socket for the vm.",
        )
        c.argument(
            'memory_size',
            type=int,
            options_list=['--memory-size'],
            help="Desired memory size in MBs for the vm.",
        )
        c.argument('tags', arg_type=tags_type)

    with self.argument_context('connectedvmware vm delete') as c:
        c.argument('force', action='store_true', help="Whether force delete or not.")

    with self.argument_context('connectedvmware vm stop') as c:
        c.argument(
            'skip_shutdown',
            action='store_true',
            help="Skips shutdown and power-off immediately.",
        )

    with self.argument_context('connectedvmware vm nic') as c:
        c.argument('nic_name', options_list=['--name', '-n'], help="Name of the NIC.")
        c.argument(
            'vm_name', options_list=['--vm-name'], help="Name of the virtual machine."
        )
        c.argument(
            'network',
            options_list=['--network'],
            help="Name or Id of the virtual network.",
        )
        c.argument(
            'nic_type', options_list=['--nic-type'], help="The nic type for the NIC."
        )
        c.argument(
            'power_on_boot',
            options_list=['--power-on-boot'],
            help="The power on boot option for the nic.",
        )
        c.argument(
            'device_key',
            type=int,
            options_list=['--device-key'],
            help="The device key for the nic.",
        )
        c.argument(
            'nic_names', options_list=['--nics'], nargs='+', help="Names of the NICs."
        )

    with self.argument_context('connectedvmware vm disk add') as c:
        c.argument('disk_name', options_list=['--name', '-n'], help="Name of the Disk.")
        c.argument(
            'vm_name', options_list=['--vm-name'], help="Name of the virtual machine."
        )
        c.argument(
            'disk_size',
            type=int,
            options_list=['--disk-size'],
            help="The disk size in GBs.",
        )
        c.argument(
            'disk_mode', options_list=['--disk-mode'], help="The mode of the disk."
        )
        c.argument(
            'controller_key',
            type=int,
            options_list=['--controller-key'],
            help="The controller key of the disk.",
        )
        c.argument(
            'unit_number',
            type=int,
            options_list=['--unit-number'],
            help="The unit number of the disk.",
        )
        c.argument(
            'device_key',
            type=int,
            options_list=['--device-key'],
            help="The device key for the disk.",
        )
        c.argument(
            'disk_names',
            options_list=['--disks'],
            nargs='+',
            help="Names of the Disks.",
        )

    with self.argument_context('connectedvmware vm disk delete') as c:
        c.argument(
            'vm_name', options_list=['--vm-name'], help="Name of the virtual machine."
        )
        c.argument(
            'disk_names',
            options_list=['--disks'],
            nargs='+',
            help="Names of the Disks.",
        )

    with self.argument_context('connectedvmware vm disk list') as c:
        c.argument(
            'vm_name', options_list=['--vm-name'], help="Name of the virtual machine."
        )

    with self.argument_context('connectedvmware vm disk show') as c:
        c.argument('disk_name', options_list=['--name', '-n'], help="Name of the Disk.")
        c.argument(
            'vm_name', options_list=['--vm-name'], help="Name of the virtual machine."
        )

    with self.argument_context('connectedvmware vm disk update') as c:
        c.argument('disk_name', options_list=['--name', '-n'], help="Name of the Disk.")
        c.argument(
            'vm_name', options_list=['--vm-name'], help="Name of the virtual machine."
        )
        c.argument(
            'disk_size',
            type=int,
            options_list=['--disk-size'],
            help="The disk size in GBs.",
        )
        c.argument(
            'disk_mode', options_list=['--disk-mode'], help="The mode of the disk."
        )
        c.argument(
            'controller_key',
            type=int,
            options_list=['--controller-key'],
            help="The controller key of the disk.",
        )
        c.argument(
            'unit_number',
            type=int,
            options_list=['--unit-number'],
            help="The unit number of the disk.",
        )
        c.argument(
            'device_key',
            type=int,
            options_list=['--device-key'],
            help="The device key for the disk.",
        )

    with self.argument_context('connectedvmware vm guest-agent enable') as c:
        c.argument(
            'vm_name', options_list=['--vm-name'], help="Name of the vm."
        )
        c.argument(
            'username',
            options_list=['--username'],
            help="Username to use for connecting to the vm.",
        )
        c.argument(
            'password',
            options_list=['--password'],
            help="Username password credentials to use for connecting to the vm.",
        )

    with self.argument_context('connectedvmware vm guest-agent show') as c:
        c.argument(
            'vm_name', options_list=['--vm-name'], help="Name of the vm.",
        )
