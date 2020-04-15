# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import get_resource_name_completion_list

# pylint: disable=line-too-long


def load_arguments(self, _):

    # REUSABLE ARGUMENT DEFINITIONS
    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')
    existing_vm_name = CLIArgumentType(overrides=name_arg_type,
                                       configured_default='vm',
                                       help="The name of the Virtual Machine. You can configure the default using `az configure --defaults vm=<name>`",
                                       completer=get_resource_name_completion_list('Microsoft.Compute/virtualMachines'), id_part='name')

    with self.argument_context('vm repair') as c:
        c.argument('vm_name', existing_vm_name)

    with self.argument_context('vm repair create') as c:
        c.argument('repair_username', help='Admin username for repair VM.')
        c.argument('repair_password', help='Admin password for the repair VM.')
        c.argument('repair_vm_name', help='Name of repair VM.')
        c.argument('copy_disk_name', help='Name of OS disk copy.')
        c.argument('repair_group_name', help='Repair resource group name.')
        c.argument('unlock_encrypted_vm', help='Option to auto-unlock encrypted VMs using current subscription auth.')

    with self.argument_context('vm repair restore') as c:
        c.argument('repair_vm_id', help='Repair VM resource id.')
        c.argument('disk_name', help='Name of fixed data disk. Defaults to the first data disk in the repair VM.')
        c.argument('yes', help='Deletes the repair resources without confirmation.')

    with self.argument_context('vm repair run') as c:
        c.argument('repair_vm_id', help='Repair VM resource id.')
        c.argument('run_id', help='Unique run id for run scripts.')
        c.argument('custom_script_file', help='Custom script file to run on VM. Script should be PowerShell for windows, Bash for Linux.')
        c.argument('parameters', nargs='+', help="Space-separated parameters in the format of '[name=]value'. Positional for bash scripts.")
        c.argument('run_on_repair', help="Script will be run on the linked repair VM.")
