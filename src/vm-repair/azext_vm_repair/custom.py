# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.vm.custom import create_vm

def helloworld():
    print('Hello World.')

def swap_disk(cmd, vm_name, resource_group_name, rescue_vm_name=None):

    # Set default rescue vm name
    if rescue_vm_name is None:
        rescue_vm_name = vm_name + '_RescueVM'

    print('swap disk')
    print(rescue_vm_name)
    #create_vm(cmd, vm_name, "test")

def restore_swap():
    print('restore swap')
