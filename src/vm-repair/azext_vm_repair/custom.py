# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger

from azure.cli.command_modules.vm.custom import get_vm, _is_linux_os
from azure.cli.command_modules.storage.storage_url_helpers import StorageResourceIdentifier

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

    resource_tag = "temp"

    #TODO, Maybe separate the createVM and attach to create the disk and VM concurrently
    #TODO, stop and start VM according to documentation recommendation

    # Set up base create vm command
    create_rescue_vm_command = 'az vm create -g {g} -n {n} --tag owner={n} --image {image} --admin-password {password}' \
                                       .format(g=resource_group_name, n=rescue_vm_name, image=os_image_name, password=rescue_password)    
    # Add username field only for Windows
    if not is_linux:
        create_rescue_vm_command += ' --admin-username {username}'.format(username=rescue_username)

    # Main command calling block
    try:
        # Stop Target VM
        stop_vm_command = 'az vm stop -g {g} -n {n}' \
                           .format(g=resource_group_name, n=vm_name)
        _call_az_command(stop_vm_command)

        # MANAGED DISK
        if is_managed:
            # Copy OS disk command
            copy_disk_command = 'az disk create -g {g} -n {n} --source {s}' \
                                .format(g=resource_group_name, n=copied_os_disk_name, s=target_disk_name)
            # Create new rescue VM with copied disk command
            create_rescue_vm_command = create_rescue_vm_command + ' --attach-data-disks {disk_name}'.format(disk_name=copied_os_disk_name)
            # Validate create vm create command to validate parameters before runnning copy disk command
            validate_create_vm_command = create_rescue_vm_command + ' --validate'

            _call_az_command(validate_create_vm_command)
            _call_az_command(stop_vm_command)
            _call_az_command(copy_disk_command)
            _call_az_command(create_rescue_vm_command)
        
        # UNMANAGED DISK
        else:
            os_disk_uri = target_vm.storage_profile.os_disk.vhd.uri
            copied_os_disk_name = copied_os_disk_name + '.vhd'
            # TODO, validate with Tosin about using this
            storage_account = StorageResourceIdentifier(cmd.cli_ctx.cloud, os_disk_uri)
            # Validate create vm create command to validate parameters before runnning copy disk commands
            validate_create_vm_command = create_rescue_vm_command + ' --validate'
            _call_az_command(validate_create_vm_command)
        
            # get storage account connection string
            get_connection_string_command = 'az storage account show-connection-string -g {g} -n {n} --query connectionString -o tsv' \
                                            .format(g=resource_group_name, n=storage_account.account_name)
            connection_string = _call_az_command(get_connection_string_command).strip('\n')

            # Create Snapshot of Unmanaged Disk
            make_snapshot_command = 'az storage blob snapshot -c {c} -n {n} --connection-string "{con_string}" --query snapshot -o tsv' \
                                    .format(c=storage_account.container, n=storage_account.blob, con_string=connection_string)
            snapshot_timestamp = _call_az_command(make_snapshot_command).strip('\n')
            snapshot_uri = os_disk_uri + '?snapshot={timestamp}'.format(timestamp=snapshot_timestamp)
        
            # Copy Snapshot into unmanaged Disk
            copy_snapshot_command = 'az storage blob copy start -c {c} -b {name} --source-uri {source} --connection-string "{con_string}"' \
                                    .format(c=storage_account.container, name=copied_os_disk_name, source=snapshot_uri, con_string=connection_string)
            _call_az_command(copy_snapshot_command)
             # Generate the copied disk uri
            copied_disk_uri = os_disk_uri.rstrip(storage_account.blob) + copied_os_disk_name

            import time
            time.sleep(5)

            # Create new rescue VM with copied ummanaged disk command
            create_rescue_vm_command = create_rescue_vm_command + ' --use-unmanaged-disk --attach-data-disks {uri}' \
                                       .format
            _call_az_command(create_rescue_vm_command)

           

            # Attach copied unmanaged disk to new vm
            attach_disk_command = "az vm unmanaged-disk attach -g {g} -n {disk_name} --vm-name {vm_name} --vhd-uri {uri}" \
                                  .format(g=resource_group_name, disk_name=copied_os_disk_name, vm_name=rescue_vm_name, uri=copied_disk_uri)
            _call_az_command(attach_disk_command)
        
    # Some error happened. Stop command and clean-up resources.
    except Exception as exception:
        logger.error(exception)
        logger.error("Repair swap-disk failed, cleaning up resouces.")
        _clean_up_resources(resource_tag)

        return None

    return 'Rescue VM: \'{n}\' succesfully created with disk: \'{d}\' attached as a data disk'.format(n=rescue_vm_name, d=copied_os_disk_name)

def restore_swap(cmd, vm_name, resource_group_name, rescue_vm_name, fixed_disk_name):

    # Get ids of rescue resources to delete first
    get_resources_command = "az resource list --tag owner={rescue_name} --query [].id -o tsv" \
                            .format(rescue_name=rescue_vm_name)
    ids = _call_az_command(get_resources_command).replace('\n', ' ')

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
    _call_az_command(deatch_disk_command)
    _call_az_command(attach_fixed_command)
    _call_az_command(delete_resources_command)

    return "{disk} successfully attached to {n} as OS disk.".format(disk=fixed_disk_name, n=vm_name)

# check if this is reliable
def _uses_managed_disk(vm):
    if vm.storage_profile.os_disk.managed_disk is None:
        return False
    else:
        return True

# returns the stdout, raises exception if command fails
def _call_az_command(command_string, run_async = False):

    logger.warning("calling: " + command_string)

    p1 = subprocess.Popen(command_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Wait for process to terminate and fetch stdout and stderror
    if not run_async:
        stdout, stderr = p1.communicate()

        print("stdout: " + stdout)
        print("stderr: " + stderr)

        if p1.returncode != 0:
            logger.error(stderr)
            raise Exception("{command} failed with return code: {return_code}, and stderr: {err}" \
                            .format(command=command_string, return_code=p1.returncode, err=stderr))
        else:
            logger.warning('\'' + command_string + '\' command succeeded.')

        return stdout
    
    return None

def _clean_up_resources(tag):
    pass