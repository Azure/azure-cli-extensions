# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string, no-else-return, duplicate-string-formatting-argument, expression-not-assigned, too-many-locals, logging-fstring-interpolation, broad-except, pointless-statement, bare-except

from azure.cli.core.azclierror import (ValidationError,ResourceNotFoundError, CLIError)

from msrestazure.tools import parse_resource_id, is_valid_resource_id

from ._clients import ConnectedEnvCertificateClient
from azure.cli.command_modules.containerapp._client_factory import handle_raw_exception
from ._client_factory import custom_location_client_factory, k8s_extension_client_factory

from ._constants import (CONTAINER_APP_EXTENSION_TYPE,
                         CONNECTED_ENV_CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE)


def connected_env_check_cert_name_availability(cmd, resource_group_name, name, cert_name):
    name_availability_request = {}
    name_availability_request["name"] = cert_name
    name_availability_request["type"] = CONNECTED_ENV_CHECK_CERTIFICATE_NAME_AVAILABILITY_TYPE
    try:
        r = ConnectedEnvCertificateClient.check_name_availability(cmd, resource_group_name, name, name_availability_request)
    except CLIError as e:
        handle_raw_exception(e)
    return r


def get_custom_location(cmd, custom_location_id):
    parsed_custom_loc = parse_resource_id(custom_location_id)
    subscription_id = parsed_custom_loc.get("subscription")
    custom_loc_name = parsed_custom_loc.get("name")
    custom_loc_rg = parsed_custom_loc.get("resource_group")
    custom_location = None
    try:
        custom_location = custom_location_client_factory(cmd.cli_ctx, subscription_id=subscription_id).get(resource_group_name=custom_loc_rg, resource_name=custom_loc_name)
    except ResourceNotFoundError:
        pass
    return custom_location


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


def validate_custom_location(cmd, custom_location=None):
    if not is_valid_resource_id(custom_location):
        raise ValidationError('{} is not a valid Azure resource ID.'.format(custom_location))

    r = get_custom_location(cmd=cmd, custom_location_id=custom_location)
    if r is None:
        raise ResourceNotFoundError("Cannot find custom location with custom location ID {}".format(custom_location))

    # check extension type
    extension_existing = False
    for extension_id in r.cluster_extension_ids:
        extension = get_cluster_extension(cmd, extension_id)
        if extension.extension_type.lower() == CONTAINER_APP_EXTENSION_TYPE.lower():
            extension_existing = True
            break
    if not extension_existing:
        raise ValidationError('There is no Microsoft.App.Environment extension found associated with custom location {}'.format(custom_location))
    return r.location
