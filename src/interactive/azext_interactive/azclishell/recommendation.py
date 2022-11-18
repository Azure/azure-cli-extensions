# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import re
from enum import Enum
import hashlib
import json
import threading

from azure.cli.core.azclierror import RecommendationError
from azure.cli.core import telemetry
from azure.cli.core import __version__ as version

from enum import Enum


class RecommendType(int, Enum):
    All = 1
    Solution = 2
    Command = 3
    Scenario = 4


class RecommendThread(threading.Thread):
    def __init__(self, cli_ctx, history):
        super().__init__()
        self.cli_ctx = cli_ctx
        self.history = history
        self.result = None

    def run(self) -> None:
        self.result = get_recommend(self.cli_ctx, self.history)


class Recommender:
    def __init__(self, cli_ctx, history):
        self.cli_ctx = cli_ctx
        self.history = history
        self.cur_thread = None

    def update(self):
        """Update recommendation in new thread"""
        self.cur_thread = RecommendThread(self.cli_ctx, self.history)
        self.cur_thread.start()

    def get_result(self, non_block=True, timeout=3.0):
        """
        Get the latest recommendation result
        :param non_block: whether to wait for data to be prepared
        :param timeout: block timeout
        :return: recommendation or None if the result is not prepared
        """
        if not self.cur_thread:
            if non_block:
                return None
            else:
                self.update()
        if non_block:
            return self.cur_thread.result
        else:
            self.cur_thread.join(timeout)
            return self.cur_thread.result


def get_recommend(cli_ctx, history):
    # Upload all execution commands of local record for personalized analysis
    command_history = get_command_list_from_history(history)

    processed_exception = None

    recommends = get_recommend_from_api(command_history, 1,
                                        cli_ctx.config.getint('next', 'num_limit', fallback=5),
                                        error_info=processed_exception)

    return [rec for rec in recommends if rec['type'] == RecommendType.Command]


def get_command_list_from_history(history):
    commands = history.strings

    def valid_command(command):
        command = command.strip()
        if command == 'az':
            return False
        elif command.startswith("az "):
            command = command[3:].strip()
        if re.match(r"^\w", command):
            return True
        return False

    commands = [re.sub(r"^az ", "", command).strip() for command in commands if valid_command(command)]
    commands = [json.dumps({"command": command}) for command in commands]
    return commands


def get_latest_command(command_history):
    if not command_history:
        return ''

    command_list_data = reversed(command_history)
    for command_item in command_list_data:
        cmd = json.loads(command_item)
        if cmd['command'] == 'next':
            continue
        return cmd['command']


def get_recommend_from_api(command_list, type, top_num=5, error_info=None):  # pylint: disable=unused-argument
    '''query next command from web api'''
    import requests
    url = "https://cli-recommendation.azurewebsites.net/api/RecommendationService"

    user_id = telemetry._get_user_azure_id()  # pylint: disable=protected-access
    hashed_user_id = hashlib.sha256(user_id.encode('utf-8')).hexdigest()
    payload = {
        "command_list": json.dumps(command_list),
        "type": type,
        "top_num": top_num,
        'error_info': error_info,
        'cli_version': version,
        'user_id': hashed_user_id
    }

    correlation_id = telemetry._session.correlation_id
    subscription_id = telemetry._get_azure_subscription_id()
    if telemetry.is_telemetry_enabled():
        if correlation_id:
            payload['correlation_id'] = correlation_id
        if subscription_id:
            payload['subscription_id'] = subscription_id

    response = requests.post(url, json.dumps(payload))
    if response.status_code != 200:
        raise RecommendationError(
            "Failed to connect to '{}' with status code '{}' and reason '{}'".format(
                url, response.status_code, response.reason))

    recommends = []
    if 'data' in response.json():
        recommends = response.json()['data']

    return recommends
