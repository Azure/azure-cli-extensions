# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.arguments import CLIArgumentType

from azure.cli.command_modules.vm._actions import _resource_not_exists
from azure.cli.core.commands.parameters import get_resource_name_completion_list

def load_arguments(self, _):

    # REUSABLE ARGUMENT DEFINITIONS
    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')
    existing_vm_name = CLIArgumentType(overrides=name_arg_type,
                                       configured_default='vm',
                                       help="The name of the Virtual Machine. You can configure the default using `az configure --defaults vm=<name>`",
                                       completer=get_resource_name_completion_list('Microsoft.Compute/virtualMachines'), id_part='name')
    existing_disk_name = CLIArgumentType(overrides=name_arg_type, help='The name of the managed disk', completer=get_resource_name_completion_list('Microsoft.Compute/disks'), id_part='name')

    with self.argument_context('vm repair') as c:
        c.argument('vm_name', existing_vm_name)

    with self.argument_context('vm repair swap-disk') as c:
        c.argument('rescue_username', help='Optional Admin username for rescue VM. Prompt will pop up if not given.')
        c.argument('rescue_password', help='Optional Admin password for the rescue VM. Prompt will pop up if not given.')

    with self.argument_context('vm repair restore-swap') as c:
        c.argument('rescue_vm_name', help='Optional. Use this parameter to specify the rescue vm name.')
        c.argument('rescue_resource_group', help='Optional. Use this parameter to specify the rescue vm resource group.')
        c.argument('disk_name', help='Optional. Name of fixed managed disk. Defaults to the first data disk in the rescue vm.')
        c.argument('disk_uri', help= 'Optional. Uri of the fixed unmanaged disk. Defaults to the first data disk in the rescue vm.')
