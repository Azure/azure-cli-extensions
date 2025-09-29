# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os.path
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)
from azure.cli.core.util import sdk_no_wait


def aks_jwtauthenticator_add_internal(cmd, client, raw_parameters, headers, no_wait):
    resource_group_name = raw_parameters.get("resource_group_name")
    cluster_name = raw_parameters.get("cluster_name")
    jwt_authenticator_name = raw_parameters.get("name")
    config_file = raw_parameters.get("config_file")

    if not jwt_authenticator_name:
        raise RequiredArgumentMissingError(
            "Please specify --name for the JWT authenticator."
        )

    if not config_file:
        raise RequiredArgumentMissingError(
            "Please specify --config-file containing the JWT authenticator configuration."
        )

    jwt_authenticator = construct_jwt_authenticator(cmd, raw_parameters)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        cluster_name,
        jwt_authenticator_name,
        jwt_authenticator,
        headers=headers,
    )


def aks_jwtauthenticator_update_internal(cmd, client, raw_parameters, headers, no_wait):
    resource_group_name = raw_parameters.get("resource_group_name")
    cluster_name = raw_parameters.get("cluster_name")
    jwt_authenticator_name = raw_parameters.get("name")
    config_file = raw_parameters.get("config_file")

    if not jwt_authenticator_name:
        raise RequiredArgumentMissingError(
            "Please specify --name for the JWT authenticator."
        )

    if not config_file:
        raise RequiredArgumentMissingError(
            "Please specify --config-file containing the updated JWT authenticator configuration."
        )

    jwt_authenticator = construct_jwt_authenticator(cmd, raw_parameters)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        cluster_name,
        jwt_authenticator_name,
        jwt_authenticator,
        headers=headers,
    )


def construct_jwt_authenticator(cmd, raw_parameters):
    config_file = raw_parameters.get("config_file")
    if not config_file:
        raise RequiredArgumentMissingError(
            "Please specify --config-file containing the JWT authenticator configuration."
        )
    if not os.path.exists(config_file):
        raise InvalidArgumentValueError(
            f"Configuration file not found: {config_file}"
        )

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise InvalidArgumentValueError(
            f"Invalid JSON in configuration file: {str(e)}"
        )
    except Exception as e:
        raise InvalidArgumentValueError(
            f"Error reading configuration file: {str(e)}"
        )

    if not isinstance(config, dict):
        raise InvalidArgumentValueError(
            "Configuration file must contain a JSON object."
        )

    JWTAuthenticator = cmd.get_models(
        "JWTAuthenticator",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="jwt_authenticators",
    )

    JWTAuthenticatorProperties = cmd.get_models(
        "JWTAuthenticatorProperties",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="jwt_authenticators",
    )

    # Create JWT authenticator properties from config
    try:
        properties = JWTAuthenticatorProperties.from_dict(config)
    except AttributeError as e:
        raise InvalidArgumentValueError(
            f"JWT authenticator model does not support from_dict method: {str(e)}"
        )
    except TypeError as e:
        raise InvalidArgumentValueError(
            f"Invalid configuration structure for JWT authenticator: {str(e)}"
        )
    except Exception as e:
        raise InvalidArgumentValueError(
            f"Error creating JWT authenticator properties from configuration: {str(e)}"
        )

    jwt_authenticator = JWTAuthenticator(properties=properties)
    return jwt_authenticator
