# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import re
import json

from azure.cli.core.azclierror import RecommendationError
from knack import help_files
from .utils import (get_int_option, get_command_list, get_last_exception, get_title_case, get_yes_or_no_option,
                    get_latest_command, get_combined_option, OptionRange)
from .constants import RecommendType
from colorama import Fore, init
from .requests import get_recommend_from_api
from azure.cli.core.style import print_styled_text, Style
import azure.cli.core.telemetry as telemetry


def handle_next(cmd, command_only=False, scenario_only=False):
    init(autoreset=True)  # turn on automatic color recovery for colorama

    if scenario_only:
        request_type = RecommendType.Scenario.value
    elif command_only:
        request_type = RecommendType.Command.value
    else:
        request_type = RecommendType.get(cmd.cli_ctx.config.get('next', 'filter_type', fallback='mix')).value

    # Upload all execution commands of local record for personalized analysis
    command_history = get_command_list(cmd, 0)

    processed_exception = None
    if request_type == RecommendType.All or request_type == RecommendType.Solution:
        processed_exception = get_last_exception(cmd, get_latest_command(command_history))

    if request_type == RecommendType.Solution and not processed_exception:
        _handle_error_no_exception_found()
        return None

    recommends = get_recommend_from_api(command_history, request_type,
                                        cmd.cli_ctx.config.getint('next', 'num_limit', fallback=5),
                                        error_info=processed_exception)
    if not recommends:
        send_feedback(request_type, -1, command_history, processed_exception)
        print("\nSorry, there is no recommendation in the next step.")
        return

    print()

    command_recommendations = [item for item in recommends if item['type'] != RecommendType.Scenario]
    scenario_recommendations = [item for item in recommends if item['type'] == RecommendType.Scenario]
    multi_type_recommendation = True
    if len(command_recommendations) == 0:
        multi_type_recommendation = False
    if len(scenario_recommendations) == 0:
        multi_type_recommendation = False

    if not multi_type_recommendation:
        _give_recommends(cmd, recommends)

        option = get_int_option("Please select your option " + Fore.LIGHTBLACK_EX + "(if none, enter 0)" +
                                Fore.RESET + ": ", 0, len(recommends), -1)
        if option == 0:
            send_feedback(request_type, 0, command_history, processed_exception, recommends)
            print(
                '\nThank you for your feedback. If you have more feedback, please submit it by using "az feedback" \n')
            return
        print()

        rec = recommends[option - 1]
        send_feedback(request_type, option, command_history, processed_exception, recommends, rec)
    else:
        print_styled_text([(Style.PRIMARY, "SCENARIO")])
        print()
        _give_recommends(cmd, scenario_recommendations, prefix='a')
        print_styled_text([(Style.PRIMARY, "COMMAND")])
        print()
        _give_recommends(cmd, command_recommendations, prefix='b')
        group, option = get_combined_option(
            "Please select your option " + Fore.LIGHTBLACK_EX + "(for example, enter \"a2\" for the second scenario. if none, enter 0)" +
            Fore.RESET + ": ",
            {'a': OptionRange(1, len(scenario_recommendations)), 'b': OptionRange(1, len(command_recommendations))},
            (None, -1))
        if group == 'a':
            rec = scenario_recommendations[option - 1]
        elif group == 'b':
            rec = command_recommendations[option - 1]
        else:
            send_feedback(request_type, 0, command_history, processed_exception, recommends)
            print(
                '\nThank you for your feedback. If you have more feedback, please submit it by using "az feedback" \n')
            return
        print()

    if rec['type'] == RecommendType.Scenario:
        _show_details_for_e2e_scenario(cmd, rec)
    elif cmd.cli_ctx.config.getboolean('next', 'print_help', fallback=False):
        _print_help_info(cmd, rec["command"])

    if cmd.cli_ctx.config.getboolean('next', 'execute_in_prompt', fallback=True):
        _execute_recommends(cmd, rec)
    else:
        print('\nThank you for your feedback. AZ NEXT is completed. '
              'If you want to execute the commands in interactive mode, '
              'you can use "az config set next.execute_in_prompt=True" to set it up.\n')

    return None


def _handle_error_no_exception_found():
    '''You choose to solve the previous problems but no exception found'''
    error_msg = 'The error information is missing, ' \
                'the solution is recommended only if only an exception occurs in the previous step.'
    recommendation = 'The recommendation for solution type need to turn on telemetry. ' \
                     'If you haven not turned it on yet, ' \
                     'please run "az config set core.collect_telemetry=True" and try again.'
    az_error = RecommendationError(error_msg, recommendation)
    az_error.print_error()


def _give_recommends(cmd, recommends, prefix=''):
    for idx, rec in enumerate(recommends):
        if rec['type'] == RecommendType.Scenario:
            _give_recommend_scenarios(prefix + str(idx + 1), rec)
        else:
            _give_recommend_commands(cmd, prefix + str(idx + 1), rec)


def _get_cmd_help_from_ctx(cmd, default_value):
    command_help = default_value
    cmd_help = help_files._load_help_file(cmd)
    if cmd_help and 'short-summary' in cmd_help:
        command_help = cmd_help['short-summary']
    if command_help:
        command_help = command_help.split('.')[0] + '.'
    return command_help


