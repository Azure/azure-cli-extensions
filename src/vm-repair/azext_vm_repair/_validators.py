# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger

from azure.cli.command_modules.vm.custom import get_vm, _is_linux_os

logger = get_logger(__name__)


def validate_swap_disk(cmd, namespace):

    target_vm = get_vm(cmd, namespace.resource_group_name, namespace.vm_name)
    is_linux = _is_linux_os(target_vm)

    # Prompt for empty auth params
    if is_linux and namespace.rescue_username != None:
        logger.warning("Chaging adminUsername property is not allowed for Linux VMs. Ignoring the given rescue_username parameter.")
    if not is_linux and namespace.rescue_username == None:
        _prompt_rescue_username(namespace)

    if namespace.rescue_password == None:
        _prompt_rescue_password(namespace)

    # Validate params, password validated through vm create call
    _validate_username(namespace.rescue_username, is_linux)
    _validate_rescue_vm_name(namespace.rescue_vm_name, is_linux)

def _validate_username(username, is_linux):
    pass

def _validate_rescue_vm_name(rescue_vm_name, is_linux):
    pass

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

