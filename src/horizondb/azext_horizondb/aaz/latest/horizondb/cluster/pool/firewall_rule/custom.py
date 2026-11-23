# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ipaddress import AddressValueError, IPv4Address

from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError

from ._create import Create
from ._update import Update

logger = get_logger(__name__)


def _address(value, option):
    try:
        return IPv4Address(value.to_serialized_data())
    except AddressValueError as exc:
        raise InvalidArgumentValueError(f'{option} must be a dotted-decimal IPv4 address.') from exc


def _validate_and_warn(properties):
    start = _address(properties.start_ip_address, '--start-ip-address')
    end = _address(properties.end_ip_address, '--end-ip-address')
    if end < start:
        raise InvalidArgumentValueError('--end-ip-address must be greater than or equal to --start-ip-address.')
    if start.is_unspecified and end.is_unspecified:
        logger.warning('Configuring firewall rule to accept connections from all Azure resources...')
    else:
        logger.warning("Configuring firewall rule to accept connections from '%s' to '%s'...", start, end)


class FirewallRuleCreate(Create):
    def pre_operations(self):
        _validate_and_warn(self.ctx.args)


class FirewallRuleUpdate(Update):
    def post_instance_update(self, instance):
        # A partial update must be checked against the endpoint retained by the GET.
        _validate_and_warn(instance.properties)
