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

MIN_GA_VERSION = '0.3.32'
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
            prompt_msg = 'The command requires the latest version of extension containerapp. Do you want to upgrade it now?'
            prompt_ext = _prompt_y_n(cmd, prompt_msg, extension_name)
            if prompt_ext:
                return _update_containerapp_extension(cmd, extension_name)
    except ExtensionNotInstalledException:
        prompt_msg = 'The command requires the extension containerapp. Do you want to install it now?'
        prompt_ext = _prompt_y_n(cmd, prompt_msg, extension_name)
        if prompt_ext:
            return _install_containerapp_extension(cmd, extension_name)
    return prompt_ext


def _prompt_y_n(cmd, prompt_msg, ext_name):
    no_prompt_config_msg = "Run 'az config set extension.use_dynamic_install=" \
                           "yes_without_prompt' to allow installing extensions without prompt."
    try:
        yes_without_prompt = 'yes_without_prompt' == _get_extension_use_dynamic_install_config(cmd.cli_ctx)
        if yes_without_prompt:
            logger.warning('The command requires the extension %s. It will be installed first.', ext_name)
            return True

        prompt_result = prompt_y_n(prompt_msg, default='y')
        if prompt_result:
            logger.warning(no_prompt_config_msg)

        return prompt_result
    except NoTTYException:
        tty_err_msg = "The command requires the extension {}. " \
                      "Unable to prompt for extension install confirmation as no tty " \
                      "available. {}".format(ext_name, no_prompt_config_msg)
        az_error = NoTTYError(tty_err_msg)
        az_error.print_error()
        az_error.send_telemetry()
        raise NoTTYError


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


def _update_containerapp_extension(cmd, extension_name):
    from azure.cli.core.extension import ExtensionNotInstalledException
    try:
        from azure.cli.core.extension import operations
        from importlib import import_module
        m1 = import_module(GA_CONTAINERAPP_EXTENSION_MODULE)
        # import_module('azext_containerapp._clients')
        # import_module('azext_containerapp._utils')
        # import_module('azext_containerapp._client_factory')
        # import_module('azext_containerapp._constants')
        # import_module('azext_containerapp._models')

        operations.update_extension(cmd=cmd, extension_name=extension_name)
        # operations.add_extension_to_path(extension_name)

        operations.reload_extension(extension_name=extension_name)
        # operations.reload_extension(extension_name=extension_name, extension_module='azext_containerapp._models')
        # operations.reload_extension(extension_name=extension_name, extension_module='azext_containerapp._constants')
        # operations.reload_extension(extension_name=extension_name, extension_module='azext_containerapp._client_factory')
        # operations.reload_extension(extension_name=extension_name, extension_module='azext_containerapp._clients')
        # operations.reload_extension(extension_name=extension_name, extension_module='azext_containerapp._utils')
        # operations.reload_extension(extension_name=extension_name, extension_module=GA_CONTAINERAPP_EXTENSION_MODULE)
    except CLIError as err:
        logger.info(err)
    except ExtensionNotInstalledException as err:
        logger.debug(err)
        return False
    except ModuleNotFoundError as err:
        logger.debug(err)
        logger.error(
            "Error occurred attempting to load the extension module. Use --debug for more information.")
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
        raise CLIError(ie)
