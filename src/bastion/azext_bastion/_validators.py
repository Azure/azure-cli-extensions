# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ipaddress
from azure.cli.core.azclierror import InvalidArgumentValueError


def validate_ip_address(namespace):
    if namespace.target_ip_address is not None:
        _validate_ip_address_format(namespace)


def _validate_ip_address_format(namespace):
    if namespace.target_ip_address is not None:
        input_value = namespace.target_ip_address
        if ' ' in input_value:
            raise InvalidArgumentValueError("Spaces not allowed: '{}' ".format(input_value))
        try:
            ipaddress.ip_address(input_value)
        except ValueError as e:
            raise InvalidArgumentValueError("""IP address provided is invalid.
            Please verify if there are any spaces or other invalid characters.""") from e
        namespace.target_ip_address = input_value
