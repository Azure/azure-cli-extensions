# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess
import shlex
import os

from knack.log import get_logger

# pylint: disable=line-too-long, broad-except

logger = get_logger(__name__)

# TODO, double check if this is reliable
def _uses_managed_disk(vm):
    if vm.storage_profile.os_disk.managed_disk is None:
        return False
    return True

def _call_az_command(command_string, run_async=False, secure_params=None):
    """
    Uses subprocess to run a command string. To hide sensitive parameters from logs, add the
    parameter in secure_params. If run_async is True then function returns the stdout,
    raises exception if command fails.
    """

    tokenized_command = shlex.split(command_string)
    # If run on windows, add 'cmd /c'
    if os.name == 'nt':
        tokenized_command = ['cmd', '/c'] + tokenized_command

    # Hide sensitive data such as passwords from logs
    if secure_params:
        for param in secure_params:
            command_string = command_string.replace(param, '********')
    logger.debug("Calling: %s", command_string)
    process = subprocess.Popen(tokenized_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Wait for process to terminate and fetch stdout and stderror
    if not run_async:
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            #logger.error(stderr)
            raise Exception(stderr)

        logger.info('Success.\n')

        return stdout
    return None

# TODO, add checks for safe delete
def _clean_up_resources(resource_group_name):
    try:
        delete_resource_group_command = 'az group delete --name {name} --yes --no-wait'.format(name=resource_group_name)
        logger.info('Cleaning up resources by deleting rescue resource group: \'%s\'...', resource_group_name)
        _call_az_command(delete_resource_group_command)
    except Exception as exception:
        # Exception doesn't give enough attributes so string matching
        if 'could not be found' in str(exception):
            logger.info('Resource group not created yet. Skipping clean up.')
            return
        logger.error(exception)
        logger.error("Clean up failed.")

def _clean_up_resources_with_tag(tag):
    try:
        # Get ids of rescue resources to delete first
        get_resources_command = 'az resource list --tag {tags} --query [].id -o tsv' \
                                .format(tags=tag)
        logger.info('Fetching created rescue resources for clean-up...')
        ids = _call_az_command(get_resources_command).replace('\n', ' ')
        # Delete rescue VM resources command
        if ids:
            delete_resources_command = 'az resource delete --ids {ids}' \
                                       .format(ids=ids)
            logger.info('Cleaning up resources...')
            _call_az_command(delete_resources_command)
        else:
            logger.info('No resources found with tag: %s. Skipping clean up.', tag)
    except Exception as exception:
        logger.error(exception)
        logger.error("Clean up failed.")

def _fetch_compatible_sku(target_vm):

    location = target_vm.location
    target_vm_sku = target_vm.hardware_profile.vm_size

    # First get the target_vm sku, if its available go with it
    check_sku_command = 'az vm list-skus -s {sku} -l {loc} --query [].name -o tsv'.format(sku=target_vm_sku, loc=location)

    logger.info('Checking if target VM size is available...')
    sku_check = _call_az_command(check_sku_command).strip('\n')

    if sku_check:
        logger.info('Faulty VM size: \'%s\' is available. Using it to create rescue VM.\n', target_vm_sku)
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

    logger.info('Fetching available VM sizes for rescue VM:')
    sku_list = _call_az_command(list_sku_command).split('\n')

    if sku_list:
        return sku_list[0]

    return None

def _get_rescue_resource_tag(target_vm_name, resource_group_name):
    return 'rescue_source={rg}/{vm_name}'.format(rg=resource_group_name, vm_name=target_vm_name)
