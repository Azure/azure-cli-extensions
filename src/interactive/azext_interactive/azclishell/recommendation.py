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
from azure.cli.core.style import print_styled_text, Style


class RecommendType(int, Enum):
    All = 1
    Solution = 2
    Command = 3
    Scenario = 4


class RecommendThread(threading.Thread):
    def __init__(self, cli_ctx, history, on_prepared):
        super().__init__()
        self.cli_ctx = cli_ctx
        self.history = history
        self.on_prepared = on_prepared
        self.result = None

    def run(self) -> None:
        self.result = get_recommend(self.cli_ctx, self.history)
        self.on_prepared()


class Recommender:
    def __init__(self, cli_ctx, history):
        self.cli_ctx = cli_ctx
        self.history = history
        self.cur_thread = None
        self.on_recommendation_prepared = lambda: None
        self.default_recommendations = {
            'help': 'Get help message of Azure CLI',
            'init': 'Set Azure CLI global configurations interactively',
            'next': 'Recommend the possible next set of commands to take'
        }

    def feedback(self):
        """
        Send User Feedback to telemetry.
        This should only be called between command execution and recommendation update.
        """
        if self.cur_thread and not self.cur_thread.is_alive() and self.history.strings:
            latest_command = self.history.strings[-1]
            recommendations = self.cur_thread.result
            if not recommendations:
                send_feedback(-1, [latest_command], recommendations, None)
                return
            for idx, rec in enumerate(recommendations):
                if rec['type'] != RecommendType.Command:
                    continue
                if re.sub(r'^az ', '', re.sub(r'\s+', ' ', latest_command)).strip().startswith(rec['command']):
                    send_feedback(idx, [latest_command], recommendations, rec)
                    return

    def update(self):
        """Update recommendation in new thread"""
        self.cur_thread = RecommendThread(self.cli_ctx, self.history, self.on_recommendation_prepared)
        self.cur_thread.start()

    def _get_result(self, non_block=True, timeout=3.0, rec_type=RecommendType.Command):
        if not self.cur_thread:
            if non_block:
                return None
            else:
                self.update()
        if not non_block:
            self.cur_thread.join(timeout)
        if not self.cur_thread.result:
            return self.cur_thread.result
        return [rec for rec in self.cur_thread.result if rec['type'] == rec_type]

    def get_commands(self, non_block=True, timeout=3.0):
        """
        Get the latest recommended commands
        :param non_block: whether to wait for data to be prepared
        :param timeout: block timeout
        :return: recommendation or None if the result is not prepared
        """
        return self._get_result(non_block, timeout, RecommendType.Command)

    def get_scenarios(self, non_block=True, timeout=3.0):
        """
        Get the latest recommended scenarios
        :param non_block: whether to wait for data to be prepared
        :param timeout: block timeout
        :return: recommendation or None if the result is not prepared
        """
        return self._get_result(non_block, timeout, RecommendType.Scenario)

    def set_on_recommendation_prepared(self, cb):
        self.on_recommendation_prepared = cb


def get_recommend(cli_ctx, history):
    # Upload all execution commands of local record for personalized analysis
    command_history = get_command_list_from_history(history)

    processed_exception = None

    try:
        recommends = get_recommend_from_api(command_history[-5:], 1,
                                            cli_ctx.config.getint('next', 'num_limit', fallback=5),
                                            error_info=processed_exception)
    except RecommendationError:
        return []

    return [rec for rec in recommends]


def get_command_list_from_history(history):
    commands = history.strings

    def valid_command(command):
        command = command.strip()
        if command == 'az':
            return False
        elif command.startswith("az "):
            command = command[3:].strip()
        if re.match(r"^[a-z]", command):
            return True
        return False

    commands = [re.sub(r"^az ", "", command).strip() for command in commands if valid_command(command)]
    commands = [command.split(' -')[0] for command in commands]
    commands = [json.dumps({"command": command}) for command in commands]
    return commands


def get_recommend_from_api(command_list, type, top_num=5, error_info=None):  # pylint: disable=unused-argument
    """query next command from web api"""
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

    try:
        response = requests.post(url, json.dumps(payload), timeout=2)
        response.raise_for_status()
    except requests.ConnectionError as e:
        raise RecommendationError(f'Network Error: {e}') from e
    except requests.exceptions.HTTPError as e:
        raise RecommendationError(f'{e}') from e
    except requests.RequestException as e:
        raise RecommendationError(f'Request Error: {e}') from e

    recommends = []
    if 'data' in response.json():
        recommends = response.json()['data']

    return recommends


