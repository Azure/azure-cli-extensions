# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from re import search

from knack.log import get_logger
from knack.util import CLIError

from azure.cli.command_modules.vm.custom import get_vm, _is_linux_os
from .custom import _uses_managed_disk

# pylint: disable=line-too-long

logger = get_logger(__name__)

def validate_swap_disk(cmd, namespace):

    target_vm = get_vm(cmd, namespace.resource_group_name, namespace.vm_name)
    is_linux = _is_linux_os(target_vm)

    # Validate params that aren't checked by 'vm create' command
    if namespace.rescue_vm_name:
        _validate_rescue_vm_name(namespace.rescue_vm_name, is_linux)

    # Handle empty params
    if is_linux and namespace.rescue_username:
        logger.warning("Chaging adminUsername property is not allowed for Linux VMs. Ignoring the given rescue-username parameter.")
    if not is_linux and not namespace.rescue_username:
        _prompt_rescue_username(namespace)
    if not namespace.rescue_password:
        _prompt_rescue_password(namespace)

def validate_restore_swap(cmd, namespace):

    # Check if data disk exists on rescue VM
    rescue_vm = get_vm(cmd, namespace.resource_group_name, namespace.rescue_vm_name)
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

def _validate_rescue_vm_name(rescue_vm_name, is_linux):

    if not is_linux:
        win_pattern = r'[\'~!@#$%^&*()=+_[\]{}\\|;:.",<>?]'

        if len(rescue_vm_name) > 15 or search(win_pattern, rescue_vm_name):
            raise CLIError('Windows computer name cannot be more than 15 characters long, be entirely numeric, or contain the following characters: ' \
                           '`~!@#$%^&*()=+_[]{}\\|; :.\'",<>/?')

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
