# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

from azure.cli.core.util import CLIError
from azure.cli.core.azclierror import ClientRequestError
from azure.core.exceptions import ResourceNotFoundError
from ._util_enterprise import (
    is_enterprise_tier, get_client
)
from .vendored_sdks.appplatform.v2022_01_01_preview.models import _app_platform_management_client_enums as AppPlatformEnums
from ._validators import _parse_sku_name
from ._buildservices import DEFAULT_BUILD_SERVICE_NAME


def only_support_enterprise(cmd, namespace):
    if namespace.resource_group and namespace.service and not is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ClientRequestError("'{}' only supports for Enterprise tier Spring instance.".format(namespace.command))


def not_support_enterprise(cmd, namespace):
    if namespace.resource_group and namespace.service and is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ClientRequestError("'{}' doesn't support for Enterprise tier Spring instance.".format(namespace.command))


def validate_builder_create(cmd, namespace):
    client = get_client(cmd)
    try:
        builder = client.build_service_builder.get(namespace.resource_group,
                                                   namespace.service,
                                                   DEFAULT_BUILD_SERVICE_NAME,
                                                   namespace.name)
        if builder is not None:
            raise ClientRequestError('Builder {} already exists.'.format(namespace.name))
    except ResourceNotFoundError:
        pass


def validate_builder_update(cmd, namespace):
    client = get_client(cmd)
    try:
        client.build_service_builder.get(namespace.resource_group,
                                         namespace.service,
                                         DEFAULT_BUILD_SERVICE_NAME,
                                         namespace.name)
    except ResourceNotFoundError:
        raise ClientRequestError('Builder {} does not exist.'.format(namespace.name))


def validate_builder_resource(namespace):
    if namespace.builder_json is not None and namespace.builder_file is not None:
        raise ClientRequestError("You can only specify either --builder-json or --builder-file.")


def validate_build_pool_size(namespace):
    if _parse_sku_name(namespace.sku) != 'enterprise':
        namespace.build_pool_size = None
