# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from knack.log import get_logger
from knack.util import CLIError

from azure.cli.command_modules.vm.custom import get_vm, _is_linux_os
from azure.cli.command_modules.resource._client_factory import _resource_client_factory
from msrestazure.azure_exceptions import CloudError
from msrestazure.tools import parse_resource_id, is_valid_resource_id

from .repair_utils import _call_az_command, _get_rescue_resource_tag, _uses_encrypted_disk

# pylint: disable=line-too-long

logger = get_logger(__name__)

def validate_swap_disk(cmd, namespace):

    # Check if VM exists and is not classic VM
    target_vm = _validate_and_get_vm(cmd, namespace.resource_group_name, namespace.vm_name)

    # Check encrypted disk
    if _uses_encrypted_disk(target_vm):
        # TODO, validate this with encrypted VMs
        logger.warning('The faulty VM OS disk is encrypted!')
    is_linux = _is_linux_os(target_vm)

    # Handle empty params
    if is_linux and namespace.rescue_username:
        logger.warning("Chaging adminUsername property is not allowed for Linux VMs. Ignoring the given rescue-username parameter.")
    if not is_linux and not namespace.rescue_username:
        _prompt_rescue_username(namespace)
    if not namespace.rescue_password:
        _prompt_rescue_password(namespace)

def validate_restore_swap(cmd, namespace):

    # Check if VM exists and is not classic VM
    target_vm = _validate_and_get_vm(cmd, namespace.resource_group_name, namespace.vm_name)

    # No rescue param given, find rescue vm using tags
    if not namespace.rescue_vm_id:
        # Find Rescue VM
        tag = _get_rescue_resource_tag(namespace.resource_group_name, namespace.vm_name)
        find_rescue_command = 'az resource list --tag {tag} --query "[?type==\'Microsoft.Compute/virtualMachines\']"' \
                              .format(tag=tag)
        logger.info('Searching for rescue-vm within subscription:')
        output = _call_az_command(find_rescue_command)
        rescue_list = json.loads(output)

        # No rescue VM found
        if not rescue_list:
            raise CLIError('Rescue VM not found for {vm_name}. Please check if the rescue resources were removed.'.format(vm_name=namespace.vm_name))

        # More than one rescue VM found
        if len(rescue_list) > 1:
            message = 'More than one rescue VM found:\n'
            for vm in rescue_list:
                message += vm['id'] + '\n'
            message += '\nPlease specify the --rescue-vm-id to restore the disk-swap with.'
            raise CLIError(message)

        # One Rescue VM Found
        namespace.rescue_vm_id = rescue_list[0]['id']
        logger.info('Found rescue vm: %s', namespace.rescue_vm_id)

    if not is_valid_resource_id(namespace.rescue_vm_id):
        raise CLIError('Rescue resource id is not valid.')

    rescue_vm_id = parse_resource_id(namespace.rescue_vm_id)
    # Check if data disk exists on rescue VM
    rescue_vm = get_vm(cmd, rescue_vm_id['resource_group'], rescue_vm_id['name'])
    data_disks = rescue_vm.storage_profile.data_disks
    if not data_disks:
        raise CLIError('No data disks found on rescue VM: {}'.format(rescue_vm_id['name']))

    # Populate disk name
    if not namespace.disk_name:
        namespace.disk_name = data_disks[0].name
        logger.warning('Disk-name not given. Defaulting to the first data disk attached to the rescue VM: %s', data_disks[0].name)
    else: # check disk name
        if not [disk for disk in data_disks if disk.name == namespace.disk_name]:
            raise CLIError('No data disks found on the rescue VM: \'{vm}\' with the disk name: \'{disk}\''.format(vm=rescue_vm_id['name'], disk=namespace.disk_name))

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

def _classic_vm_exists(cmd, resource_group_name, vm_name):
    api_version = '2017-04-01'
    classic_vm_provider = 'Microsoft.ClassicCompute'
    vm_resource_type = 'virtualMachines'

    resource_client = _resource_client_factory(cmd.cli_ctx).resources
    vm = None
    try:
        vm = resource_client.get(resource_group_name, classic_vm_provider, '', vm_resource_type, vm_name, api_version)
    except CloudError as cloudError:
        # Resource does not exist or the API failed
        logger.debug(cloudError)
        return False
    return True

def _validate_and_get_vm(cmd, resource_group_name, vm_name):

    # Check if target VM exists
    resource_not_found_error = 'ResourceNotFound'
    target_vm = None
    try:
        target_vm = get_vm(cmd, resource_group_name, vm_name)
    except CloudError as cloudError:
        logger.debug(cloudError)
        if cloudError.error.error == resource_not_found_error and _classic_vm_exists(cmd, resource_group_name, vm_name):
            # Given VM is classic VM (RDFE)
            raise CLIError('The given VM \'{}\' is a classic VM. VM Repair commands do not support classic VMs.'.format(vm_name))
        # Unknown Error
        raise CLIError(cloudError.message)

    return target_vm