# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.azclierror import ValidationError
from knack.util import CLIError
from knack.log import get_logger
from msrestazure.tools import parse_resource_id

from ._constants import MIN_GA_VERSION, GA_CONTAINERAPP_EXTENSION_NAME
from ._client_factory import (k8s_extension_client_factory, customlocation_client_factory)

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


def get_cluster_extension(cmd, cluster_extension_id=None):
    parsed_extension = parse_resource_id(cluster_extension_id)
    subscription_id = parsed_extension.get("subscription")
    cluster_rg = parsed_extension.get("resource_group")
    cluster_rp = parsed_extension.get("namespace")
    cluster_type = parsed_extension.get("type")
    cluster_name = parsed_extension.get("name")
    resource_name = parsed_extension.get("resource_name")

    return k8s_extension_client_factory(cmd.cli_ctx, subscription_id=subscription_id).get(
        resource_group_name=cluster_rg,
        cluster_rp=cluster_rp,
        cluster_resource_name=cluster_type,
        cluster_name=cluster_name,
        extension_name=resource_name)


def get_custom_location(cmd, custom_location_id):
    parsed_custom_loc = parse_resource_id(custom_location_id)
    subscription_id = parsed_custom_loc.get("subscription")
    custom_loc_name = parsed_custom_loc["name"]
    custom_loc_rg = parsed_custom_loc["resource_group"]
    custom_location = None
    try:
        custom_location = customlocation_client_factory(cmd.cli_ctx, subscription_id=subscription_id).get(resource_group_name=custom_loc_rg, resource_name=custom_loc_name)
    except:
        pass
    return custom_location
