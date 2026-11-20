# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ipaddress import AddressValueError, IPv4Address

from azure.cli.core.azclierror import InvalidArgumentValueError

from ._create import Create
from ._update import Update


def _address(value, option):
    try:
        return IPv4Address(value.to_serialized_data())
    except AddressValueError as exc:
        raise InvalidArgumentValueError(f'{option} must be a dotted-decimal IPv4 address.') from exc


def _validate_range(properties):
    start = _address(properties.start_ip_address, '--start-ip-address')
    end = _address(properties.end_ip_address, '--end-ip-address')
    if end < start:
        raise InvalidArgumentValueError('--end-ip-address must be greater than or equal to --start-ip-address.')


class FirewallRuleCreate(Create):
    def pre_operations(self):
        _validate_range(self.ctx.args)


class FirewallRuleUpdate(Update):
    def post_instance_update(self, instance):
        # A partial update must be checked against the endpoint retained by the GET.
        _validate_range(instance.properties)
