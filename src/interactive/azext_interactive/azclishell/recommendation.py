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
from prompt_toolkit.history import FileHistory
from .scenario_search import SearchThread


class RecommendType(int, Enum):
    All = 1
    Solution = 2
    Command = 3
    Scenario = 4
    Search = 5
    Chatgpt = 6


class RecommendThread(threading.Thread):
    """ Worker Thread to fetch recommendation online based on user's context """

    def __init__(self, cli_ctx, recommendation_path, executing_command, on_prepared_callback):
        super().__init__()
        self.cli_ctx = cli_ctx
        self.on_prepared_callback = on_prepared_callback
        # The latest 25 commands are extracted for personalized analysis
        self.command_history = recommendation_path.get_cmd_history(25)
        if executing_command:
            self.command_history.append(executing_command)
        self.processed_exception = recommendation_path.get_result_summary() if not executing_command else None
        self.result = None
        self.api_version = None

    def run(self) -> None:
        try:
            self.result, self.api_version = get_recommend_from_api([json.dumps(cmd) for cmd in self.command_history],
                                                                   RecommendType.All,
                                                                   self.cli_ctx.config.getint('next', 'num_limit',
                                                                                              fallback=5),
                                                                   error_info=self.processed_exception)
        except RecommendationError:
            self.result = []
        self.on_prepared_callback()


