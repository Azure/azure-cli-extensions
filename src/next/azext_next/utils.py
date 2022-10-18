# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from colorama import Fore
import os
import json


def read_int(default_value=0):
    ret = input()
    if ret == '' or ret is None:
        return default_value
    while not ret.isnumeric():
        ret = input("Please input a legal number: ")
        if ret == '' or ret is None:
            return default_value
    return int(ret)


def read_combined_option(group_range, default_value=(None, 0)):
    """
    Read combined option from stdin, ensure the group_name is in range or be None and option is a ledge number
    :param group_range: the range a valid group name should be in
    :param default_value:
    :return: the combined option read from stdin
    :rtype: tuple[str|None, int]
    """
    ret = input()
    if ret == '' or ret is None:
        return default_value
    if ret.isnumeric():
        return None, int(ret)
    while True:
        group = ret[:1]
        option = ret[1:]
        if group not in group_range:
            ret = input("The option should start with " + " or ".join(group_range) + ":")
        elif not option.isnumeric():
            ret = input("The option should end with a ledge number: ")
        else:
            return group, int(option)


def get_yes_or_no_option(option_description):
    print(Fore.LIGHTBLUE_EX + ' ? ' + Fore.RESET + option_description, end='')
    option = input()
    yes_options = ["y", "yes", "Y", "Yes", "YES"]
    no_options = ["n", "no", "N", "No", "NO"]
    while (option not in yes_options) and (option not in no_options):
        option = input("This option can only be Yes or No, please input again: ")
    return option in yes_options


class OptionRange:
    def __init__(self, min_option, max_option):
        self.min_option = min_option
        self.max_option = max_option

    def __contains__(self, item):
        return self.min_option <= item <= self.max_option


def get_combined_option(option_description, valid_groups, default_option):
    """
    Read a combined option from stdin.
    Request user to re-enter if not in valid_group or range

    :param option_description: displayed description
    :type option_description: str
    :param valid_groups: a dict for valid group name and option range
    :type valid_groups: dict[str, OptionRange]
    :param default_option: default option if users input empty str
    :type default_option: tuple[str|None, int]
    :return: the group name and option the user input, which is ensured in valid groups or be (None, 0)
    :rtype: tuple[str|None, int]
    """
    print(Fore.LIGHTBLUE_EX + ' ? ' + Fore.RESET + option_description, end='')
    group, option = read_combined_option(valid_groups.keys(), default_option)
    while True:
        if group is None:
            if option == 0:
                return group, option
            print("The option should start with \"a\" for scenario, \"b\" for commands or be \"0\": ", end='')
            group, option = read_combined_option(valid_groups.keys(), default_option)
        elif option not in valid_groups[group]:
            print(f"The option should end with a valid option "
                  f"({group}{valid_groups[group].min_option}-{group}{valid_groups[group].max_option}): ", end='')
            group, option = read_combined_option(valid_groups.keys(), default_option)
        else:
            return group, option


def get_int_option(option_description, min_option, max_option, default_option):
    print(Fore.LIGHTBLUE_EX + ' ? ' + Fore.RESET + option_description, end='')
    option = read_int(default_option)
    while option < min_option or option > max_option:
        print(f"Please enter a valid option ({min_option}-{max_option}): ", end='')
        option = read_int(default_option)
    return option


def get_command_list(cmd, num=2):
    '''Get last executed command from local log files'''
    history_file_name = os.path.join(cmd.cli_ctx.config.config_dir, 'recommendation', 'cmd_history.log')
    if not os.path.exists(history_file_name):
        return _get_command_list_from_core(cmd, num)
    with open(history_file_name, "r") as f:
        lines = f.read().splitlines()
        lines = [x for x in lines if x != 'next']
        return lines[-num:]

    # If the historical execution record is not found in the file recorded by "az next",
    # it may be the first time that "az next" is installed.
    # At this time, we will take the history recorded in the file under commands directory
    return _get_command_list_from_core(cmd, num)


def _get_command_list_from_core(cmd, num=2):
    commands_history_dir = os.path.join(cmd.cli_ctx.config.config_dir, 'commands')
    if not os.path.isdir(commands_history_dir):
        return []

    command_file_list = os.listdir(commands_history_dir)
    command_file_list.sort(key=lambda fn: fn, reverse=True)
    command_list = []
    for item in command_file_list:
        if 'next' in item or 'extension_add' in item or 'unknown_command' in item:
            continue
        command_info = _parse_command_file(os.path.join(commands_history_dir, item))
        if command_info:
            command_list.insert(0, command_info)
            if len(command_list) == num:
                return command_list

    return command_list


