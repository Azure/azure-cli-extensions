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


def get_yes_or_no_option(option_description):
    print(Fore.LIGHTBLUE_EX + ' ? ' + Fore.RESET + option_description, end='')
    option = input()
    yes_options = ["y", "yes", "Y", "Yes", "YES"]
    no_options = ["n", "no", "N", "No", "NO"]
    while (option not in yes_options) and (option not in no_options):
        option = input("This option can only be Yes or No, please input again: ")
    return option in yes_options


def get_int_option(option_description, min_option, max_option, default_option):
    print(Fore.LIGHTBLUE_EX + ' ? ' + Fore.RESET + option_description, end='')
    option = read_int(default_option)
    while option < min_option or option > max_option:
        print("The range of options is {}-{}, please input again: ".format(min_option, max_option), end='')
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


def get_last_exception(cmd):
    '''Get last executed command from local log files'''
    import os
    history_file_name = os.path.join(cmd.cli_ctx.config.config_dir, 'recommendation', 'exception_history.log')
    if not os.path.exists(history_file_name):
        return ''
    with open(history_file_name, "r") as f:
        lines = f.read().splitlines()
        return lines[-1]
    return ''


def get_title_case(str):
    if not str:
        return str
    str = str.strip()
    return str[0].upper() + str[1:]


def _is_modern_terminal():
    # Windows Terminal: https://github.com/microsoft/terminal/issues/1040
    if 'WT_SESSION' in os.environ:
        return True
    # VS Code: https://github.com/microsoft/vscode/pull/30346
    if os.environ.get('TERM_PROGRAM', '').lower() == 'vscode':
        return True
    return False


def is_modern_terminal():
    """Detect whether the current terminal is a modern terminal that supports Unicode and
    Console Virtual Terminal Sequences.
    Currently, these terminals can be detected:
      - Windows Terminal
      - VS Code terminal
    """
    # This function wraps _is_modern_terminal and use a function-level cache to save the result.
    if not hasattr(is_modern_terminal, "return_value"):
        setattr(is_modern_terminal, "return_value", _is_modern_terminal())
    return getattr(is_modern_terminal, "return_value")


def print_successful_styled_text(message):

    from azure.cli.core.style import print_styled_text, Style
    prefix_text = '\nDone: '
    if is_modern_terminal():
        prefix_text = '\n(✓ )Done: '
    print_styled_text([(Style.SUCCESS, prefix_text), (Style.PRIMARY, message)])
