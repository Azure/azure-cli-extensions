# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from re import search
import json
from knack.log import get_logger
from knack.util import CLIError

from azure.cli.command_modules.vm.custom import get_vm, _is_linux_os
from repair_utils import _uses_managed_disk, _call_az_command, _get_rescue_resource_tag

# pylint: disable=line-too-long

logger = get_logger(__name__)

def validate_swap_disk(cmd, namespace):

    target_vm = get_vm(cmd, namespace.resource_group_name, namespace.vm_name)
    is_linux = _is_linux_os(target_vm)

    # Handle empty params
    if is_linux and namespace.rescue_username:
        logger.warning("Chaging adminUsername property is not allowed for Linux VMs. Ignoring the given rescue-username parameter.")
    if not is_linux and not namespace.rescue_username:
        _prompt_rescue_username(namespace)
    if not namespace.rescue_password:
        _prompt_rescue_password(namespace)

def validate_restore_swap(cmd, namespace):
    
    # Only one of the rescue param given
    if bool(namespace.rescue_vm_name) ^ bool(namespace.rescue_resource_group):
        raise CLIError('Please specify both rescue-resource-group and rescue-vm-name, or none.')
    
    # No rescue param given, find rescue vm using tags
    if not namespace.rescue_vm_name and not namespace.rescue_resource_group:
        # Find Rescue VM
        tag = _get_rescue_resource_tag(namespace.vm_name, namespace.resource_group_name)
        find_rescue_command = 'az resource list --tag {tag} --query "[?type==\'Microsoft.Compute/virtualMachines\']"' \
                              .format(tag=tag)
        logger.info('Searching for rescue-vm within subscription:')
        output = _call_az_command(find_rescue_command)
        rescue_list = json.loads(output)

        # No rescue VM found
        if len(rescue_list) == 0:
            raise CLIError('Rescue VM not found for {vm_name}. Please check if the rescue resources were not removed.'.format(vm_name=namespace.vm_name))

        # More than one rescue VM found
        if len(rescue_list) > 1:
            given_rescue_found = False
            message = 'More than one rescue VM found:\n'
            for vm in rescue_list:
                message += vm['id'] + '\n'
            message += '\nPlease specify the rescue-resource-group and rescue-vm-name to restore the disk-swap with.'
            raise CLIError(message)

        # One Rescue VM Found
        namespace.rescue_vm_name = rescue_list[0]['name']
        namespace.rescue_resource_group = rescue_list[0]['resourceGroup']
        logger.info('Found rescue vm: \'{vmname}\' in resource group: \'{rg}\''.format(vmname=namespace.rescue_vm_name, rg=namespace.rescue_resource_group))

    # Check if data disk exists on rescue VM
    rescue_vm = get_vm(cmd, namespace.rescue_resource_group, namespace.rescue_vm_name)
    is_managed = _uses_managed_disk(rescue_vm)
    data_disks = rescue_vm.storage_profile.data_disks
    if data_disks is None or len(data_disks) < 1:
        raise CLIError('No data disks found on rescue VM: {}'.format(namespace.rescue_vm_name))

    # Populate data disk name and uri
    if not namespace.disk_name:
        namespace.disk_name = data_disks[0].name
        logger.warning('Disk-name not given. Defaulting to the first data disk attached to the rescue VM: {}'.format(data_disks[0].name))
    if not namespace.disk_uri and not is_managed:
        namespace.disk_uri = data_disks[0].vhd.uri
        logger.warning('Disk-uri not given. Defaulting to the first data disk attached to the rescue VM: {}'.format(data_disks[0].vhd.uri))

def _prompt_rescue_username(namespace):

    from knack.prompting import prompt, NoTTYException
    try:
        namespace.rescue_username = prompt('Rescue VM Admin username: ')
    except NoTTYException:
        raise CLIError('Please specify username in non-interactive mode.')

def _prompt_rescue_password(namespace):
    from knack.prompting import prompt_pass, NoTTYException
    try:
        namespace.rescue_password = prompt_pass('Rescue VM Admin Password: ', confirm=True)
    except NoTTYException:
        raise CLIError('Please specify password in non-interactive mode.')
