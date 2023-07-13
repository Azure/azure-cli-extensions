# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.azclierror import NoTTYError, ValidationError
from knack.util import CLIError
from knack.log import get_logger

from ._constants import MIN_GA_VERSION, GA_CONTAINERAPP_EXTENSION_NAME

logger = get_logger(__name__)


def is_containerapp_extension_available():
    from azure.cli.core.extension import (
        ExtensionNotInstalledException, get_extension)
    from packaging.version import parse
    try:
        ext = get_extension(GA_CONTAINERAPP_EXTENSION_NAME)
        # Check extension version
        if ext and parse(ext.version) < parse(MIN_GA_VERSION):
            return False
    except ExtensionNotInstalledException:
        return False
    return True


def _get_azext_containerapp_module(module_name):
    try:
        if not is_containerapp_extension_available():
            raise ValidationError(f"The command requires the version of {GA_CONTAINERAPP_EXTENSION_NAME} >= {MIN_GA_VERSION}. Run 'az extension add --upgrade -n {GA_CONTAINERAPP_EXTENSION_NAME}' to install extension")

        # Adding the installed extension in the path
        from azure.cli.core.extension.operations import add_extension_to_path
        add_extension_to_path(GA_CONTAINERAPP_EXTENSION_NAME)
        # Import the extension module
        from importlib import import_module
        azext_custom = import_module(module_name)
        return azext_custom
    except ImportError as ie:
        raise CLIError(ie) from ie
