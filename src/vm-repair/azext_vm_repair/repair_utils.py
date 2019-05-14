# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess
import shlex
import os

from knack.log import get_logger
from knack.prompting import prompt_y_n, NoTTYException

from .exceptions import AzCommandError
# pylint: disable=line-too-long

logger = get_logger(__name__)

def _uses_managed_disk(vm):
    if vm.storage_profile.os_disk.managed_disk is None:
        return False
    return True

def _call_az_command(command_string, run_async=False, secure_params=None):
    """
    Uses subprocess to run a command string. To hide sensitive parameters from logs, add the
    parameter in secure_params. If run_async is False then function returns the stdout,
    raises exception if command fails.
    """

    tokenized_command = shlex.split(command_string)
    # If run on windows, add 'cmd /c'
    windows_os_name = 'nt'
    if os.name == windows_os_name:
        tokenized_command = ['cmd', '/c'] + tokenized_command

    # Hide sensitive data such as passwords from logs
    if secure_params:
        for param in secure_params:
            command_string = command_string.replace(param, '********')
    logger.debug("Calling: %s", command_string)
    process = subprocess.Popen(tokenized_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # Wait for process to terminate and fetch stdout and stderror
    if not run_async:
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            #logger.error(stderr)
            raise AzCommandError(stderr)

        logger.debug('Success.\n')

        return stdout
    return None

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
        logger.info('Cleaning up resources by deleting repair resource group: \'%s\'...', resource_group_name)
        _call_az_command(delete_resource_group_command)
    # Exception only thrown from confirm block
    except NoTTYException:
        logger.warning('Cannot confirm clean-up resouce in non-interactive mode.')
        logger.warning('Skipping clean-up')
        return
    except AzCommandError as azCommandError:
        resource_not_found_error_string = 'could not be found'
        if resource_not_found_error_string in str(azCommandError):
            logger.info('Resource group not found. Skipping clean up.')
            return
        logger.error(azCommandError)
        logger.error("Clean up failed.")

def _clean_up_resources_with_tag(tag):
    try:
        # Get ids of repair resources to delete first
        get_resources_command = 'az resource list --tag {tags} --query [].id -o tsv' \
                                .format(tags=tag)
        logger.info('Fetching created repair resources for clean-up...')
        ids = _call_az_command(get_resources_command).replace('\n', ' ')
        # Delete repair VM resources command
        if ids:
            delete_resources_command = 'az resource delete --ids {ids}' \
                                       .format(ids=ids)
            logger.info('Cleaning up resources...')
            _call_az_command(delete_resources_command)
        else:
            logger.info('No resources found with tag: %s. Skipping clean up.', tag)
    except AzCommandError as azCommandError:
        logger.error(azCommandError)
        logger.error("Clean up failed.")

def _fetch_compatible_sku(target_vm):

    location = target_vm.location
    target_vm_sku = target_vm.hardware_profile.vm_size

    # First get the target_vm sku, if its available go with it
    check_sku_command = 'az vm list-skus -s {sku} -l {loc} --query [].name -o tsv'.format(sku=target_vm_sku, loc=location)

    logger.info('Checking if target VM size is available...')
    sku_check = _call_az_command(check_sku_command).strip('\n')

    if sku_check:
        logger.info('Faulty VM size: \'%s\' is available. Using it to create repair VM.\n', target_vm_sku)
        return target_vm_sku

    logger.info('Faulty VM size: \'%s\' is NOT available.\n', target_vm_sku)

    # List available standard SKUs
    # TODO, premium IO only when needed
    list_sku_command = 'az vm list-skus -s standard_d -l {loc} --query ' \
                       '"[?capabilities[?name==\'vCPUs\' && to_number(value)<= to_number(\'4\')] && ' \
                       'capabilities[?name==\'MemoryGB\' && to_number(value)<=to_number(\'16\')] && ' \
                       'capabilities[?name==\'MaxDataDiskCount\' && to_number(value)>to_number(\'0\')] && ' \
                       'capabilities[?name==\'PremiumIO\' && value==\'True\']].name"'\
                       ' -o tsv' \
                       .format(loc=location)

    logger.info('Fetching available VM sizes for repair VM:')
    sku_list = _call_az_command(list_sku_command).strip('\n').split('\n')

    if sku_list:
        return sku_list[0]

    return None

def _get_repair_resource_tag(resource_group_name, target_vm_name):
    return 'repair_source={rg}/{vm_name}'.format(rg=resource_group_name, vm_name=target_vm_name)

def _list_resource_ids_in_rg(resource_group_name):
    get_resources_command = 'az resource list --resource-group {rg} --query [].id -o tsv' \
                            .format(rg=resource_group_name)
    logger.info('Fetching resources in resource group...')
    ids = _call_az_command(get_resources_command).strip('\n').split('\n')
    return ids

def _uses_encrypted_disk(vm):
    return vm.storage_profile.os_disk.encryption_settings
       