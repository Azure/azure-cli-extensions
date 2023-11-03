# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.azclierror import RequiredArgumentMissingError


def validate_network_rule(namespace):
    if not namespace.public_network and not namespace.connection_name:
        raise RequiredArgumentMissingError('Either public network (--public-network) or private endpoint connections (--connection-name) should be set.')