def _feed_arguments_from_sample(rec):
    cmd_help = help_files._load_help_file(rec['command'])
    if cmd_help:
        if cmd_help['type'] == 'group':
            rec['arguments'] = ['-h']

        elif 'examples' in cmd_help and cmd_help['examples']:
            cmd_example = cmd_help['examples'][0]['text']
            if cmd_example:
                cmd_items = cmd_example.split()
                arguments = []
                argument_start = False
                has_positional_arguments = False
                for item in cmd_items:
                    if item.startswith('-'):
                        arguments.append(item)
                        argument_start = True
                    elif not argument_start and item not in rec['command'] and item != 'az':
                        has_positional_arguments = True

                if arguments:
                    rec['arguments'] = arguments
                if has_positional_arguments:
                    if rec['arguments'] is None:
                        rec['arguments'] = ['<positional argument>']
                    else:
                        rec['arguments'].insert(0, '<positional argument>')


def _give_recommend_commands(cmd, idx, rec):
    index_str = "[" + str(idx) + "] "
    command_item = "az " + rec['command']
    no_arguments = 'arguments' not in rec or not rec['arguments'] or \
                   (len(rec['arguments']) == 1 and rec['arguments'][0] == '')
    if no_arguments:
        _feed_arguments_from_sample(rec)

    if 'arguments' in rec and cmd.cli_ctx.config.getboolean('next', 'show_arguments', fallback=False):
        command_item = "{} {}".format(command_item, ' '.join(rec['arguments']))
    print_styled_text([(Style.ACTION, index_str), (Style.PRIMARY, command_item)])

    if 'reason' in rec:
        reason = rec['reason']
    else:
        reason = _get_cmd_help_from_ctx(rec['command'], "")
        if 'usage_condition' in rec and rec['usage_condition']:
            reason = reason + " (" + rec['usage_condition'] + ")"

    if reason:
        space_padding = re.sub('.', ' ', index_str)
        print_styled_text([(Style.SECONDARY, space_padding + get_title_case(reason) + "\n")])
    else:
        print()


def _give_recommend_scenarios(idx, rec):
    index_str = "[" + str(idx) + "] "
    num_notice = " ({} Commands)".format(len(rec['nextCommandSet']))
    print_styled_text([(Style.ACTION, index_str), (Style.PRIMARY, rec['scenario']), (Style.SECONDARY, num_notice)])
    if 'reason' in rec:
        reason = rec['reason']
    else:
        reason = "This is a set of commands that may help you complete this scenario."

    if reason:
        space_padding = re.sub('.', ' ', index_str)
        print_styled_text([(Style.SECONDARY, space_padding + get_title_case(reason) + "\n")])
    else:
        print()


def _execute_recommends(cmd, rec):
    if rec['type'] == RecommendType.Scenario:
        _execute_recommend_scenarios(cmd, rec)
    else:
        _execute_recommend_commands(cmd, rec)


def _execute_nx_cmd(cmd, nx_cmd, nx_param, catch_exception=False):
    args = []
    args.extend(nx_cmd.split())
    nx_param = [param for param in nx_param if param and param != '']
    for param in nx_param:
        store_true_params = ['-h', '--yes', '-y', '--no-wait', '--dry-run', '--no-log']
        if param in store_true_params:
            args.append(param)
        else:
            print("Please input " + Fore.LIGHTBLUE_EX + param + Fore.RESET + ":", end='')
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

    output_format = cmd.cli_ctx.config.get('next', 'output', fallback='status')

    if '--output' not in args and '-o' not in args:
        args.append('--output')
        if 'status' == output_format:
            is_show_operation = False
            for operation in ['show', 'list', 'get', 'version']:
                if operation in nx_cmd:
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
        exit_code = cmd.cli_ctx.invoke(args)

    else:
        try:
            exit_code = cmd.cli_ctx.invoke(args)
        except Exception:
            return -1
        except SystemExit:
            return -1

    if 'status' == output_format and exit_code == 0:
        from .utils import print_successful_styled_text
        print_successful_styled_text('command completed\n')

    return exit_code


def _get_command_item_sample(rec):
    if "example" in rec and rec["example"]:
        example = Fore.LIGHTBLUE_EX + rec["example"]
        example = re.sub('<', Fore.RESET + '<', example)
        example = re.sub('>', '>' + Fore.LIGHTBLUE_EX, example)
        return example

    nx_param = []
    if "arguments" in rec and rec["arguments"]:
        nx_param = rec["arguments"]
        sorted_nx_param = sorted(nx_param)
        cmd_help = help_files._load_help_file(rec['command'])
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
                            example = example + Fore.RESET + ' <' + ' '.join(argument_values[argument]) + '>'
                    return example

    return Fore.LIGHTBLUE_EX + "az {} {}".format(rec["command"], ' '.join(nx_param) if nx_param else "")


