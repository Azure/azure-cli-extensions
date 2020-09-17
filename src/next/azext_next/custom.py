# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from knack.util import CLIError


def _get_api_url():
    return "https://cli-recommendation.azurewebsites.net/api/RecommendationService"


def _get_last_cmd(cmd):
    '''Get last executed command from local log files'''
    import os
    history_file_name = os.path.join(cmd.cli_ctx.config.config_dir, 'recommendation', 'cmd_history.log')
    with open(history_file_name, "r") as f:
        lines = f.read().splitlines()
        lines = [x for x in lines if x != 'next']
        return lines[-1]
    return ''


def _get_last_exception(cmd):
    '''Get last executed command from local log files'''
    import os
    history_file_name = os.path.join(cmd.cli_ctx.config.config_dir, 'recommendation', 'exception_history.log')
    if not os.path.exists(history_file_name):
        return ''
    with open(history_file_name, "r") as f:
        lines = f.read().splitlines()
        return lines[-1].replace('Message: ', '')
    return ''


def _process_exception(exception_str):
    '''Extract more information from the exception string'''
    return exception_str


def _handle_error_no_exception_found():
    '''You choose to solve the previous problems but no exception found'''
    from azure.cli.core.azclierror import AzCLIError
    from azure.cli.core.azclierror import AzCLIErrorType
    error_msg = 'The error information is missing, please try the original command again.'
    recommendation = 'You can set the recommendation type to 1 to get all available recommendations.'
    az_error = AzCLIError(AzCLIErrorType.ClientError, error_msg)
    az_error.set_recommendation(recommendation)
    az_error.print_error()

def _update_last_cmd(cmd):
    import os
    history_file_name = os.path.join(cmd.cli_ctx.config.config_dir, 'recommendation', 'cmd_history.log')
    with open(history_file_name, "a") as f:
        f.write("{}\n".format(cmd))


def _get_recommend_from_api(last_cmd, type, top_num=5, error_info=None):  # pylint: disable=unused-argument
    '''query next command from web api'''
    import requests
    url = _get_api_url()
    payload = {
        "command": last_cmd,
        "type": type,
        "top_num": top_num,
        'error_info': error_info
    }
    response = requests.post(url, json.dumps(payload))
    if response.status_code != 200:
        raise CLIError("Failed to connect to '{}' with status code '{}' and reason '{}'".format(
            url, response.status_code, response.reason))
    recommends = response.json()['data']

    return recommends


def _read_int(msg, default_value=0):
    ret = input(msg)
    if ret == '' or not ret.isnumeric():
        ret = default_value
    else:
        ret = int(ret)
    return ret


def _give_recommends(recommends):
    idx = 0
    for rec in recommends:
        if 'reason' in rec:
            reason = rec['reason']
        else:
            reason = " people use this command in next step."
        idx += 1
        print("{}. az {} {}".format(idx, rec['command'], ' '.join(rec['arguments'])))
        if rec['ratio']:
               reason = "{:.1f}% {}".format(rec['ratio'] * 100, reason)
        print("Recommended reason: {}".format(reason))


def handle_next(cmd):
    msg = '''
Please select the type of recommendation you need:
1. all: It will intelligently analyze the types of recommendation you need, and may recommend multiple types of command to you
2. solution: Only the solutions to problems when errors occur are recommend
3. command: Only the commands with high correlation with previously executed commands are recommend
4. resource: Only the resources related to previously created resources are recommended
5. senario: Only the E2E scenarios related to current usage scenarios are recommended
'''
    print(msg)
    option = _read_int("What kind of recommendation do you want? (RETURN is to set all): ", 1)
    last_cmd = _get_last_cmd(cmd)
    last_exception = _get_last_exception(cmd)
    processed_exception = _process_exception(last_exception)
    if option == 2 and not processed_exception:
        _handle_error_no_exception_found()
        return None

    recommends = _get_recommend_from_api(last_cmd, option, error_info=processed_exception)
    if not recommends:
        raise CLIError("Failed to get recommend for '{}'.".format(last_cmd))
    print()
    _give_recommends(recommends)
    print()
    if len(recommends) > 1:
        option = _read_int("Which one is helpful to you? (If none, please input 0) :")
    else:
        option = input("Does it helpful to you? (y/n): ")
        if option in ["y", "yes", "Y", "Yes", "YES"]:
            option = 1
        else:
            option = 0
    if option == 0:
        # we can send feedback here
        return "recommend abort"

    option = option - 1
    nx_cmd = recommends[option]["command"]
    nx_param = recommends[option]["arguments"]
    print("Run: az {} {}".format(nx_cmd, ' '.join(nx_param)))
    print()
    doit = input("Do you want to run it now? (y/n): ")
    if doit not in ["y", "yes", "Y", "Yes", "YES"]:
        ret = {"result": "Thank you for your feedback"}
        return ret

    args = []
    args.extend(nx_cmd.split())
    for param in nx_param:
        value = input("Please input {}: ".format(param))
        args.append(param)
        if value:
            args.append(value)

    cmd.cli_ctx.invoke(args)
    return None
