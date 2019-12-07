# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import datetime
from json import loads
from re import match, search, findall
from knack.log import get_logger
from knack.util import CLIError

from azure.cli.command_modules.vm.custom import get_vm, _is_linux_os
from azure.cli.command_modules.resource._client_factory import _resource_client_factory
from msrestazure.azure_exceptions import CloudError
from msrestazure.tools import parse_resource_id, is_valid_resource_id

from .exceptions import AzCommandError
from .repair_utils import (
    _call_az_command,
    _get_repair_resource_tag,
    _uses_encrypted_disk,
    _resolve_api_version,
    check_extension_version
)

# pylint: disable=line-too-long, broad-except

logger = get_logger(__name__)
EXTENSION_NAME = 'vm-repair'


def validate_create(cmd, namespace):
    check_extension_version(EXTENSION_NAME)

    # Check if VM exists and is not classic VM
    source_vm = _validate_and_get_vm(cmd, namespace.resource_group_name, namespace.vm_name)
    is_linux = _is_linux_os(source_vm)

    # Check repair vm name
    if namespace.repair_vm_name:
        _validate_vm_name(namespace.repair_vm_name, is_linux)
    else:
        namespace.repair_vm_name = ('repair-' + namespace.vm_name)[:15]

    # Check copy disk name
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    if namespace.copy_disk_name:
        _validate_disk_name(namespace.copy_disk_name)
    else:
        namespace.copy_disk_name = namespace.vm_name + '-DiskCopy-' + timestamp

    # Check copy resouce group name
    if namespace.repair_group_name:
        if namespace.repair_group_name == namespace.resource_group_name:
            raise CLIError('The repair resource group name cannot be the same as the source VM resource group.')
        _validate_resource_group_name(namespace.repair_group_name)
    else:
        namespace.repair_group_name = 'repair-' + namespace.vm_name + '-' + timestamp

    # Check encrypted disk
    if _uses_encrypted_disk(source_vm):
        # TODO, validate this with encrypted VMs
        logger.warning('The source VM\'s OS disk is encrypted.')

    # Validate Auth Params
    # Prompt vm username
    if not namespace.repair_username:
        _prompt_repair_username(namespace)
    # Validate vm username
    validate_vm_username(namespace.repair_username, is_linux)
    # Prompt vm password
    if not namespace.repair_password:
        _prompt_repair_password(namespace)
    # Validate vm password
    validate_vm_password(namespace.repair_password, is_linux)


def validate_restore(cmd, namespace):
    check_extension_version(EXTENSION_NAME)

    # Check if VM exists and is not classic VM
    _validate_and_get_vm(cmd, namespace.resource_group_name, namespace.vm_name)

    # No repair param given, find repair vm using tags
    if not namespace.repair_vm_id:
        fetch_repair_vm(namespace)

    if not is_valid_resource_id(namespace.repair_vm_id):
        raise CLIError('Repair resource id is not valid.')

    repair_vm_id = parse_resource_id(namespace.repair_vm_id)
    # Check if data disk exists on repair VM
    repair_vm = get_vm(cmd, repair_vm_id['resource_group'], repair_vm_id['name'])
    data_disks = repair_vm.storage_profile.data_disks
    if not data_disks:
        raise CLIError('No data disks found on repair VM: {}'.format(repair_vm_id['name']))

    # Populate disk name
    if not namespace.disk_name:
        namespace.disk_name = data_disks[0].name
        logger.info('Disk-name not given. Defaulting to the first data disk attached to the repair VM: %s', data_disks[0].name)
    else:  # check disk name
        if not [disk for disk in data_disks if disk.name == namespace.disk_name]:
            raise CLIError('No data disks found on the repair VM: \'{vm}\' with the disk name: \'{disk}\''.format(vm=repair_vm_id['name'], disk=namespace.disk_name))