def _execute_recommend_commands(cmd, rec):
    nx_param = []
    if "arguments" in rec:
        nx_param = rec["arguments"]
    print("\nRunning: " + _get_command_item_sample(rec))
    print_styled_text([(Style.SECONDARY, "Input Enter to skip unnecessary parameters")])
    execute_result = _execute_nx_cmd(cmd, rec["command"], nx_param, catch_exception=True)
    is_help_printed = False
    while execute_result != 0:
        if not cmd.cli_ctx.config.getboolean('next', 'print_help', fallback=False) and not is_help_printed:
            _print_help_info(cmd, rec["command"])
            is_help_printed = True

        step_msg = "Do you want to retry this command? " + Fore.LIGHTBLACK_EX + "(y/n)" + Fore.RESET + ": "
        run_option = get_yes_or_no_option(step_msg)
        if run_option:
            execute_result = _execute_nx_cmd(cmd, rec["command"], nx_param, catch_exception=True)
        else:
            print()
            return


def _execute_recommend_scenarios(cmd, rec):
    exec_idx = rec.get("execIdx")
    for idx, nx_cmd in enumerate(rec["nextCommandSet"]):
        cmd_active = exec_idx is None or idx in exec_idx
        if not cmd_active:
            continue
        nx_param = []
        if "arguments" in nx_cmd:
            nx_param = nx_cmd["arguments"]

        if cmd.cli_ctx.config.getboolean('next', 'print_help', fallback=False):
            _print_help_info(cmd, nx_cmd["command"])

        print("\nRunning: " + _get_command_item_sample(nx_cmd))
        step_msg = "How do you want to run this step? 1. Run it 2. Skip it 3. Quit process " + Fore.LIGHTBLACK_EX \
                   + "(Enter is to Run)" + Fore.RESET + ": "
        run_option = get_int_option(step_msg, 1, 3, 1)
        if run_option == 1:
            print_styled_text([(Style.SECONDARY, "Input Enter to skip unnecessary parameters")])
            execute_result = _execute_nx_cmd(cmd, nx_cmd['command'], nx_param, catch_exception=True)
            is_help_printed = False
            while execute_result != 0:
                if not cmd.cli_ctx.config.getboolean('next', 'print_help', fallback=False) and not is_help_printed:
                    _print_help_info(cmd, nx_cmd["command"])
                    is_help_printed = True

                step_msg = "Do you want to retry this step? 1. Run it 2. Skip it 3. Quit process " + Fore.LIGHTBLACK_EX \
                           + "(Enter is to Run)" + Fore.RESET + ": "
                run_option = get_int_option(step_msg, 1, 3, 1)
                if run_option == 1:
                    execute_result = _execute_nx_cmd(cmd, nx_cmd['command'], nx_param, catch_exception=True)
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
    print_successful_styled_text('All commands in this scenario have been executed! \n')


def _get_filter_option():
    msg = '''
Please select the type of recommendation you need:
1. all: It will intelligently analyze the types of recommendation you need, and may recommend multiple types of command to you
2. solution: Only the solutions to problems when errors occur are recommend
3. command: Only the commands with high correlation with previously executed commands are recommend
4. scenario: Only the E2E scenarios related to current usage scenarios are recommended
'''
    print(msg)
    return get_int_option("What kind of recommendation do you want? " + Fore.LIGHTBLACK_EX + "(RETURN is to set all)" +
                          Fore.RESET + ": ", 1, 4, 1)


def _show_details_for_e2e_scenario(cmd, rec):
    print_styled_text([(Style.PRIMARY, rec['scenario']),
                       (Style.ACTION, " contains the following commands:\n")])

    nx_cmd_set = rec["nextCommandSet"]
    exec_idx = rec.get("execIdx")
    for idx, nx_cmd in enumerate(nx_cmd_set):
        command_item = "az " + nx_cmd['command']
        if 'arguments' in nx_cmd and cmd.cli_ctx.config.getboolean('next', 'show_arguments', fallback=False):
            command_item = "{} {}".format(command_item, ' '.join(nx_cmd['arguments']))
        cmd_active = exec_idx is None or idx in exec_idx
        print_styled_text([(Style.ACTION, " > "), (Style.PRIMARY if cmd_active else Style.SECONDARY, command_item)])

        if nx_cmd['reason']:
            print_styled_text([(Style.SECONDARY, get_title_case(nx_cmd['reason']) + "\n")])
        else:
            print()


def send_feedback(request_type, option, latest_commands, processed_exception=None, recommends=None, rec=None):
    feedback_data = [str(request_type), str(option)]

    if latest_commands:
        trigger_commands = json.loads(latest_commands[-1])['command']
        if len(latest_commands) > 1:
            trigger_commands = json.loads(latest_commands[-2])['command'] + "," + trigger_commands
        feedback_data.append(trigger_commands)
    else:
        feedback_data.append(' ')
    if processed_exception and processed_exception != '':
        feedback_data.append(processed_exception)
    else:
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

    telemetry.set_feedback("#".join(feedback_data))


def _print_help_info(cmd, command):
    print("\n---------- Help Start ----------")
    try:
        _execute_nx_cmd(cmd, command, ["-h", "--no-log"])
    except SystemExit:
        pass
    print("---------- Help End ----------\n")
