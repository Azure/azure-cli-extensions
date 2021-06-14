# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
# from azure.cli.core.api import get_subscription_id_list


name_arg_type = CLIArgumentType(
    options_list=('--name', '-n'), help='Name of the VM or VMSS')
vmss_instance_arg_type = CLIArgumentType(
    options_list=('--instance-id'),
    help='ID of VMSS instance. Not needed when connecting to the serial port of a VM')
sysrq_input_arg_type = CLIArgumentType(
    options_list=('--input'), help='SysRq Input Key')


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import resource_group_name_type
    # from azure.cli.core.commands.validators import get_default_location_from_resource_group

    with self.argument_context('serial-console') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('vm_vmss_name', arg_type=name_arg_type)
        c.argument('vmss_instanceid', arg_type=vmss_instance_arg_type)

    with self.argument_context('serial-console send sysrq') as c:
        c.argument('sysrqinput', arg_type=sysrq_input_arg_type)