def _parse_command_file(command_file_path):
    if not os.path.exists(command_file_path):
        return ""

    with open(command_file_path, "r") as f:
        first_line = f.readline()
        if not first_line:
            return ""
        line_items = first_line.split('command args: ')
        if len(line_items) != 2:
            return ""
        command_str = line_items[1]
        if not command_str:
            return ""

        items = command_str.split()
        commend_items = []
        argument_items = []
        for item in items:
            if item.startswith('-'):
                argument_items.append(item)
            elif not item.startswith('{'):
                commend_items.append(item)

        command_info = {'command': ' '.join(commend_items)}
        if argument_items:
            command_info['arguments'] = argument_items

        return json.dumps(command_info)


def get_latest_command(command_history):
    if not command_history:
        return ''

    command_list_data = reversed(command_history)
    for command_item in command_list_data:
        cmd = json.loads(command_item)
        if cmd['command'] == 'next':
            continue
        return cmd['command']


def get_last_exception(cmd, latest_command):
    '''Get last exception from T cache'''
    # Because Telemetry cache is the place where all exceptions are recorded uniformly
    # And it needs to decouple from azure-cli-core, so it's designed to get exceptions from Telemetry cache.

    # If Telemetry is turned off, the errors recorded in the Telemetry cache will stagnate,
    # resulting in a mismatch with the last executed command
    if not cmd.cli_ctx.config.getboolean('core', 'collect_telemetry', fallback=True):
        return ''

    telemetry_cache_file = os.path.join(cmd.cli_ctx.config.config_dir, 'telemetry', 'cache')
    if not os.path.exists(telemetry_cache_file):
        return ''

    with open(telemetry_cache_file, "r") as f:
        lines = f.read().splitlines()
        history_data_list = reversed(lines)
        for history_data_item in history_data_list:
            if not history_data_item:
                return ''

            record_data = history_data_item.split(',', 1)
            if not record_data or len(record_data) < 2:
                return ''

            import ast
            data_dict = ast.literal_eval(record_data[1])
            if not data_dict or len(data_dict) != 1:
                return

            data_item = list(data_dict.values())[0][0]
            if not data_item or 'properties' not in data_item:
                return
            properties = data_item['properties']

            command_key = 'Context.Default.AzureCLI.RawCommand'
            if command_key not in properties:
                continue
            command = properties[command_key]
            if command == 'next':
                continue

            # When executing "az next" after telemetry is turned off and than turned on,
            # make sure that the command in Telemetry cache can match the latest command
            if latest_command != command:
                return ''

            latest_exception = ''
            summary_key = 'Reserved.DataModel.Action.ResultSummary'
            exception_key = 'Reserved.DataModel.Fault.Exception.Message'
            if summary_key in properties and properties[summary_key]:
                latest_exception = properties[summary_key]
            elif exception_key in properties and properties[exception_key]:
                latest_exception = properties[exception_key]

            return latest_exception

    return ''


def get_title_case(str):
    if not str:
        return str
    str = str.strip()
    return str[0].upper() + str[1:]


def print_successful_styled_text(message):
    from azure.cli.core.style import print_styled_text, Style, is_modern_terminal

    prefix_text = '\nDone: '
    if is_modern_terminal():
        prefix_text = '\n(✓ )Done: '
    print_styled_text([(Style.SUCCESS, prefix_text), (Style.PRIMARY, message)])


def log_command_history(command, args):
    import os
    from knack.util import ensure_dir
    from azure.cli.core._environment import get_config_dir

    if not args or '--no-log' in args:
        return

    if not command or command == 'next':
        return

    base_dir = os.path.join(get_config_dir(), 'recommendation')
    ensure_dir(base_dir)

    file_path = os.path.join(base_dir, 'cmd_history.log')
    if not os.path.exists(file_path):
        with open(file_path, 'w') as fd:
            fd.write('')

    lines = []
    with open(file_path, 'r') as fd:
        lines = fd.readlines()
        lines = [x.strip('\n') for x in lines if x]

    with open(file_path, 'w') as fd:
        command_info = {'command': command}
        params = []
        for arg in args:
            if arg.startswith('-'):
                params.append(arg)
        if params:
            command_info['arguments'] = params

        lines.append(json.dumps(command_info))
        if len(lines) > 30:
            lines = lines[-30:]
        fd.write('\n'.join(lines))