def send_feedback(option_idx, latest_commands, recommends=None, rec=None):
    feedback_data = ['1', str(option_idx)]

    trigger_commands = latest_commands[-1]
    if len(latest_commands) > 1:
        trigger_commands = latest_commands[-2] + "," + trigger_commands
    feedback_data.append(trigger_commands)
    # processed_exception
    feedback_data.append(' ')

    has_personalized_rec = False
    if recommends:
        source_list = set()
        rec_type_list = set()
        for item in recommends:
            source_list.add(str(item['source']))
            rec_type_list.add(str(item['type']))
            if 'is_personalized' in item:
                has_personalized_rec = True
        feedback_data.append(' '.join(source_list))
        feedback_data.append(' '.join(rec_type_list))
    else:
        feedback_data.extend([' ', ' '])

    if rec:
        feedback_data.append(str(rec['source']))
        feedback_data.append(str(rec['type']))
        if rec['type'] == RecommendType.Scenario:
            feedback_data.extend([rec['scenario'], ' '])
        else:
            feedback_data.append(rec['command'])
            if "arguments" in rec and rec["arguments"]:
                feedback_data.append(' '.join(rec["arguments"]))
            else:
                feedback_data.append(' ')

        if not has_personalized_rec:
            feedback_data.extend([' '])
        elif 'is_personalized' in rec:
            feedback_data.extend(['1'])
        else:
            feedback_data.extend(['0'])
    else:
        feedback_data.extend([' ', ' ', ' ', ' ', ' '])

    telemetry.start(mode='interactive')
    telemetry.set_command_details('next')
    telemetry.set_feedback("#".join(feedback_data))
    telemetry.flush()


def _show_details_for_e2e_scenario(scenario, file=None):
    print_styled_text([(Style.PRIMARY, scenario['scenario']),
                       (Style.ACTION, " contains the following commands:\n")],
                      file=file)
    nx_cmd_set = scenario["nextCommandSet"]
    exec_idx = scenario.get("executeIndex", [])
    for idx, nx_cmd in enumerate(nx_cmd_set):
        styled_command = [(Style.ACTION, ' > '), (Style.PRIMARY, "az " + nx_cmd['command'])]
        if idx not in exec_idx:
            styled_command.append((Style.WARNING, " (executed)"))
        print_styled_text(styled_command, file=file)
        if nx_cmd['reason']:
            print_styled_text([(Style.SECONDARY, '  ' + nx_cmd['reason'])], file=file)
        else:
            print()


def gen_command_in_scenario(scenario, file=None):
    exec_idx = scenario.get("executeIndex", [])
    for idx, nx_cmd in enumerate(scenario["nextCommandSet"]):
        cmd_active = idx in exec_idx
        if not cmd_active:
            continue
        print()
        command_sample = _get_command_sample(nx_cmd)
        print_styled_text([(Style.ACTION, "Running: ")] + command_sample,
                          file=file)
        yield nx_cmd, ''.join([part[1] for part in command_sample])


def _get_command_sample(command):
    """Try getting example from command. Or load the example from `--help` if not found."""
    if "example" in command and command["example"]:
        command_sample, _ = _format_command_sample(command["example"].replace(" $", " "))
        return command_sample

    from knack import help_files
    parameter = []
    if "arguments" in command and command["arguments"]:
        parameter = command["arguments"]
        sorted_param = sorted(parameter)
        cmd_help = help_files._load_help_file(command['command'])   # pylint: disable=protected-access
        if cmd_help and 'examples' in cmd_help and cmd_help['examples']:
            for cmd_example in cmd_help['examples']:
                command_sample, example_arguments = _format_command_sample(cmd_example['text'])
                if sorted(example_arguments) == sorted_param:
                    return command_sample

    command = command["command"] if command["command"].startswith("az ") else "az " + command["command"]
    command_sample = f"{command} {' '.join(parameter) if parameter else ''}"
    return [(Style.PRIMARY, command_sample)]


def _format_command_sample(command_sample):
    """
    Format command sample in the style of `az xxx --name <appServicePlan>`.
    Also return the arguments used in the sample.
    """
    if not command_sample:
        return [], []

    cmd_items = command_sample.split()
    arguments_start = False
    example_arguments = []
    command_item = []
    argument_values = {}
    values = []
    for item in cmd_items:
        if item.startswith('-'):
            arguments_start = True
            if values and example_arguments:
                argument_values[example_arguments[-1]] = values
                values = []
            example_arguments.append(item)
        elif not arguments_start:
            command_item.append(item)
        else:
            values.append(item)
    if values and example_arguments:
        argument_values[example_arguments[-1]] = values

    formatted_example = [(Style.PRIMARY, ' '.join(command_item))]
    for argument in example_arguments:
        formatted_example.append((Style.PRIMARY, " " + argument))
        if argument in argument_values and argument_values[argument]:
            argument_value = ' '.join(argument_values[argument])
            if not (argument_value.startswith('<') and argument_value.endswith('>')):
                argument_value = '<' + argument_value + '>'
            formatted_example.append((Style.WARNING, ' ' + argument_value))

    return formatted_example, example_arguments
