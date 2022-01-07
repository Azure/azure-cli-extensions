# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

from azure.cli.core.azclierror import ClientRequestError
from azure.cli.core.util import CLIError
from azure.cli.core.commands.validators import validate_tag
from azure.core.exceptions import ResourceNotFoundError
from .buildpack_binding import (DEFAULT_BUILD_SERVICE_NAME)
from ._util_enterprise import (
    is_enterprise_tier, get_client
)


def only_support_enterprise(cmd, namespace):
    if namespace.resource_group and namespace.service and not is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ClientRequestError("'{}' only supports for Enterprise tier Spring instance.".format(namespace.command))


def not_support_enterprise(cmd, namespace):
    if namespace.resource_group and namespace.service and is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ClientRequestError("'{}' doesn't support for Enterprise tier Spring instance.".format(namespace.command))

def validate_buildpack_binding_properties(namespace):
    """ Extracts multiple space-separated properties in key[=value] format """
    if isinstance(namespace.properties, list):
        properties_dict = {}
        for item in namespace.properties:
            properties_dict.update(validate_tag(item))
        namespace.properties = properties_dict


def validate_buildpack_binding_secrets(namespace):
    """ Extracts multiple space-separated secrets in key[=value] format """
    if isinstance(namespace.secrets, list):
        secrets_dict = {}
        for item in namespace.secrets:
            secrets_dict.update(validate_tag(item))
        namespace.secrets = secrets_dict


def validate_buildpack_binding_not_exist(cmd, namespace):
    client = get_client(cmd)
    try:
        binding_resource = client.buildpack_binding.get(namespace.resource_group,
                                                         namespace.service,
                                                         DEFAULT_BUILD_SERVICE_NAME,
                                                         namespace.builder_name,
                                                         namespace.name)
        if binding_resource is not None:
            raise CLIError('buildpack Binding {} in builder {} already exists '
                           'in resource group {}, service {}. You can edit it by set command.'
                           .format(namespace.name, namespace.resource_group, namespace.service, namespace.builder_name))
    except ResourceNotFoundError:
        # Excepted case
        pass

def validate_buildpack_binding_exist(cmd, namespace):
    client = get_client(cmd)
    # If not exists exception will be raised
    client.buildpack_binding.get(namespace.resource_group,
                                  namespace.service,
                                  DEFAULT_BUILD_SERVICE_NAME,
                                  namespace.builder_name,
                                  namespace.name)