class Recommender:
    def __init__(self, cli_ctx, filename):
        self.cli_ctx = cli_ctx
        self.recommendation_path = RecommendPath(filename)
        self.cur_thread = None
        self.on_prepared_callback = lambda: None
        self.default_recommendations = {
            'help': 'Get help message of Azure CLI',
            'init': 'Set Azure CLI global configurations interactively',
            'next': 'Recommend the possible next set of commands to take',
            'scenario guide': 'Search for a scenario using keywords',
        }
        self.executing_command = None

    @property
    def enabled(self):
        """Whether recommender is enabled in global config"""
        return self.cli_ctx.config.getboolean("interactive", "enable_recommender", fallback=True)

    def feedback_command(self, command):
        """Send user's command choice in recommendations to telemetry."""
        if self.cur_thread and not self.cur_thread.is_alive():
            recommendations = self.cur_thread.result
            api_version = self.cur_thread.api_version
            trigger_commands = [cmd['command'] for cmd in self.cur_thread.command_history[-2:]]
            processed_exception = self.cur_thread.processed_exception
            # reformat the user input
            # e.g. `az webapp   create -h` => `webapp create -h`
            command = re.sub(r'^az ', '', re.sub(r'\s+', ' ', command)).strip()
            if not recommendations:
                send_feedback("-1", trigger_commands, processed_exception, recommendations, accepted_recommend=None,
                              api_version=api_version)
            elif not command:
                send_feedback("0", trigger_commands, processed_exception, recommendations, accepted_recommend=None,
                              api_version=api_version)
            # idx: index of the recommendation in the recommendation list, number from 0
            for idx, recommendation in enumerate(recommendations):
                if recommendation['type'] != RecommendType.Command:
                    continue
                # check if the user input matches recommendation
                if command.startswith(recommendation['command']):
                    send_feedback(f'a{idx + 1}', trigger_commands, processed_exception, recommendations,
                                  accepted_recommend=recommendation, api_version=api_version)
                    return

    def feedback_scenario(self, scenario_idx, scenario=None):
        """Send user's scenario choice in recommendations to telemetry.

        :param scenario_idx: idx of the scenario in scenario recommendations list(number from 1)
        :param scenario: selected scenario item
        """
        if self.cur_thread and not self.cur_thread.is_alive():
            recommendations = self.cur_thread.result
            api_version = self.cur_thread.api_version
            trigger_commands = [cmd['command'] for cmd in self.cur_thread.command_history[-2:]]
            processed_exception = self.cur_thread.processed_exception
            if not recommendations:
                send_feedback("-1", trigger_commands, processed_exception, recommendations, accepted_recommend=None,
                              api_version=api_version)
            elif not scenario:
                send_feedback("0", trigger_commands, processed_exception, recommendations, accepted_recommend=None,
                              api_version=api_version)
            else:
                send_feedback(f'b{scenario_idx}', trigger_commands, processed_exception, recommendations,
                              accepted_recommend=scenario, api_version=api_version)

    def feedback_search(self, search_idx, keywords, scenario=None):
        """Send user's scenario choice in scenario search to telemetry.

        :param search_idx: idx of the scenario in scenario search list(number from 1)
        :param keywords: search keywords
        """
        if self.cur_thread and not self.cur_thread.is_alive():
            recommendations = self.cur_thread.result
            api_version = self.cur_thread.api_version
            search_keywords = keywords.split(' ')
            processed_exception = self.cur_thread.processed_exception
            if not recommendations:
                send_feedback("-1", search_keywords, processed_exception, recommendations, accepted_recommend=None,
                              api_version=api_version)
            elif not scenario:
                send_feedback("0", search_keywords, processed_exception, recommendations, accepted_recommend=None,
                              api_version=api_version)
            else:
                send_feedback(f'c{search_idx}', search_keywords, processed_exception, recommendations,
                              accepted_recommend=scenario, api_version=api_version, request_type=5)

    def update_executing(self, cmd, feedback=True):
        """Update executing command info, and prefetch the recommendation result as if the execution is successful

        :param cmd: The command that would be executed soon
        :param feedback: whether send feedback to telemetry using this command as actual execution vs
        previous recommendation
        """
        if not self.enabled:
            return
        # e.g. `az  webapp create --name xxx -g xxxx` => `webapp create`
        command = re.sub('^az *', '', cmd).split('-', 1)[0].strip()
        param = sorted([p for p in cmd.split() if p.startswith('-')])
        if feedback:
            self.feedback_command(command)
        self.executing_command = {'command': command, 'arguments': param}
        self._update()

    def update_exec_result(self, exit_code, result_summary=''):
        """Update execution result of executing_command set previously, fetch recommendation result if execution fails

        :param exit_code: exit code of previous executing command
        :param result_summary: Result Summary of previous executing command
        """
        if not self.enabled or not self.executing_command:
            return
        self.recommendation_path.append_result(self.executing_command['command'], self.executing_command['arguments'],
                                               exit_code, result_summary)
        self.executing_command = None
        # If the execution of the last command fails, get the recommendation result again
        if exit_code != 0:
            self._update()

    def _update(self):
        """Update recommendation result in new thread"""
        self.cur_thread = RecommendThread(self.cli_ctx, self.recommendation_path, self.executing_command,
                                          self.on_prepared_callback)
        self.cur_thread.start()

    def _get_result(self, recommendation_type=RecommendType.Command):
        if not self.cur_thread:
            # This `None` represents that the recommender is initialized but not updated
            return None
        if not self.cur_thread.result:
            # This `None` represents the request is running and recommendation is not ready
            return None
        return [recommendation for recommendation in self.cur_thread.result if
                recommendation['type'] == recommendation_type]

    def get_commands(self):
        """
        Get the latest recommended commands
        :return: recommendation or None if the result is not prepared
        """
        # The `[]` represents no recommendation fetched from recommendation service
        return self._get_result(RecommendType.Command) if self.enabled else []

    def get_default_recommendations(self):
        return self.default_recommendations if self.enabled else []

    def get_scenarios(self):
        """
        Get the latest recommended scenarios
        :return: recommendation or None if the result is not prepared
        """
        return self._get_result(RecommendType.Scenario) if self.enabled else []

    def set_on_prepared_callback(self, cb):
        self.on_prepared_callback = cb


class RecommendPath:
    """ History recording the commands that affect recommendations """

    def __init__(self, filename):
        self.history = FileHistory(filename)
        self.commands = [json.loads(line) for line in self.history.strings[-30:]]
        self.last_result_summary = ''

    def append_result(self, command, param, exit_code, result_summary=''):
        if not command:
            return
        execution_info = {
            'command': command,
            'arguments': param,
            'exit_code': exit_code,
        }
        self.last_result_summary = result_summary if exit_code != 0 else ''
        self.commands.append(execution_info)
        self.history.append(json.dumps(execution_info))

    def get_result_summary(self):
        """
        Get Result Summary of last appended command
        :return: last result summary
        """
        return self.last_result_summary

    def get_cmd_history(self, top_num):
        return self.commands[-top_num:]


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

    api_version = None
    if 'api_version' in response.json():
        api_version = response.json()['api_version']
    return recommends, api_version


