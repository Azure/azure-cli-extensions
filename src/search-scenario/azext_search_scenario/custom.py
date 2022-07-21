# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from azure.cli.core import telemetry
from azure.cli.core.style import Style, print_styled_text
from colorama import Fore, init

from .constants import SearchType
from .requests import get_search_result_from_api
from .utils import get_int_option


# pylint: disable=redefined-builtin
def search_scenario(cmd, search_keyword, type=None, top=None):
    init(autoreset=True)  # turn on automatic color recovery for colorama
    if type == "scenario":
        search_type = SearchType.Scenario
    elif type == "command":
        search_type = SearchType.Command
    else:
        search_type = SearchType.All

    search_keyword = " ".join(search_keyword)
    results = get_search_result_from_api(search_keyword, search_type, top)

    if not results:
        send_feedback(search_type, -1, search_keyword)
        print("\nSorry, there is no scenario result.")
        return

    _show_results(results)
    print()

    # TODO: Use style instead of colorma
    option = get_int_option("Please select your option " + Fore.LIGHTBLACK_EX + "(if none, enter 0)" +
                            Fore.RESET + ": ", 0, len(results), -1)
    if option == 0:
        send_feedback(search_type, 0, search_keyword, results)
        print('\nThank you for your feedback. If you have more feedback, please submit it by using "az feedback" \n')
        return
    print()

    chosen_scenario = results[option - 1]
    send_feedback(search_type, option, search_keyword,
                  results, chosen_scenario)
    _show_detail(cmd, chosen_scenario)

    if cmd.cli_ctx.config.getboolean('search_scenario', 'execute_in_prompt', fallback=True):
        _execute_scenario(cmd, chosen_scenario)
    else:
        print('\nThank you for your feedback. AZ SCENARIO-SEARCH is completed. '
              'If you want to execute the commands in interactive mode, '
              'you can use "az config set search_scenario.execute_in_prompt=True" to set it up.\n')

    return


def _show_results(results, highlight_style=Style.ACTION):
    for idx, result in enumerate(results):
        print()
        idx_str = f"[{idx+1:2}] " if len(results) >= 10 else f"[{idx+1:1}] "
        num_notice = f"({len(result['commandSet'])} Commands)"
        print_styled_text([(Style.ACTION, idx_str), (Style.PRIMARY,
                          result['scenario']), (Style.SECONDARY, num_notice)])
        highlight_desc = next(
            iter(result.get('highlights', {}).get('description', [])), None)
        if highlight_desc:
            print_styled_text(_style_highlight(
                highlight_desc, highlight_style))
            continue
        highlight_cmd = next(
            iter(result.get('highlights', {}).get('commandSet/command', [])), None)
        if highlight_cmd:
            print_styled_text(_style_highlight(highlight_cmd, highlight_style))
            continue
        highlight_name = next(
            iter(result.get('highlights', {}).get('scenario', [])), None)
        if highlight_name:
            print_styled_text(_style_highlight(
                highlight_name, highlight_style))
            continue
        print_styled_text((Style.SECONDARY, result.get('description', "")))
    print()


def _show_detail(cmd, scenario):
    print_styled_text([(Style.PRIMARY, scenario['scenario']),
                       (Style.ACTION, " contains the following commands:\n")])
    for command in scenario["commandSet"]:
        command_item = command["command"]
        if 'arguments' in command and \
                cmd.cli_ctx.config.getboolean('search_scenario', 'show_arguments', fallback=False):
            command_item = f"{command_item} {' '.join(command['arguments'])}"
        print_styled_text(
            [(Style.ACTION, " > "), (Style.PRIMARY, command_item)])

        if command['reason']:
            print_styled_text([(Style.SECONDARY, command['reason'].replace(
                "\\n", " ").split(".")[0].strip().capitalize())])
        print()
    if scenario.get("source_url"):
        print_styled_text([(Style.PRIMARY, "To learn more about this scenario, please visit "),
                           (Style.HYPERLINK, scenario.get("source_url"))])
        print()


def _execute_scenario(ctx_cmd, scenario):
    for command in scenario["commandSet"]:
        nx_param = []
        if "arguments" in command:
            nx_param = command["arguments"]

        if ctx_cmd.cli_ctx.config.getboolean('search_scenario', 'print_help', fallback=False):
            _print_help_info(ctx_cmd, command["command"])

        print("\nRunning: " + _get_command_item_sample(command))
        step_msg = "How do you want to run this step? 1. Run it 2. Skip it 3. Quit process " + Fore.LIGHTBLACK_EX \
                   + "(Enter is to Run)" + Fore.RESET + ": "
        run_option = get_int_option(step_msg, 1, 3, 1)
        if run_option == 1:
            print_styled_text(
                [(Style.SECONDARY, "Input Enter to skip unnecessary parameters")])
            execute_result = _execute_cmd(
                ctx_cmd, command['command'], nx_param, catch_exception=True)
            is_help_printed = False
            while execute_result != 0:
                if not ctx_cmd.cli_ctx.config.getboolean('search_scenario', 'print_help', fallback=False) \
                        and not is_help_printed:
                    _print_help_info(ctx_cmd, command["command"])
                    is_help_printed = True

                step_msg = "Do you want to retry this step? 1. Run it 2. Skip it 3. Quit process " \
                    + Fore.LIGHTBLACK_EX + "(Enter is to Run)" + Fore.RESET + ": "
                run_option = get_int_option(step_msg, 1, 3, 1)
                if run_option == 1:
                    execute_result = _execute_cmd(
                        ctx_cmd, command['command'], nx_param, catch_exception=True)
                elif run_option == 2:
                    print()
                    break
                else:
                    print()
                    return
        elif run_option == 2:
            print()
            continue
        else:
            print()
            break

    from .utils import print_successful_styled_text
    print_successful_styled_text(
        'All commands in this scenario have been executed! \n')


