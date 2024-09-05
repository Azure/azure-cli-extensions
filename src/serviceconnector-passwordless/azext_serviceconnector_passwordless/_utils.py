# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import time
from knack.prompting import prompt, prompt_y_n, NoTTYException
from knack.log import get_logger
from azure.cli.core import telemetry
from azure.cli.core.azclierror import (
    AzureConnectionError,
    CLIInternalError,
)
from azure.cli.command_modules.serviceconnector._utils import (
    should_load_source as should_load_source_base
)
from ._resource_config import PASSWORDLESS_SOURCE_RESOURCES

logger = get_logger(__name__)

IP_ADDRESS_CHECKER = 'https://api.ipify.org'
OPEN_ALL_IP_MESSAGE = 'Do you want to enable access for all IPs to allow local environment connecting to database?'
SET_ADMIN_MESSAGE = 'Do you want to set current user as Entra admin?'
ENABLE_ENTRA_AUTH_MESSAGE = 'Do you want to enable Microsoft Entra Authentication for the database server?\
 It may cause the server restart.'


def should_load_source(source):
    if source not in PASSWORDLESS_SOURCE_RESOURCES:
        return False
    return should_load_source_base(source)


def run_cli_cmd(cli_ctx, cmd, retry=0, interval=0, should_retry_func=None, should_return_json=True):
    try:
        if should_return_json:
            return run_cli_cmd_base(cli_ctx, cmd + ' -o json', retry, interval, should_retry_func)
        return run_cli_cmd_base(cli_ctx, cmd, retry, interval, should_retry_func)
    except CLIInternalError as e:
        error_code = 'Unknown'
        error_res = re.search(
            r'\(([a-zA-Z]+)\)', str(e))
        if error_res:
            error_code = error_res.group(1)
        telemetry.set_exception(
            e, "Cli-Command-Fail-" + cmd.split(" -")[0].strip() + '-' + error_code)
        raise e


def run_cli_cmd_base(cli_ctx, cmd, retry=0, interval=0, should_retry_func=None):
    '''Run a CLI command
    :param cmd: The CLI command to be executed
    :param retry: The times to re-try
    :param interval: The seconds wait before retry
    '''
    import json

    output = _in_process_execute(cli_ctx, cmd, expect_failure=False)
    if output['returncode'] != 0 or (should_retry_func and should_retry_func(output)):
        if retry:
            time.sleep(interval)
            return run_cli_cmd(cmd, retry - 1, interval)
        raise CLIInternalError('Command execution failed, command is: '
                               '{}, error message is: \n {}'.format(cmd, output['stderr']))
    stdout = output['stdout']
    try:
        return json.loads(stdout) if stdout else None
    except ValueError as e:
        logger.debug(e)
        return stdout or None


# pylint: disable=lost-exception, return-in-finally, logging-fstring-interpolation
def _in_process_execute(cli_ctx, command, expect_failure=False):
    from io import StringIO
    import shlex

    if command.startswith('az '):
        command = command[3:]

    stdout_buf = StringIO()
    logging_buf = StringIO()
    process_error = None
    try:
        exit_code = cli_ctx.invoke(shlex.split(command), out_file=stdout_buf) or 0
        output = stdout_buf.getvalue()
    except Exception as ex:  # pylint: disable=broad-except
        exit_code = 1
        output = stdout_buf.getvalue()
        process_error = ex
    except SystemExit as ex:
        # SystemExit not caught by broad exception, check for sys.exit(3)
        if ex.code == 3 and expect_failure:
            exit_code = 1
            output = stdout_buf.getvalue()
        else:
            process_error = ex
    finally:
        stdout_buf.close()
        logging_buf.close()
        # logger.debug(f'output: {output}')
        return {
            'returncode': exit_code,
            'stderr': process_error,
            'stdout': output
        }


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


def confirm_enable_entra_auth():
    try:
        if not prompt_y_n(ENABLE_ENTRA_AUTH_MESSAGE):
            ex = AzureConnectionError(
                "Please enable Microsoft Entra authentication manually and try again.")
            telemetry.set_exception(ex, "Refuse-Entra-Auth")
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


def get_object_id_of_current_user_new(cli_ctx):
    signed_in_user_info = run_cli_cmd(cli_ctx, 'az account show -o json')
    if not isinstance(signed_in_user_info, dict):
        raise CLIInternalError(
            f"Can't parse login user information {signed_in_user_info}")
    signed_in_user = signed_in_user_info.get('user')
    user_type = signed_in_user.get('type')
    if not user_type or not signed_in_user.get('name'):
        raise CLIInternalError(
            f"Can't get user type or name from signed-in user {signed_in_user}")
    try:
        if user_type == 'user':
            user_info = run_cli_cmd(cli_ctx, 'az ad signed-in-user show -o json')
            user_object_id = user_info.get('objectId') if user_info.get(
                'objectId') else user_info.get('id')
            return user_object_id
        if user_type == 'servicePrincipal':
            user_info = run_cli_cmd(
                cli_ctx,
                f'az ad sp show --id "{signed_in_user.get("name")}" -o json')
            user_object_id = user_info.get('id')
            return user_object_id
    except CLIInternalError as e:
        if 'AADSTS530003' in e.error_msg:
            logger.warning(
                'Please ask your IT department for help to join this device to Azure Active Directory.')
        raise e
