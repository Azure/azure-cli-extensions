# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from enum import Enum
import threading
import json
from ._azclierror import ChatgptGenrateError
from .recommendation import RecommendType


class ChatgptThread(threading.Thread):
    def __init__(self, cli_ctx, user_msg, search_path, executing_command, on_prepared_callback, history_msg=None):
        super().__init__()
        self.cli_ctx = cli_ctx
        self.user_msg = user_msg
        self.history_msg = history_msg
        self.on_prepared_callback = on_prepared_callback
        # maintain a copy of the command history to insert commands executed in the searched scenario
        self.command_history = search_path.get_cmd_history(25)
        if executing_command:
            self.command_history.append(executing_command)
        self.processed_exception = search_path.get_result_summary() if not executing_command else None
        self.result = []
        self.api_version = None

    def run(self) -> None:
        try:
            result, self.api_version = generate_script(user_msg=self.user_msg, history_msg=self.history_msg)
            self.result.append(
                {"content": transform_script_to_scenario(result["content"]), "history_msg": result["history_msg"],
                 "api_version": self.api_version, "type": RecommendType.Chatgpt})
        except ChatgptGenrateError:
            self.result = "Connection Error. Please check your network connection."


def generate_script(user_msg: str, history_msg: list):
    """Generate CLI Scripts with ChatGPT model"""
    import requests
    url = "https://cli-recommendation.azurewebsites.net/api/chatgptservice"
    payload = {
        "user_msg": user_msg,
        "history_msg": history_msg
    }
    try:
        response = requests.post(url, json.dumps(payload))
        response.raise_for_status()
    except requests.ConnectionError as e:
        raise ChatgptGenrateError(f'Network Error: {e}') from e
    except requests.exceptions.HTTPError as e:
        raise ChatgptGenrateError(f'{e}') from e
    except requests.RequestException as e:
        raise ChatgptGenrateError(f'Request Error: {e}') from e

    result = None
    if 'data' in response.json():
        # result.content: the generated script
        # result.history_msg: the history of the conversations
        result = response.json()['data']
    api_version = None
    if 'api_version' in response.json():
        api_version = response.json()['api_version']
    return result, api_version


def transform_script_to_scenario(script):
    """Transform the generated script to a scenario"""
    scenario = {'scenario': script['Description'], 'nextCommandSet': script['CommandSet'], 'source': 5, 'type': 6,
                'executeIndex': range(len(script['CommandSet'])), 'score': 1, 'reason': script['Reason'],
                'description': script['Description']}
    return scenario
