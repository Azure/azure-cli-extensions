# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.azclierror import NoTTYError
from azure.cli.core.extension.dynamic_install import _get_extension_use_dynamic_install_config
from knack.prompting import prompt_y_n, NoTTYException
from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)

MIN_GA_VERSION = '0.3.33'
GA_CONTAINERAPP_EXTENSION_NAME = 'containerapp'
GA_CONTAINERAPP_EXTENSION_MODULE = 'azext_containerapp.custom'


def _get_or_add_extension(cmd, extension_name):
    from azure.cli.core.extension import (
        ExtensionNotInstalledException, get_extension)
    from pkg_resources import parse_version
    prompt_ext = True
    try:
        ext = get_extension(extension_name)
        # check extension version
        if ext and parse_version(ext.version) < parse_version(MIN_GA_VERSION):
            msg = f"The command requires the latest version of extension {extension_name}. Run 'az extension add --upgrade -n {extension_name}' to upgrade extension"
            logger.Error(msg)
            return False
    except ExtensionNotInstalledException:
        prompt_msg = f"The command requires the extension {extension_name}. Do you want to install it now?"
        prompt_ext = _prompt_y_n(cmd, prompt_msg, extension_name)
        if prompt_ext:
            return _install_containerapp_extension(cmd, extension_name)
    return prompt_ext


def _prompt_y_n(cmd, prompt_msg, ext_name):
    no_prompt_config_msg = "Run 'az config set extension.use_dynamic_install=" \
                           "yes_without_prompt' to allow installing extensions without prompt."
    try:
        yes_without_prompt = _get_extension_use_dynamic_install_config(cmd.cli_ctx) == 'yes_without_prompt'
        if yes_without_prompt:
            logger.warning('The command requires the extension %s. It will be installed first.', ext_name)
            return True

        prompt_result = prompt_y_n(prompt_msg, default='y')
        if prompt_result:
            logger.warning(no_prompt_config_msg)

        return prompt_result
    except NoTTYException:
        tty_err_msg = f"The command requires the extension {ext_name}. " \
                      "Unable to prompt for extension install confirmation as no tty " \
                      "available. {no_prompt_config_msg}"
        az_error = NoTTYError(tty_err_msg)
        az_error.print_error()
        az_error.send_telemetry()
        raise NoTTYError from az_error


def _install_containerapp_extension(cmd, extension_name, upgrade=False):
    try:
        from azure.cli.core.extension import operations
        operations.add_extension(cmd=cmd, extension_name=extension_name, upgrade=upgrade)
    except Exception:  # nopa pylint: disable=broad-except
        return False
    return True


def _remove_extension(extension_name):
    try:
        from azure.cli.core.extension import operations
        operations.remove_extension(extension_name=extension_name)
    except Exception:  # nopa pylint: disable=broad-except
        return False
    return True


def _get_azext_module(extension_name, module_name):
    try:
        # Adding the installed extension in the path
        from azure.cli.core.extension.operations import add_extension_to_path
        add_extension_to_path(extension_name)
        # Import the extension module
        from importlib import import_module
        azext_custom = import_module(module_name)
        return azext_custom
    except ImportError as ie:
        raise CLIError(ie) from ie