def validate_run(cmd, namespace):
    check_extension_version(EXTENSION_NAME)

    # Set run_on_repair to True if repair_vm_id given
    if namespace.repair_vm_id:
        namespace.run_on_repair = True

    # Check run-id and custom run file parameters
    if not namespace.run_id and not namespace.custom_script_file:
        raise CLIError('Please specify the run id with --run-id.')
    if namespace.run_id and namespace.custom_script_file:
        raise CLIError('Cannot continue with both the run-id and the custom-run-file. Please specify just one.')
    # Check if VM exists and is not classic VM
    source_vm = _validate_and_get_vm(cmd, namespace.resource_group_name, namespace.vm_name)
    is_linux = _is_linux_os(source_vm)

    if namespace.custom_script_file:
        # Check if file extension is correct
        if is_linux and not (namespace.custom_script_file.endswith('.sh') or namespace.custom_script_file.endswith('.bash')):
            raise CLIError('Only .sh or .bash scripts are supported for repair run on a Linux VM.')
        if not is_linux and not (namespace.custom_script_file.endswith('.ps1') or namespace.custom_script_file.endswith('.ps2')):
            raise CLIError('Only PowerShell scripts are supported for repair run on a Windows VM.')
        # Check if file exists
        import os.path
        if not os.path.isfile(namespace.custom_script_file):
            raise CLIError('Custom script file cannot be found. Please check if the file exists.')
        # Check for current custom-run-file parameter limitations
        if namespace.parameters:
            raise CLIError('Parameter passing does not work for custom run files yet. Please remove --parameters arguments.')
        with open(namespace.custom_script_file, 'r') as f:
            first_line = f.readline()
            if first_line.lower().startswith('param('):
                raise CLIError('Powershell param() statement does not work for custom script files yet. Please remove the param() line in the file.')

        namespace.run_id = 'no-op'

    # Check if the script type matches the OS
    if not is_linux and namespace.run_id.startswith('linux'):
        raise CLIError('Script IDs that start with \'linux\' are Linux Shell scripts. You cannot run Linux Shell scripts on a Windows VM.')
    if is_linux and namespace.run_id.startswith('win'):
        raise CLIError('Script IDs that start with \'win\' are Windows PowerShell scripts. You cannot run Windows PowerShell scripts on a Linux VM.')

    # Fetch repair vm
    if namespace.run_on_repair and not namespace.repair_vm_id:
        fetch_repair_vm(namespace)

    # If not run_on_repair, repair_vm = source_vm. Scripts directly run on source VM.
    if not namespace.run_on_repair:
        namespace.repair_vm_id = source_vm.id

    if not is_valid_resource_id(namespace.repair_vm_id):
        raise CLIError('Repair resource id is not valid.')


def _prompt_repair_username(namespace):

    from knack.prompting import prompt, NoTTYException
    try:
        namespace.repair_username = prompt('Repair VM admin username: ')
    except NoTTYException:
        raise CLIError('Please specify the username parameter in non-interactive mode.')


def _prompt_repair_password(namespace):
    from knack.prompting import prompt_pass, NoTTYException
    try:
        namespace.repair_password = prompt_pass('Repair VM admin password: ', confirm=True)
    except NoTTYException:
        raise CLIError('Please specify the password parameter in non-interactive mode.')


def _classic_vm_exists(cmd, resource_group_name, vm_name):
    classic_vm_provider = 'Microsoft.ClassicCompute'
    vm_resource_type = 'virtualMachines'

    try:
        rcf = _resource_client_factory(cmd.cli_ctx)
        api_version = _resolve_api_version(rcf, classic_vm_provider, None, vm_resource_type)
        resource_client = rcf.resources
        resource_client.get(resource_group_name, classic_vm_provider, '', vm_resource_type, vm_name, api_version)
    except CloudError as cloudError:
        # Resource does not exist or the API failed
        logger.debug(cloudError)
        return False
    except Exception as exception:
        # Unknown error, so return false for default resource not found error message
        logger.debug(exception)
        return False
    return True


def _validate_and_get_vm(cmd, resource_group_name, vm_name):
    # Check if target VM exists
    resource_not_found_error = 'ResourceNotFound'
    source_vm = None
    try:
        source_vm = get_vm(cmd, resource_group_name, vm_name)
    except CloudError as cloudError:
        logger.debug(cloudError)
        if cloudError.error.error == resource_not_found_error and _classic_vm_exists(cmd, resource_group_name, vm_name):
            # Given VM is classic VM (RDFE)
            raise CLIError('The given VM \'{}\' is a classic VM. VM repair commands do not support classic VMs.'.format(vm_name))
        # Unknown Error
        raise CLIError(cloudError.message)

    return source_vm


def _validate_vm_name(vm_name, is_linux):
    if not is_linux:
        win_pattern = r'[\'~!@#$%^&*()=+_[\]{}\\|;:.",<>?]'
        num_pattern = r'[0-9]+$'

        if len(vm_name) > 15 or search(win_pattern, vm_name) or match(num_pattern, vm_name):
            raise CLIError('Windows computer name cannot be more than 15 characters long, be entirely numeric, or contain the following characters: '
                           r'`~!@#$%^&*()=+_[]{}\|; :.\'",<>/?')


def _validate_disk_name(disk_name):
    disk_pattern = r'([a-zA-Z0-9][a-zA-Z0-9_.\-]+[a-zA-Z0-9_])$'
    if not match(disk_pattern, disk_name):
        raise CLIError('Disk name must begin with a letter or number, end with a letter, number or underscore, and may contain only letters, numbers, underscores, periods, or hyphens.')
    if len(disk_name) > 80:
        raise CLIError('Disk name only allow up to 80 characters.')