def _style_highlight(highlight_content: str, highlight_style=Style.ACTION) -> list:
    styled_text_object = []
    remain = highlight_content
    in_highlight = False
    while remain:
        split_result = remain.split('<em>' if not in_highlight else "</em>", 1)
        content = split_result[0]
        try:
            remain = split_result[1]
        except IndexError:
            remain = None
        styled_text_object.append(
            (Style.SECONDARY if not in_highlight else highlight_style, content))
        in_highlight = not in_highlight
    return styled_text_object


def _execute_cmd(ctx_cmd, command, params, catch_exception=False):
    args = []
    args.extend(command.split())
    if args[0] == "az":
        args.pop(0)
    params = [param for param in params if param and param != '']
    for param in params:
        store_true_params = ['-h', '--yes', '-y',
                             '--no-wait', '--dry-run', '--no-log']
        if param in store_true_params:
            args.append(param)
        else:
            print("Please input " + Fore.LIGHTBLUE_EX +
                  param + Fore.RESET + ":", end='')
            value = input()
            if param == '<positional argument>':
                if value:
                    args.append(value)
            else:
                args.append(param)
                if value:
                    args.append(value)
                else:
                    args.pop()

    output_format = ctx_cmd.cli_ctx.config.get(
        'next', 'output', fallback='status')

    if '--output' not in args and '-o' not in args:
        args.append('--output')
        if output_format == 'status':
            is_show_operation = False
            for operation in ['show', 'list', 'get', 'version']:
                if operation in command:
                    is_show_operation = True
                    break
            if is_show_operation:
                args.append('json')
            else:
                args.append('none')
        else:
            args.append(output_format)

    exit_code = 0
    if not catch_exception:
        exit_code = ctx_cmd.cli_ctx.invoke(args)

    else:
        try:
            exit_code = ctx_cmd.cli_ctx.invoke(args)
        except Exception:   # pylint: disable=broad-except
            return -1
        except SystemExit:
            return -1

    if output_format == 'status' and exit_code == 0:
        from .utils import print_successful_styled_text
        print_successful_styled_text('command completed\n')

    return exit_code


def _get_command_item_sample(command):
    if "example" in command and command["example"]:
        converted_example = command["example"].replace(" $", " ")
        if "$" not in converted_example:
            example = Fore.LIGHTBLUE_EX + converted_example
            example = re.sub('<', Fore.RESET + '<', example)
            example = re.sub('>', '>' + Fore.LIGHTBLUE_EX, example)
            return example

    from knack import help_files
    nx_param = []
    if "arguments" in command and command["arguments"]:
        nx_param = command["arguments"]
        sorted_nx_param = sorted(nx_param)
        cmd_help = help_files._load_help_file(command['command'])   # pylint: disable=protected-access
        if cmd_help and 'examples' in cmd_help and cmd_help['examples']:
            for cmd_example in cmd_help['examples']:
                cmd_items = cmd_example['text'].split()

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

                if sorted(example_arguments) == sorted_nx_param:
                    example = Fore.LIGHTBLUE_EX + ' '.join(command_item)
                    for argument in example_arguments:
                        example = example + " " + Fore.LIGHTBLUE_EX + argument
                        if argument in argument_values and argument_values[argument]:
                            example = example + Fore.RESET + ' <' + \
                                ' '.join(argument_values[argument]) + '>'
                    return example

    command = command["command"] if command["command"].startswith("az ") else "az " + command["command"]
    return Fore.LIGHTBLUE_EX + f"{command} {' '.join(nx_param) if nx_param else ''}"


def send_feedback(search_type, option, keyword, search_results=None, adoption=None):
    feedback = str(int(search_type)) + "#" + str(option) + "#" + \
        keyword.replace("\\", "\\\\").replace("#", "\\sharp") + "#"
    if search_results and isinstance(search_results, list):
        feedback += " ".join(map(lambda r: str(r.get("source", 0)),
                             search_results))
    else:
        feedback += " "
    feedback += "#"
    if adoption:
        feedback += str(adoption.get("source", " ")) + "#" + adoption.get("scenario", " ") + \
            "#" + adoption.get("description", " ").replace("\\",
                                                           "\\\\").replace("#", "\\sharp")
    else:
        feedback += " # # "

    telemetry.set_feedback(feedback)


def _print_help_info(cmd, command):
    print("\n---------- Help Start ----------")
    try:
        _execute_cmd(cmd, command, ["-h", "--no-log"])
    except SystemExit:
        pass
    print("---------- Help End ----------\n")
