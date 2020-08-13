# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess
import shlex
import os
import re
from json import loads
import pkgutil
import requests

from knack.log import get_logger
from knack.prompting import prompt_y_n, NoTTYException

from .encryption_types import Encryption

from .exceptions import AzCommandError, WindowsOsNotAvailableError, RunScriptNotFoundForIdError
# pylint: disable=line-too-long, deprecated-method

REPAIR_MAP_URL = 'https://raw.githubusercontent.com/Azure/repair-script-library/master/map.json'

logger = get_logger(__name__)


def _uses_managed_disk(vm):
    if vm.storage_profile.os_disk.managed_disk is None:
        return False
    return True


def _call_az_command(command_string, run_async=False, secure_params=None):
    """
    Uses subprocess to run a command string. To hide sensitive parameters from logs, add the
    parameter in secure_params. If run_async is False then function returns the stdout.
    Raises AzCommandError if command fails.
    """

    tokenized_command = shlex.split(command_string)

    # If command does not start with 'az' then raise exception
    if not tokenized_command or tokenized_command[0] != 'az':
        raise AzCommandError("The command string is not an 'az' command!")
    # If run on windows, add 'cmd /c'
    windows_os_name = 'nt'
    if os.name == windows_os_name:
        tokenized_command = ['cmd', '/c'] + tokenized_command

    # Hide sensitive data such as passwords from logs
    if secure_params:
        for param in secure_params:
            if param:
                command_string = command_string.replace(param, '********')
    logger.debug("Calling: %s", command_string)
    process = subprocess.Popen(tokenized_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # Wait for process to terminate and fetch stdout and stderror
    if not run_async:
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise AzCommandError(stderr)

        logger.debug('Success.\n')

        return stdout
    return None


def _get_current_vmrepair_version():
    from azure.cli.core.extension.operations import list_extensions
    version = [ext['version'] for ext in list_extensions() if ext['name'] == 'vm-repair']
    if version:
        return version[0]
    return None


def check_extension_version(extension_name):
    from azure.cli.core.extension.operations import list_available_extensions, list_extensions

    available_extensions = list_available_extensions()
    installed_extensions = list_extensions()
    extension_to_check = [ext for ext in installed_extensions if ext['name'] == extension_name]
    if not extension_to_check:
        logger.debug('The extension with name %s does not exist within installed extensions.', extension_name)
        return

    extension_to_check = extension_to_check[0]

    for ext in available_extensions:
        if ext['name'] == extension_name and ext['version'] > extension_to_check['version']:
            logger.warning('The %s extension is not up to date, please update with az extension update -n %s', extension_name, extension_name)
            return

    logger.debug('The extension with name %s does not exist within available extensions.', extension_name)


def _clean_up_resources(resource_group_name, confirm):

    try:
        if confirm:
            message = 'The clean-up will remove the resource group \'{rg}\' and all repair resources within:\n\n{r}' \
                      .format(rg=resource_group_name, r='\n'.join(_list_resource_ids_in_rg(resource_group_name)))
            logger.warning(message)
            if not prompt_y_n('Continue with clean-up and delete resources?'):
                logger.warning('Skipping clean-up')
                return

        delete_resource_group_command = 'az group delete --name {name} --yes --no-wait'.format(name=resource_group_name)
        logger.info('Cleaning up resources by deleting repair resource group \'%s\'...', resource_group_name)
        _call_az_command(delete_resource_group_command)
    # NoTTYException exception only thrown from confirm block
    except NoTTYException:
        logger.warning('Cannot confirm clean-up resouce in non-interactive mode.')
        logger.warning('Skipping clean-up')
        return
    except AzCommandError as azCommandError:
        # Only way to distinguish errors
        resource_not_found_error_string = 'could not be found'
        if resource_not_found_error_string in str(azCommandError):
            logger.info('Resource group not found. Skipping clean up.')
            return
        logger.error(azCommandError)
        logger.error("Clean up failed.")


def _fetch_compatible_sku(source_vm):

    location = source_vm.location
    source_vm_sku = source_vm.hardware_profile.vm_size

    # First get the source_vm sku, if its available go with it
    check_sku_command = 'az vm list-skus -s {sku} -l {loc} --query [].name -o tsv'.format(sku=source_vm_sku, loc=location)

    logger.info('Checking if source VM size is available...')
    sku_check = _call_az_command(check_sku_command).strip('\n')

    if sku_check:
        logger.info('Source VM size \'%s\' is available. Using it to create repair VM.\n', source_vm_sku)
        return source_vm_sku

    logger.info('Source VM size: \'%s\' is NOT available.\n', source_vm_sku)

    # List available standard SKUs
    # TODO, premium IO only when needed
    list_sku_command = 'az vm list-skus -s standard_d -l {loc} --query ' \
                       '"[?capabilities[?name==\'vCPUs\' && to_number(value)>= to_number(\'2\')] && ' \
                       'capabilities[?name==\'vCPUs\' && to_number(value)<= to_number(\'8\')] && ' \
                       'capabilities[?name==\'MemoryGB\' && to_number(value)>=to_number(\'8\')] && ' \
                       'capabilities[?name==\'MemoryGB\' && to_number(value)<=to_number(\'32\')] && ' \
                       'capabilities[?name==\'MaxDataDiskCount\' && to_number(value)>to_number(\'0\')] && ' \
                       'capabilities[?name==\'PremiumIO\' && value==\'True\']].name" -o json'\
                       .format(loc=location)

    logger.info('Fetching available VM sizes for repair VM...')
    sku_list = loads(_call_az_command(list_sku_command).strip('\n'))

    if sku_list:
        logger.info('VM size \'%s\' is available. Using it to create repair VM.\n', sku_list[0])
        return sku_list[0]

    return None


def _fetch_disk_info(resource_group_name, disk_name):
    """ Returns sku, location, os_type, hyperVgeneration as tuples """
    show_disk_command = 'az disk show -g {g} -n {name} --query [sku.name,location,osType,hyperVgeneration] -o json'.format(g=resource_group_name, name=disk_name)
    disk_info = loads(_call_az_command(show_disk_command))
    # Note that disk_info will always have 4 elements if the command succeeded, if it fails it will cause an exception
    sku, location, os_type, hyper_v_version = disk_info[0], disk_info[1], disk_info[2], disk_info[3]
    return (sku, location, os_type, hyper_v_version)


def _get_repair_resource_tag(resource_group_name, source_vm_name):
    return 'repair_source={rg}/{vm_name}'.format(rg=resource_group_name, vm_name=source_vm_name)


def _list_resource_ids_in_rg(resource_group_name):
    get_resources_command = 'az resource list --resource-group {rg} --query [].id -o json' \
                            .format(rg=resource_group_name)
    logger.debug('Fetching resources in resource group...')
    ids = loads(_call_az_command(get_resources_command))
    return ids


def _fetch_encryption_settings(source_vm):
    key_vault = None
    kekurl = None
    if source_vm.storage_profile.os_disk.encryption_settings is not None:
        return Encryption.DUAL, key_vault, kekurl
    # Unmanaged disk only support dual
    if not _uses_managed_disk(source_vm):
        return Encryption.NONE, key_vault, kekurl

    disk_id = source_vm.storage_profile.os_disk.managed_disk.id
    show_disk_command = 'az disk show --id {i} --query [encryptionSettingsCollection,encryptionSettingsCollection.encryptionSettings[].diskEncryptionKey.sourceVault.id,encryptionSettingsCollection.encryptionSettings[].keyEncryptionKey.keyUrl] -o json'.format(i=disk_id)
    encryption_type, key_vault, kekurl = loads(_call_az_command(show_disk_command))
    if [encryption_type, key_vault, kekurl] == [None, None, None]:
        return Encryption.NONE, key_vault, kekurl
    if kekurl == []:
        key_vault = key_vault[0]
        return Encryption.SINGLE_WITHOUT_KEK, key_vault, kekurl
    key_vault, kekurl = key_vault[0], kekurl[0]
    return Encryption.SINGLE_WITH_KEK, key_vault, kekurl


def _unlock_singlepass_encrypted_disk(source_vm, is_linux, repair_group_name, repair_vm_name):
    # Installs the extension on repair VM and mounts the disk after unlocking.
    encryption_type, key_vault, kekurl = _fetch_encryption_settings(source_vm)
    if is_linux:
        volume_type = 'DATA'
    else:
        volume_type = 'ALL'

    try:
        if encryption_type is Encryption.SINGLE_WITH_KEK:
            install_ade_extension_command = 'az vm encryption enable --disk-encryption-keyvault {vault} --name {repair} --resource-group {g} --key-encryption-key {kek_url} --volume-type {volume}' \
                                            .format(g=repair_group_name, repair=repair_vm_name, vault=key_vault, kek_url=kekurl, volume=volume_type)
        elif encryption_type is Encryption.SINGLE_WITHOUT_KEK:
            install_ade_extension_command = 'az vm encryption enable --disk-encryption-keyvault {vault} --name {repair} --resource-group {g} --volume-type {volume}' \
                                            .format(g=repair_group_name, repair=repair_vm_name, vault=key_vault, volume=volume_type)
        logger.info('Unlocking attached copied disk...')
        _call_az_command(install_ade_extension_command)
        # Linux VM encryption extension has a bug and we need to manually unlock and mount its disk
        if is_linux:
            logger.debug("Manually unlocking and mounting disk for Linux VMs.")
            _manually_unlock_mount_encrypted_disk(repair_group_name, repair_vm_name)
    except AzCommandError as azCommandError:
        error_message = str(azCommandError)
        # Linux VM encryption extension bug where it fails and then continue to mount disk manually
        if is_linux and "Failed to encrypt data volumes with error" in error_message:
            logger.debug("Expected bug for linux VMs. Ignoring error.")
            _manually_unlock_mount_encrypted_disk(repair_group_name, repair_vm_name)
        else:
            raise


def _manually_unlock_mount_encrypted_disk(repair_group_name, repair_vm_name):
    # Unlocks the disk using the phasephrase and mounts it on the repair VM.
    REPAIR_DIR_NAME = 'azext_vm_repair'
    SCRIPTS_DIR_NAME = 'scripts'
    LINUX_RUN_SCRIPT_NAME = 'mount-encrypted-disk.sh'
    command_id = 'RunShellScript'
    loader = pkgutil.get_loader(REPAIR_DIR_NAME)
    mod = loader.load_module(REPAIR_DIR_NAME)
    rootpath = os.path.dirname(mod.__file__)
    run_script = os.path.join(rootpath, SCRIPTS_DIR_NAME, LINUX_RUN_SCRIPT_NAME)
    mount_disk_command = 'az vm run-command invoke -g {rg} -n {vm} --command-id {command_id} ' \
                         '--scripts "@{run_script}" -o json' \
                         .format(rg=repair_group_name, vm=repair_vm_name, command_id=command_id, run_script=run_script)
    _call_az_command(mount_disk_command)


def _fetch_compatible_windows_os_urn(source_vm):
    location = source_vm.location
    fetch_urn_command = 'az vm image list -s "2016-Datacenter" -f WindowsServer -p MicrosoftWindowsServer -l {loc} --verbose --all --query "[?sku==\'2016-Datacenter\'].urn | reverse(sort(@))" -o json'.format(loc=location)
    logger.info('Fetching compatible Windows OS images from gallery...')
    urns = loads(_call_az_command(fetch_urn_command))

    # No OS images available for Windows2016
    if not urns:
        raise WindowsOsNotAvailableError()

    logger.debug('Fetched Urns:\n%s', urns)
    # temp fix to mitigate Windows disk signature collision error
    os_image_ref = source_vm.storage_profile.image_reference
    if os_image_ref and isinstance(os_image_ref.version, str) and os_image_ref.version in urns[0]:
        if len(urns) < 2:
            logger.debug('Avoiding Win2016 latest image due to expected disk collision. But no other image available.')
            raise WindowsOsNotAvailableError()
        logger.debug('Returning Urn 1 to avoid disk collision error: %s', urns[1])
        return urns[1]
    logger.debug('Returning Urn 0: %s', urns[0])
    return urns[0]


def _resolve_api_version(rcf, resource_provider_namespace, parent_resource_path, resource_type):

    provider = rcf.providers.get(resource_provider_namespace)
    # If available, we will use parent resource's api-version

    resource_type_str = (parent_resource_path.split('/')[0] if parent_resource_path else resource_type)
    rt = [t for t in provider.resource_types if t.resource_type.lower() == resource_type_str.lower()]
    if not rt:
        raise Exception('Resource type {} not found.'.format(resource_type_str))
    if len(rt) == 1 and rt[0].api_versions:
        npv = [v for v in rt[0].api_versions if 'preview' not in v.lower()]
        return npv[0] if npv else rt[0].api_versions[0]
    raise Exception(
        'API version is required and could not be resolved for resource {}'
        .format(resource_type))


def _fetch_run_script_map():

    # Fetch map.json from GitHub
    response = requests.get(url=REPAIR_MAP_URL)
    # Raise exception when request fails
    response.raise_for_status()

    return response.json()


def _fetch_run_script_path(run_id):

    map_json = _fetch_run_script_map()
    repair_script_path = [script['path'] for script in map_json if script['id'] == run_id]
    if repair_script_path:
        return repair_script_path[0]

    raise RunScriptNotFoundForIdError('Run-script not found for id: {}. Please validate if the id is correct.'.format(run_id))


def _process_ps_parameters(parameters):
    """
    Returns a ps script formatted parameter string from a list of parameters.
    Example: [param1=1, param2=2] => -param1 1 -param2 2
    """
    param_string = ''
    for param in parameters:
        if '=' in param:
            n, v = param.split('=', 1)
            param_string += '-{name} {value} '.format(name=n, value=v)
        else:
            param_string += '{} '.format(param)

    return param_string.strip(' ')


def _process_bash_parameters(parameters):
    """
    Returns a bash script formatted parameter string from a list of parameters.
    Example: [param1=1, param2=2] => 1 2
    """
    param_string = ''
    for param in parameters:
        if '=' in param:
            param = param.split('=', 1)[1]
        param_string += '{p} '.format(p=param)

    return param_string.strip(' ')


def _parse_run_script_raw_logs(log_string):
    """
    Splits one aggregate log string into a list of each log entry.
    """
    pattern = r'((?=\[(?:Log-Start|Log-End|Output|Info|Warning|Error|Debug) ' \
              r'[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]\])|(?=\[STATUS\]))'
    log_list = _regex_split(pattern, log_string)
    # Remove empty strings in logs
    log_list = list(filter(None, log_list))
    # Format them in dictionary to parse out level
    logs_dict_list = []
    for log in log_list:
        log_dict = {}
        log_dict['message'] = log.strip('\n')
        # Set log level property
        if '[STATUS]::' in log_dict['message']:
            log_dict['level'] = 'STATUS'
        else:
            log_dict['level'] = log_dict['message'].split(' ', 1)[0][1:]
        logs_dict_list.append(log_dict)

    return logs_dict_list


def _regex_split(pattern, string):
    """
    Custom split function for zero width split fix.
    """
    splits = list((m.start(), m.end()) for m in re.finditer(pattern, string))
    starts = [0] + [i[1] for i in splits]
    ends = [i[0] for i in splits] + [len(string)]
    return [string[start:end] for start, end in zip(starts, ends)]


def _check_script_succeeded(log_string):

    status_success = '[STATUS]::SUCCESS'
    # status_failure = '[STATUS]::ERROR'

    return status_success in log_string


def _get_function_param_dict(frame):
    import inspect
    # getargvalues inadvertently marked as deprecated in Python 3.5
    _, _, _, values = inspect.getargvalues(frame)
    if 'cmd' in values:
        del values['cmd']
    secure_params = ['repair_password', 'repair_username']
    for param in secure_params:
        if param in values:
            values[param] = '********'
    return values
