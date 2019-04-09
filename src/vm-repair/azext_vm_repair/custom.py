# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger

from azure.cli.command_modules.vm.custom import get_vm, _is_linux_os

import subprocess

logger = get_logger(__name__)

def helloworld():
    print('Hello World.')

def swap_disk(cmd, vm_name, resource_group_name, rescue_password=None, rescue_username=None, rescue_vm_name=None):

    # fetch VM and Get OS Disk
    target_vm = get_vm(cmd, resource_group_name, vm_name)
    is_linux = _is_linux_os(target_vm)

    if is_linux:
        os_image_name = "UbuntuLTS"
    else:
        os_image_name = "Win2016Datacenter"

    # Ask for username and password data if None
    # Do it here or through validator?

    # Set default rescue vm name TODO: move to validator
    if rescue_vm_name is None:
        rescue_vm_name = vm_name[:8] + '-Rescue'
    copied_os_disk_name = vm_name + "_Copied_Disk"

    
    target_disk_name = target_vm.storage_profile.os_disk.name
    
    # Figure out managed vs unmanged
    # _uses_managed_disk(target_vm)
    
    # Copy OS disk command
    copy_disk_command = 'az disk create -g {g} -n {n} --source {s}' \
                        .format(g=resource_group_name, n=copied_os_disk_name, s=target_disk_name)
    # Create new rescue VM with copied disk command
    create_rescue_vm_command = 'az vm create -g {g} -n {n} --image {image} --attach-data-disks {disk_name} --admin-password {password}' \
                               .format(g=resource_group_name, n=rescue_vm_name, image=os_image_name, disk_name=copied_os_disk_name, password=rescue_password)    
    if not is_linux:
        create_rescue_vm_command += ' --admin-username {username}'.format(username=rescue_username)
    # Validate create vm create command to validate parameters before runnning copy disk command
    validate_create_vm_command = create_rescue_vm_command + ' --validate'

    # Run all az commands
    return_code = _az_serial_caller([validate_create_vm_command, copy_disk_command, create_rescue_vm_command])

    if return_code == 0:
        logger.warning("Rescue VM succesfully created with name: {n}".format(n=rescue_vm_name))
    else:
        # Clean up resources here (copied disk and created rescue vm)
        logger.error("Some error happened")
  
    return None

def restore_swap():
    print('restore swap')

# check if this is reliable
def _uses_managed_disk(vm):
    if vm.storage_profile.os_disk.managed_disk is None:
        return False
    else:
        return True

# returns the return code of the subprocess.Popen
def _call_az_command(command_string):

    logger.warning(command_string)

    p1 = subprocess.Popen(command_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Wait for process to terminate and fetch stdout and stderror
    stdout, stderr = p1.communicate()

    if p1.returncode != 0:
        logger.warning(stderr)
    else:
        # logger.warning(stdout)
        logger.warning('\'' + command_string + '\' command succeeded.')

    return p1.returncode

def _az_serial_caller(command_list):

    for command_string in command_list:
        return_code = _call_az_command(command_string)
        if return_code != 0:
            return return_code;        
    
    return 0;