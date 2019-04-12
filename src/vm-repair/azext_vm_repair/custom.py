# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger

from azure.cli.command_modules.vm.custom import get_vm, _is_linux_os, get_vm_details

import subprocess
from uuid import uuid4

logger = get_logger(__name__)

def helloworld():
    print('Hello World.')

def swap_disk(cmd, vm_name, resource_group_name, rescue_password=None, rescue_username=None, rescue_vm_name=None):

    # Fetch VM info
    target_vm = get_vm(cmd, resource_group_name, vm_name)
    is_linux = _is_linux_os(target_vm)
    target_disk_name = target_vm.storage_profile.os_disk.name
    is_managed = _uses_managed_disk(target_vm)

    if is_linux:
        os_image_name = "UbuntuLTS"
    else:
        os_image_name = "Win2016Datacenter"

    # TODO, validate restrictions on disk naming
    copied_os_disk_name = vm_name + "-DiskCopy_" + str(uuid4())

    # Maybe separate the createVM and attach to create the disk and VM concurrently
    
    # Copy OS disk command
    copy_disk_command = 'az disk create -g {g} -n {n} --source {s}' \
                        .format(g=resource_group_name, n=copied_os_disk_name, s=target_disk_name)
    # Create new rescue VM with copied disk command
    create_rescue_vm_command = 'az vm create -g {g} -n {n} --tag owner={n} --image {image} --attach-data-disks {disk_name} --admin-password {password}' \
                               .format(g=resource_group_name, n=rescue_vm_name, image=os_image_name, disk_name=copied_os_disk_name, password=rescue_password)    
    # Add username field only for Windows
    if not is_linux:
        create_rescue_vm_command += ' --admin-username {username}'.format(username=rescue_username)
    # Validate create vm create command to validate parameters before runnning copy disk command
    validate_create_vm_command = create_rescue_vm_command + ' --validate'

    # Run all az commands
    return_code = _az_serial_caller([validate_create_vm_command, copy_disk_command, create_rescue_vm_command])

    if return_code == 0:
        pass
        #logger.warning()
    else:
        # TODO: Clean up resources here (copied disk and created rescue vm)
        logger.error("Repair swap-disk failed.")
        return None

    return 'Rescue VM: \'{n}\' succesfully created with disk: \'{d}\' attached as a data disk'.format(n=rescue_vm_name, d=copied_os_disk_name)

def restore_swap(cmd, vm_name, resource_group_name, rescue_vm_name, fixed_disk_name):

    # Get ids of rescue resources to delete first
    get_resources_command = "az resource list --tag owner={rescue_name} --query [].id -o tsv" \
                            .format(rescue_name=rescue_vm_name)
    ids = _call_az_command(get_resources_command, True).replace('\n', ' ')

    # Detach fixed disk command
    deatch_disk_command = 'az vm disk detach -g {g} --vm-name {rescue} --name {disk}' \
                          .format(g=resource_group_name, rescue=rescue_vm_name, disk=fixed_disk_name)
    # Update OS disk with fixed disk command
    attach_fixed_command = 'az vm update -g {g} -n {n} --os-disk {disk}' \
                           .format(g=resource_group_name, n=vm_name, disk=fixed_disk_name)
    # Delete rescue VM resources command
    delete_resources_command = 'az resource delete --ids {ids}' \
                               .format(ids=ids)

    # Maybe run attach and delete concurrently
    return_code = _az_serial_caller([deatch_disk_command, attach_fixed_command, delete_resources_command])

    if return_code == 0:
        pass
        #logger.warning()
    else:
        # TODO: Clean up resources here (copied disk and created rescue vm)
        logger.error("Repair restore-swap failed.")
        return None

    return "{disk} successfully attached to {n} as OS disk.".format(disk=fixed_disk_name, n=vm_name)

# check if this is reliable
def _uses_managed_disk(vm):
    if vm.storage_profile.os_disk.managed_disk is None:
        return False
    else:
        return True

# returns the return code of the subprocess.Popen
def _call_az_command(command_string, return_stdout = False):

    logger.warning(command_string)

    p1 = subprocess.Popen(command_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Wait for process to terminate and fetch stdout and stderror
    stdout, stderr = p1.communicate()

    print("stdout: " + stdout)
    print("stderr: " + stderr)

    if p1.returncode != 0:
        logger.error(stderr)
    else:
        logger.warning('\'' + command_string + '\' command succeeded.')

    if return_stdout:
        return stdout
    else:
        return p1.returncode

def _az_serial_caller(command_list):

    for command_string in command_list:
        return_code = _call_az_command(command_string)
        if return_code != 0:
            return return_code;        
    
    return 0;