def send_feedback(option_idx, latest_commands, processed_exception=None, recommends=None, accepted_recommend=None,
                  api_version=None, request_type=RecommendType.All):
    # initialize feedback data
    # If you want to add a new property to the feedback, please initialize it here in advance and place it with 'None' to prevent parameter loss due to parsing errors.
    feedback_data = {"request_type": None, "option": None, "trigger_commands": None, "error_info": None,
                     "recommendations_list": None, "recommendations_source_list": None,
                     "recommendations_type_list": None, "accepted_recommend_source": None,
                     "accepted_recommend_type": None, "accepted_recommend": None, "is_personalized": None}

    # request_type is the type of recommendation mode, 1 means recommend all tyes of recommendations of command, scenario and solution
    feedback_data['request_type'] = request_type
    # option is the index of the recommended command that user chooses.
    # 'a' means commands while 'b' means scenarios, such as 'a1'
    feedback_data['option'] = str(option_idx)

    if request_type == RecommendType.Search:
        # trigger_commands is the keywords that used to search for scenarios
        trigger_commands = latest_commands
    else:
        # trigger_commands is the commands that trigger the recommendation, can be multiple, max is 2 commands
        if len(latest_commands) > 1:
            trigger_commands = list(latest_commands[-2:])
        else:
            trigger_commands = list(latest_commands[-1])
    feedback_data["trigger_commands"] = trigger_commands

    # get exception while command failed, succeeded commands return ' '
    if processed_exception and processed_exception != '':
        feedback_data["error_info"] = processed_exception

    # get all recommend sources and types
    has_personalized_rec = False
    if recommends:
        recommends_list = []
        source_list = set()
        recommend_type_list = set()
        for item in recommends:
            try:
                recommends_list.append({"command": str(item['command'])})
            except KeyError:
                recommends_list.append({"scenario": str(item['scenario'])})
            source_list.add(str(item['source']))
            recommend_type_list.add(str(item['type']))
            if 'is_personalized' in item:
                has_personalized_rec = True
        feedback_data["recommendations_source_list"] = sorted(source_list)
        feedback_data["recommendations_type_list"] = sorted(recommend_type_list)
        feedback_data["recommendations_list"] = recommends_list

    if accepted_recommend:
        feedback_data["accepted_recommend_source"] = accepted_recommend['source']
        feedback_data["accepted_recommend_type"] = accepted_recommend['type']
        if accepted_recommend['type'] in [RecommendType.Scenario, RecommendType.Search]:
            feedback_data['accepted_recommend'] = accepted_recommend['scenario']
        else:
            feedback_data['accepted_recommend'] = accepted_recommend['command']

        if not has_personalized_rec:
            feedback_data["is_personalized"] = None
        elif 'is_personalized' in accepted_recommend:
            feedback_data["is_personalized"] = 1
        else:
            feedback_data["is_personalized"] = 0

    # replace null to None:
    for key, value in feedback_data.items():
        if value is None:
            feedback_data[key] = "None"

    telemetry.start(mode='interactive')
    if request_type == RecommendType.Search:
        telemetry.set_command_details('search')
    else:
        telemetry.set_command_details('next')
    telemetry.set_cli_recommendation(api_version=api_version, feedback=feedback_data)
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
    for idx in exec_idx:
        nx_cmd = scenario["nextCommandSet"][idx]
        print()
        command_sample = _get_command_sample(nx_cmd)
        print_styled_text([(Style.ACTION, "Running: ")] + command_sample,
                          file=file)
        yield nx_cmd, ''.join([part[1] for part in command_sample])


def _get_command_sample(command):
    """Try getting example from command. Or load the example from `--help` if not found."""
    if "example" in command and command["example"]:
        command_sample, _ = _format_command_sample(command["example"])
        return command_sample

    from knack import help_files
    parameter = []
    if "arguments" in command and command["arguments"]:
        parameter = command["arguments"]
        sorted_param = sorted(parameter)
        cmd_help = help_files._load_help_file(command['command'])  # pylint: disable=protected-access
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
    if the parameter dose not have $ to show it is customisable, it will return the raw command sample value. For example: -o tsv
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
            if argument_value.startswith('$'):
                argument_value = argument_value[1:]
                argument_value = '<' + argument_value + '>'
            formatted_example.append((Style.WARNING, ' ' + argument_value))

    return formatted_example, example_arguments
