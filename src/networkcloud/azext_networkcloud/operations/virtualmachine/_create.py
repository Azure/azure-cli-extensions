# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=wildcard-import,unused-wildcard-import,too-many-nested-blocks
# pylint: disable=protected-access, too-few-public-methods,line-too-long
# flake8: noqa

"""
Provides VirtualMachineCreate customization
"""

import os

from azure.cli.core import keys
from azure.cli.core.aaz import *
from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError

from ...aaz.latest.networkcloud.virtualmachine import \
    Create as _VirtualMachineCreate

logger = get_logger(__name__)

class VirtualMachineCreate(_VirtualMachineCreate):
    '''
    This custom code inherits from generate virtual machine functions. It is
    integrated into the generated code via:
    cli-ext/v20221212preview/ext/src/networkcloud/azext_networkcloud/commands.py
    '''

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)

        # Build VM Authentication args
        args_schema.generate_ssh_keys = AAZBoolArg(
            options=["--generate-ssh-keys"],
            arg_group="Authentication",
            help="Generate SSH public and private key files if missing. The keys will " +
            "be stored under '~/.ssh'."
        )

        args_schema.ssh_dest_key_path = AAZListArg(
            options=["--ssh-dest-key-path"],
            arg_group="Authentication",
            help="The list of space-separated paths to ssh public keys. A file path can be " +
            "provided or a directory. If a directory is provided will attempt to load all the " +
            "public keys (.pub) found."
        )
        args_schema.ssh_dest_key_path.Element = AAZStrArg()

        args_schema.ssh_key_values = AAZListArg(
            options=["--ssh-key-values"],
            arg_group="Authentication",
            help="The list of space-separated SSH public keys."
        )
        args_schema.ssh_key_values.Element = AAZStrArg()

        # deregister the VM cli arguments which users should not interact with
        args_schema.ssh_public_keys._registered = False
        args_schema.cloud_services_network_attachment.ip_allocation_method._required = False
        args_schema.cloud_services_network_attachment.ip_allocation_method._registered = False

        return args_schema

    @register_callback
    def pre_operations(self):
        args = self.ctx.args

        # Dynamic is the default allocation method for the cloud services network attachment
        args.cloud_services_network_attachment.ip_allocation_method = "Dynamic"

        ssh_keys = []
        if bool(args.generate_ssh_keys):
            ssh_keys += generate_ssh_keys()
        if list(args.ssh_dest_key_path):
            ssh_keys += get_ssh_keys_from_path(list(args.ssh_dest_key_path))
        if list(args.ssh_key_values):
            ssh_keys += add_ssh_key_action(list(args.ssh_key_values))
        if len(ssh_keys) == 0:
            logger.warning('No keys are selected for insertion into the vm. The image will need to have keys or credentials setup in order to access.')
        args.ssh_public_keys = ssh_keys

        return args


def generate_ssh_keys():
    ''' generates ssh keys in user .ssh folder '''

    key_name = "id_rsa"
    private_key_path = os.path.join(os.path.expanduser('~'), '.ssh', key_name)
    public_key_path = os.path.join(
        os.path.expanduser('~'), '.ssh', f"{key_name}.pub")
    logger.warning(f"Attempted to find or generate SSH key files {key_name} and {key_name}.pub under ~/.ssh to allow SSH access "
          "to the vm. If using machines without permanent storage, back up your keys to a safe location.")
    return [{'keyData': keys.generate_ssh_keys(private_key_path, public_key_path)}]


def get_ssh_keys_from_path(values):
    ''' get ssh keys from the provided path '''

    key_list = []
    for path in values:
        # Casting is necessary to get away from the custom type AAZSimpleType wrapping the string we want
        path = str(path)
        if os.path.isdir(path):
            content = ""
            for key in os.listdir(path):
                if key.endswith(".pub"):
                    with open(os.path.join(path, key,), 'r', encoding="utf-8") as k:
                        content = k.read()
                    try:
                        if keys.is_valid_ssh_rsa_public_key(content):
                            key_list.append({'keyData': content})
                    except Exception as exception:
                        raise InvalidArgumentValueError(
                            f'Unsupported Key {key} is provided.\nContent:\n{content}.') from exception
            if len(key_list) == 0:
                raise InvalidArgumentValueError(
                    f'No public keys found in the path: {path}')
        elif os.path.isfile(path):
            with open(path, 'r', encoding="utf-8") as k:
                content = k.read()
            try:
                if keys.is_valid_ssh_rsa_public_key(content):
                    key_list.append({'keyData': content})
            except Exception as excep:
                raise InvalidArgumentValueError(
                    f'Unsupported Key {path} is provided.\nContent:\n{content}') from excep
        else:
            raise InvalidArgumentValueError(f'An invalid directory or key was provided: {path}')
    return key_list


def add_ssh_key_action(values):
    '''validate and add ssh key to the list '''

    key_data = []
    for key in values:
        # Casting is necessary to get away from the custom type AAZSimpleType wrapping the string we want
        key = str(key)
        try:
            if keys.is_valid_ssh_rsa_public_key(key):
                key_data.append({'keyData': key})
        except Exception as excep:
            raise CLIError(
                f'Unsupported Key is provided.\nContent:\n{key}') from excep
    return key_data