def _validate_resource_group_name(rg_name):
    rg_pattern = r'[0-9a-zA-Z._\-()]+$'
    # if match is null or ends in period, then raise error
    if not match(rg_pattern, rg_name) or rg_name[-1] == '.':
        raise CLIError('Resource group name only allow alphanumeric characters, periods, underscores, hyphens and parenthesis and cannot end in a period.')

    if len(rg_name) > 90:
        raise CLIError('Resource group name only allow up to 90 characters.')

    # Check for existing dup name
    try:
        list_rg_command = 'az group list --query "[].name"'
        logger.info('Checking for existing resource groups with identical name within subscription...')
        output = _call_az_command(list_rg_command)
    except AzCommandError as azCommandError:
        logger.error(azCommandError)
        raise CLIError('Unexpected error occured while fetching existing resource groups.')
    rg_list = loads(output)

    if rg_name in [rg.lower() for rg in rg_list]:
        raise CLIError('Resource group with name \'{}\' already exists within subscription.'.format(rg_name))


def fetch_repair_vm(namespace):
    # Find repair VM
    tag = _get_repair_resource_tag(namespace.resource_group_name, namespace.vm_name)
    try:
        find_repair_command = 'az resource list --tag {tag} --query "[?type==\'Microsoft.Compute/virtualMachines\']"' \
                              .format(tag=tag)
        logger.info('Searching for repair-vm within subscription...')
        output = _call_az_command(find_repair_command)
    except AzCommandError as azCommandError:
        logger.error(azCommandError)
        raise CLIError('Unexpected error occured while locating repair VM.')
    repair_list = loads(output)

    # No repair VM found
    if not repair_list:
        raise CLIError('Repair VM not found for {vm_name}. Run \'az vm repair create -n {vm_name} -g {rg} --verbose\' to create repair vm and rerun the command.'
                       .format(vm_name=namespace.vm_name, rg=namespace.resource_group_name))

    # More than one repair VM found
    if len(repair_list) > 1:
        message = 'More than one repair VM found:\n'
        for vm in repair_list:
            message += vm['id'] + '\n'
        message += '\nPlease specify the repair VM id using the parameter --repair-vm-id'
        raise CLIError(message)

    # One repair VM found
    namespace.repair_vm_id = repair_list[0]['id']

    logger.info('Found repair VM: %s\n', namespace.repair_vm_id)


def validate_vm_password(password, is_linux):
    """Sourced from src/azure-cli/azure/cli/command_modules/vm/_validators.py  _validate_admin_password()"""
    max_length = 72 if is_linux else 123
    min_length = 12
    if len(password) not in range(min_length, max_length + 1):
        raise CLIError('Password length must be between {} and {}'.format(min_length, max_length))

    contains_lower = findall('[a-z]+', password)
    contains_upper = findall('[A-Z]+', password)
    contains_digit = findall('[0-9]+', password)
    contains_special_char = findall(r'[ `~!@#$%^&*()=+_\[\]{}\|;:.\/\'\",<>?]+', password)
    count = len([x for x in [contains_lower, contains_upper, contains_digit, contains_special_char] if x])

    if count < 3:
        raise CLIError('Password must have the 3 of the following: 1 lower case character, 1 upper case character, 1 number and 1 special character')


def validate_vm_username(username, is_linux):
    """Sourced from src/azure-cli/azure/cli/command_modules/vm/_validators.py _validate_admin_username()"""
    pattern = (r'[\\\/"\[\]:|<>+=;,?*@#()!A-Z]+' if is_linux else r'[\\\/"\[\]:|<>+=;,?*@]+')
    linux_err = r'VM username cannot contain upper case character A-Z, special characters \/"[]:|<>+=;,?*@#()! or start with $ or -'
    win_err = r'VM username cannot contain special characters \/"[]:|<>+=;,?*@# or ends with .'

    if findall(pattern, username):
        raise CLIError(linux_err if is_linux else win_err)

    if is_linux and findall(r'^[$-]+', username):
        raise CLIError(linux_err)

    if not is_linux and username.endswith('.'):
        raise CLIError(win_err)

    # Sourced from vm module also
    disallowed_user_names = [
        "administrator", "admin", "user", "user1", "test", "user2",
        "test1", "user3", "admin1", "1", "123", "a", "actuser", "adm",
        "admin2", "aspnet", "backup", "console", "guest",
        "owner", "root", "server", "sql", "support", "support_388945a0",
        "sys", "test2", "test3", "user4", "user5"]

    if username.lower() in disallowed_user_names:
        raise CLIError("This username '{}' meets the general requirements, but is specifically disallowed. Please try a different value.".format(username))
