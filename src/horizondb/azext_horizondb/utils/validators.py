# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.prompting import NoTTYException, prompt_pass
from knack.util import CLIError
from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.core.commands.validators import (
    get_default_location_from_resource_group, validate_tags)
from typing import Any, Dict, Iterable, Optional


def check_resource_group(resource_group_name):
    # check if rg is already null originally
    if not resource_group_name:
        return False

    # replace single and double quotes with empty string
    resource_group_name = resource_group_name.replace("'", '').replace('"', '').strip()

    # check if rg is empty after removing quotes
    if not resource_group_name:
        return False
    return True


def password_validator(ns):
    if not ns.administrator_login_password:
        try:
            ns.administrator_login_password = prompt_pass(msg='Admin Password: ')
        except NoTTYException:
            raise CLIError('Specify --administrator-login-password when running in non-interactive mode.')


def get_combined_validator(validators):
    def _final_validator_impl(cmd, namespace):
        # do additional creation validation
        if cmd.name == 'horizondb create' or cmd.name.endswith(' horizondb create'):
            password_validator(namespace)
            get_default_location_from_resource_group(cmd, namespace)

        validate_tags(namespace)

        for validator in validators:
            validator(namespace)

    return _final_validator_impl


def is_supported_vcore(processor_capabilities: Optional[Dict[str, Any]], vcore_arg: Any) -> bool:
    supported_vcores: Iterable[Any] = (processor_capabilities or {}).get("supportedVcores", [])

    try:
        processor_vcore_options = [int(v) for v in supported_vcores]
        parsed_vcore_arg = int(vcore_arg)
    except (TypeError, ValueError):
        return False

    return parsed_vcore_arg in processor_vcore_options


def validate_resource_group(resource_group_name):
    if not check_resource_group(resource_group_name):
        raise CLIError('Resource group name cannot be empty.')


# Argument Validators
def validate_replica_count(ns):
    if ns.replica_count is None:
        return
    if ns.replica_count < 1 or ns.replica_count > 16:
        raise CLIError('Replica count must be between 1 and 16, inclusive.')


def ip_address_validator(ns):
    if (ns.end_ip_address and not _validate_ranges_in_ip(ns.end_ip_address)) or \
       (ns.start_ip_address and not _validate_ranges_in_ip(ns.start_ip_address)):
        raise CLIError('Invalid IP address. Provide an IPv4 address, for example 12.12.12.12.')
    if ns.start_ip_address and ns.end_ip_address:
        _validate_start_and_end_ip_address_order(ns.start_ip_address, ns.end_ip_address)


def public_access_validator(ns):
    if ns.public_access:
        val = ns.public_access.lower()
        if not (val in ['disabled', 'enabled', 'all', 'none'] or
                (len(val.split('-')) == 1 and _validate_ip(val)) or
                (len(val.split('-')) == 2 and _validate_ip(val))):
            raise CLIError('Invalid value for --public-access. '
                           'Allowed values: \'Disabled\', \'Enabled\', \'All\', \'None\', \'<startIP>\', '
                           'or \'<startIP>-<endIP>\', where each IP ranges from 0.0.0.0 to 255.255.255.255.')
        if len(val.split('-')) == 2:
            vals = val.split('-')
            _validate_start_and_end_ip_address_order(vals[0], vals[1])


def _validate_start_and_end_ip_address_order(start_ip, end_ip):
    start_ip_elements = [int(octet) for octet in start_ip.split('.')]
    end_ip_elements = [int(octet) for octet in end_ip.split('.')]

    for idx in range(4):
        if start_ip_elements[idx] < end_ip_elements[idx]:
            break
        if start_ip_elements[idx] > end_ip_elements[idx]:
            raise ArgumentUsageError('The end IP address is smaller than the start IP address.')


def _validate_ip(ips):
    parsed_input = ips.split('-')
    if len(parsed_input) == 1:
        return _validate_ranges_in_ip(parsed_input[0])
    if len(parsed_input) == 2:
        return _validate_ranges_in_ip(parsed_input[0]) and _validate_ranges_in_ip(parsed_input[1])
    return False


def _validate_ranges_in_ip(ip):
    parsed_ip = ip.split('.')
    if len(parsed_ip) == 4 and _valid_range(parsed_ip[0]) and _valid_range(parsed_ip[1]) \
       and _valid_range(parsed_ip[2]) and _valid_range(parsed_ip[3]):
        return True
    return False


def _valid_range(addr_range):
    if addr_range.isdigit() and 0 <= int(addr_range) <= 255:
        return True
    return False
