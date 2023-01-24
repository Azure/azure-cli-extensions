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
        input_ips = input_value.split(',')
        if len(input_ips) > 8:
            raise InvalidArgumentValueError('Maximum 8 IP addresses are allowed per rule.')
        validated_ips = ''
        for ip in input_ips:
            # Use ipaddress library to validate ip network format
            ip_obj = ipaddress.ip_network(ip)
            validated_ips += str(ip_obj) + ','
        namespace.target_ip_address = validated_ips[:-1]
