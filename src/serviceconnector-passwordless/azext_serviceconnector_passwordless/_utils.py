# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
from knack.prompting import prompt, prompt_y_n, NoTTYException
from knack.log import get_logger
from azure.cli.core import telemetry
from azure.cli.core.azclierror import (
    AzureConnectionError,
    CLIInternalError,
)
from azure.cli.command_modules.serviceconnector._utils import (
    run_cli_cmd as run_cli_cmd_base,
    should_load_source as should_load_source_base
)
from ._resource_config import PASSWORDLESS_SOURCE_RESOURCES

logger = get_logger(__name__)

IP_ADDRESS_CHECKER = 'https://api.ipify.org'
OPEN_ALL_IP_MESSAGE = 'Do you want to enable access for all IPs to allow local environment connecting to database?'
SET_ADMIN_MESSAGE = 'Do you want to set current user as Entra admin?'


def should_load_source(source):
    if source not in PASSWORDLESS_SOURCE_RESOURCES:
        return False
    return should_load_source_base(source)


def run_cli_cmd(cmd, retry=0, interval=0, should_retry_func=None, should_return_json=True):
    try:
        if should_return_json:
            return run_cli_cmd_base(cmd + ' -o json', retry, interval, should_retry_func)
        return run_cli_cmd_base(cmd, retry, interval, should_retry_func)
    except CLIInternalError as e:
        error_code = 'Unknown'
        error_res = re.search(
            r'\(([a-zA-Z]+)\)', str(e))
        if error_res:
            error_code = error_res.group(1)
        telemetry.set_exception(
            e, "Cli-Command-Fail-" + cmd.split(" -")[0].strip() + '-' + error_code)
        raise e


# pylint: disable=broad-except, line-too-long
def get_local_ip():
    from requests import get
    try:
        return get(IP_ADDRESS_CHECKER).text
    except Exception:
        help_message = "Please enter your local IP address to allow connection to database(press enter to allow all IPs): "
        try:
            while True:
                ip = prompt(help_message)
                if not ip:
                    return ip
                try:
                    # check if the ip address is a valid ipv4 address
                    import ipaddress
                    ipaddress.IPv4Address(ip)
                    return ip
                except Exception:
                    logger.warning(
                        'The provided IP address is not a valid IPv4 address.')
        except NoTTYException as e:
            telemetry.set_exception(e, "No-TTY")
            raise CLIInternalError(
                'Unable to get local ip address. Please add firewall rule to allow local connection first.') from e


def confirm_all_ip_allow():
    try:
        if not prompt_y_n(OPEN_ALL_IP_MESSAGE):
            ex = AzureConnectionError(
                "Please confirm local environment can connect to database and try again.")
            telemetry.set_exception(ex, "Connect-Db-Fail")
            raise ex
    except NoTTYException as e:
        telemetry.set_exception(e, "No-TTY")
        raise CLIInternalError(
            'Unable to prompt for confirmation as no tty available. Use --yes.') from e


def confirm_admin_set():
    try:
        return prompt_y_n(SET_ADMIN_MESSAGE)
    except NoTTYException as e:
        telemetry.set_exception(e, "No-TTY")
        logger.warning(
            'Unable to prompt for confirmation as no tty available. Use --yes to enable the operation.')
        return False
