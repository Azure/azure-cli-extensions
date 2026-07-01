# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=raise-missing-from

from requests import get
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_y_n
from knack.util import CLIError
from azure.cli.core.azclierror import InvalidArgumentValueError
from .validators import _validate_ranges_in_ip

logger = get_logger(__name__)

# The reserved, service-seeded default pool. HorizonDB firewall rules are pool-scoped
# (.../clusters/{cluster}/pools/{pool}/firewallRules/{name}); Public Preview clusters use a
# single default pool named "DefaultPool".
DEFAULT_POOL_NAME = 'DefaultPool'

# Service used to detect the caller's outbound public IP address.
IP_ADDRESS_CHECKER = 'https://api.ipify.org'


def parse_public_access_input(public_access):
    if public_access is not None:
        parsed_input = public_access.split('-')
        if len(parsed_input) == 1:
            return parsed_input[0], parsed_input[0]
        if len(parsed_input) == 2:
            return parsed_input[0], parsed_input[1]
        raise InvalidArgumentValueError(
            "incorrect usage: --public-access. Acceptable values are 'All', 'None', '<startIP>' and "
            "'<startIP>-<destinationIP>' where startIP and destinationIP range from 0.0.0.0 to "
            "255.255.255.255")
    return None, None


def _get_user_confirmation(message, yes=False):
    if yes:
        return True
    try:
        return bool(prompt_y_n(message))
    except NoTTYException:
        raise CLIError('Unable to prompt for confirmation as no tty available. Use --yes.')


def _resolve_client_ip_range(yes):
    try:
        response = get(IP_ADDRESS_CHECKER, timeout=5)
        response.raise_for_status()
        ip_address = response.text.strip()
        if not _validate_ranges_in_ip(ip_address):
            raise ValueError('The detection service returned an invalid IPv4 address.')
    except Exception as ex:
        raise CLIError('Unable to detect your current IP address. Please provide a valid IP address or '
                       'range for the --public-access parameter, or set --public-access Disabled. '
                       'Error: {}'.format(ex))

    logger.warning('Detected current client IP : %s', ip_address)
    if _get_user_confirmation('Do you want to enable access to client {0}'.format(ip_address), yes=yes):
        return ip_address, ip_address
    if _get_user_confirmation('Do you want to enable access for all IPs', yes=yes):
        return '0.0.0.0', '255.255.255.255'
    return -1, -1


def resolve_public_access_range(public_access, yes):
    """Map a --public-access value to a (start_ip, end_ip) pair.

    Returns (-1, -1) when no firewall rule should be created. ``Enabled`` triggers client-IP
    auto-detection because HorizonDB's ``publicNetworkAccess`` flag is service-computed (read-only),
    so a firewall rule is the only way to open public access.
    """
    val = str(public_access).lower()
    if val == 'enabled':
        return _resolve_client_ip_range(yes)
    if val == 'all':
        return '0.0.0.0', '255.255.255.255'
    if val in ['none', 'disabled']:
        return -1, -1
    return parse_public_access_input(public_access)
