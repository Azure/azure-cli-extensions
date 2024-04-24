# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import re
from azure.cli.core.azclierror import (ValidationError, InvalidArgumentValueError,
                                       MutuallyExclusiveArgumentError, RequiredArgumentMissingError)
from msrestazure.tools import is_valid_resource_id
from knack.log import get_logger

from azure.cli.command_modules.containerapp._utils import is_registry_msi_system
from ._constants import ACR_IMAGE_SUFFIX, \
    CONNECTED_ENVIRONMENT_TYPE, \
    EXTENDED_LOCATION_RP, CUSTOM_LOCATION_RESOURCE_TYPE, MAXIMUM_SECRET_LENGTH, CONTAINER_APPS_RP, \
    CONNECTED_ENVIRONMENT_RESOURCE_TYPE, MANAGED_ENVIRONMENT_RESOURCE_TYPE, MANAGED_ENVIRONMENT_TYPE
from urllib.parse import urlparse

logger = get_logger(__name__)


# called directly from custom method bc otherwise it disrupts the --environment auto RID functionality
def validate_create(registry_identity, registry_pass, registry_user, registry_server, no_wait, source=None, artifact=None, repo=None, yaml=None, environment_type=None):
    if source and repo:
        raise MutuallyExclusiveArgumentError("Usage error: --source and --repo cannot be used together. Can either deploy from a local directory or a GitHub repository")
    if (source or repo) and yaml:
        raise MutuallyExclusiveArgumentError("Usage error: --source or --repo cannot be used with --yaml together. Can either deploy from a local directory or provide a yaml file")
    if (source or repo) and environment_type == CONNECTED_ENVIRONMENT_TYPE:
        raise MutuallyExclusiveArgumentError("Usage error: --source or --repo cannot be used with --environment-type connectedEnvironment together. Please use --environment-type managedEnvironment")
    if repo:
        if not registry_server:
            raise RequiredArgumentMissingError('Usage error: --registry-server is required while using --repo')
        if ACR_IMAGE_SUFFIX not in registry_server:
            raise InvalidArgumentValueError("Usage error: --registry-server: expected an ACR registry (*.azurecr.io) for --repo")
    if repo and registry_server and "azurecr.io" in registry_server:
        parsed = urlparse(registry_server)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split(".")[0]
        if registry_name and len(registry_name) > MAXIMUM_SECRET_LENGTH:
            raise ValidationError(f"--registry-server ACR name must be less than {MAXIMUM_SECRET_LENGTH} "
                                  "characters when using --repo")
    if registry_identity and (registry_pass or registry_user):
        raise MutuallyExclusiveArgumentError("Cannot provide both registry identity and username/password")
    if is_registry_msi_system(registry_identity) and no_wait:
        raise MutuallyExclusiveArgumentError("--no-wait is not supported with system registry identity")
    if registry_identity and not is_valid_resource_id(registry_identity) and not is_registry_msi_system(registry_identity):
        raise InvalidArgumentValueError("--registry-identity must be an identity resource ID or 'system'")
    if registry_identity and ACR_IMAGE_SUFFIX not in (registry_server or ""):
        raise InvalidArgumentValueError("--registry-identity: expected an ACR registry (*.azurecr.io) for --registry-server")


def validate_env_name_or_id(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id, parse_resource_id

    if not namespace.managed_env:
        return

    # Set environment type
    environment_type = None

    if namespace.__dict__.get("environment_type"):
        environment_type = namespace.environment_type

    if is_valid_resource_id(namespace.managed_env):
        env_dict = parse_resource_id(namespace.managed_env)
        resource_type = env_dict.get("resource_type")
        if resource_type:
            if CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                environment_type = CONNECTED_ENVIRONMENT_TYPE
            if MANAGED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                environment_type = MANAGED_ENVIRONMENT_TYPE

    # Validate resource id / format resource id
    if environment_type == CONNECTED_ENVIRONMENT_TYPE:
        if not is_valid_resource_id(namespace.managed_env):
            namespace.managed_env = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace=CONTAINER_APPS_RP,
                type=CONNECTED_ENVIRONMENT_RESOURCE_TYPE,
                name=namespace.managed_env
            )
    else:
        if not is_valid_resource_id(namespace.managed_env):
            namespace.managed_env = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace=CONTAINER_APPS_RP,
                type=MANAGED_ENVIRONMENT_RESOURCE_TYPE,
                name=namespace.managed_env
            )


def validate_env_name_or_id_for_up(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id, parse_resource_id

    if not namespace.environment:
        return

    # Set environment type
    environment_type = None

    if is_valid_resource_id(namespace.environment):
        env_dict = parse_resource_id(namespace.environment)
        resource_type = env_dict.get("resource_type")
        if resource_type:
            if CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                environment_type = CONNECTED_ENVIRONMENT_TYPE
            if MANAGED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                environment_type = MANAGED_ENVIRONMENT_TYPE

    if namespace.__dict__.get("custom_location") or namespace.__dict__.get("connected_cluster_id"):
        environment_type = CONNECTED_ENVIRONMENT_TYPE

    # Validate resource id / format resource id
    if environment_type == CONNECTED_ENVIRONMENT_TYPE:
        if not is_valid_resource_id(namespace.environment):
            namespace.environment = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace=CONTAINER_APPS_RP,
                type=CONNECTED_ENVIRONMENT_RESOURCE_TYPE,
                name=namespace.environment
            )
    elif environment_type == MANAGED_ENVIRONMENT_TYPE:
        if not is_valid_resource_id(namespace.environment):
            namespace.environment = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace=CONTAINER_APPS_RP,
                type=MANAGED_ENVIRONMENT_RESOURCE_TYPE,
                name=namespace.environment
            )


def validate_custom_location_name_or_id(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id

    if not namespace.custom_location or not namespace.resource_group_name:
        return

    if not is_valid_resource_id(namespace.custom_location):
        namespace.custom_location = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace=EXTENDED_LOCATION_RP,
            type=CUSTOM_LOCATION_RESOURCE_TYPE,
            name=namespace.custom_location
        )


def validate_build_env_vars(cmd, namespace):
    env_list = namespace.build_env_vars

    if not env_list:
        return

    env_pairs = {}

    for pair in env_list:
        key_val = pair.split('=', 1)
        if len(key_val) <= 1:
            raise ValidationError("Build environment variables must be in the format \"<key>=<value>\".")
        if key_val[0] in env_pairs:
            raise ValidationError(
                "Duplicate build environment variable {env} found, environment variable names must be unique.".format(
                    env=key_val[0]))
        env_pairs[key_val[0]] = key_val[1]

def validate_otlp_headers(cmd, namespace):
    headers = namespace.headers

    if not headers:
        return

    header_pairs = {}

    for pair in headers:
        key_val = pair.split('=', 1)
        if len(key_val) != 2:
            raise ValidationError("Otlp headers must be in the format \"<key>=<value>\".")
        if key_val[0] in header_pairs:
            raise ValidationError(
                "Duplicate headers {header} found, header names must be unique.".format(
                    header=key_val[0]))
        header_pairs[key_val[0]] = key_val[1]

