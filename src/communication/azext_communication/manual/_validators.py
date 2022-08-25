# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def get_config_value(cmd, section, key, default):
    return cmd.cli_ctx.config.get(section, key, default)


def validate_client_parameters(cmd, namespace):
    """ Retrieves communication connection parameters from environment variables
    and parses out connection string into account name and key """
    n = namespace

    if not n.connection_string:
        n.connection_string = get_config_value(cmd, 'communication', 'connection_string', None)


def validate_endpoint(cmd, namespace):
    """ Retrieves communication connection parameters from environment variables """
    n = namespace

    if not n.endpoint:
        n.endpoint = get_config_value(cmd, 'communication', 'endpoint', None)


def validate_access_token(cmd, namespace):
    """ Retrieves communication connection parameters from environment variables """
    n = namespace

    if not n.access_token:
        n.access_token = get_config_value(cmd, 'communication', 'access_token', None)
