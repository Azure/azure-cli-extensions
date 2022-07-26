# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import telemetry
from azure.cli.core.style import Style, print_styled_text

from .constants import MatchRule, SearchScope
from .requests import get_search_result_from_api
from .utils import get_int_option


def search_scenario(cmd, search_keyword, scope=None, match_rule=None, top=None):

    scope = SearchScope.get_search_scope_by_name(scope)
    match_rule = MatchRule.get_match_rule_by_name(match_rule)
    search_keyword = " ".join(map(lambda w: w.replace("-", " "), search_keyword))
    results = get_search_result_from_api(search_keyword, scope, match_rule, top)

    if not results:
        send_feedback(scope, -1, search_keyword)
        print("\nSorry, no relevant E2E scenario examples found")
        return

    _show_search_item(results)

    option_msg = [(Style.ACTION, " ? "), (Style.PRIMARY, "Please select your option "),
                  (Style.SECONDARY, "(if none, enter 0)"), (Style.PRIMARY, ": ")]
    option = get_int_option(option_msg, 0, len(results), -1)
    print()

    if option == 0:
        send_feedback(scope, 0, search_keyword, results)
        print('Thank you for your feedback. If you have more feedback, please submit it by using "az feedback" \n')
        return

    chosen_scenario = results[option - 1]
    _show_detail(cmd, chosen_scenario)
    send_feedback(scope, option, search_keyword, results, chosen_scenario)

    if cmd.cli_ctx.config.getboolean('search_scenario', 'execute_in_prompt', fallback=True):
        _execute_scenario(cmd, chosen_scenario)
    else:
        print('\nThank you for your feedback. AZ SEARCH-SCENARIO is completed. '
              'If you want to execute the commands in interactive mode, '
              'you can use "az config set search_scenario.execute_in_prompt=True" to set it up.\n')

    return


def _show_search_item(results):

    for idx, result in enumerate(results):

        print()
        idx_str = f"[{idx+1:2}] " if len(results) >= 10 else f"[{idx+1:1}] "
        num_notice = f" ({len(result['commandSet'])} Commands)"
        print_styled_text([(Style.ACTION, idx_str), (Style.PRIMARY, result['scenario']), (Style.SECONDARY, num_notice)])

        highlight_desc = next(iter(result.get('highlights', {}).get('description', [])), None)
        if highlight_desc:
            print_styled_text(_style_highlight(highlight_desc))
            continue

        highlight_command = max(result.get('highlights', {}).get('commandSet/command', []), key=lambda cmd: len(cmd.split("<em>")), default=None)
        if highlight_command:
            include_command_style = [(Style.SECONDARY, "Include command: ")]
            include_command_style.extend(_style_highlight(highlight_command))
            print_styled_text(include_command_style)
            continue

        highlight_name = next(iter(result.get('highlights', {}).get('scenario', [])), None)
        if highlight_name:
            print_styled_text(_style_highlight(highlight_name))
            continue

        print_styled_text((Style.SECONDARY, result.get('description', "")))

    print()


def _show_detail(cmd, scenario):
    print_styled_text([(Style.WARNING, scenario['scenario']), (Style.PRIMARY, " contains the following commands:\n")])

    for command in scenario["commandSet"]:
        command_item = command["command"]
        if 'arguments' in command and \
                cmd.cli_ctx.config.getboolean('search_scenario', 'show_arguments', fallback=False):
            command_item = f"{command_item} {' '.join(command['arguments'])}"

        print_styled_text([(Style.ACTION, " > "), (Style.PRIMARY, command_item)])

        if command['reason']:
            command_desc = command['reason'].replace("\\n", " ").split(".")[0].strip()
            command_desc = command_desc[:1].upper() + command_desc[1:]
            print_styled_text([(Style.SECONDARY, command_desc)])

        print()

    if scenario.get("source_url"):
        print_styled_text([(Style.PRIMARY, "To learn more about this scenario, please visit the link below:")])
        print_styled_text([(Style.HYPERLINK, scenario.get("source_url"))])
        print()


def _execute_scenario(ctx_cmd, scenario):

    for command in scenario["commandSet"]:
        parameters = []
        if "arguments" in command:
            parameters = command["arguments"]

        if ctx_cmd.cli_ctx.config.getboolean('search_scenario', 'print_help', fallback=False):
            _print_help_info(ctx_cmd, command["command"])

        print_styled_text([(Style.ACTION, "Running: ")], end='')
        print_styled_text(_get_command_item_sample(command))
        option_msg = [(Style.ACTION, " ? "),
                      (Style.PRIMARY, "How do you want to run this step? 1. Run it 2. Skip it 3. Quit process "),
                      (Style.SECONDARY, "(Enter is to Run)"), (Style.PRIMARY, ": ")]
        run_option = get_int_option(option_msg, 1, 3, 1)
        if run_option == 1:
            print_styled_text([(Style.SECONDARY, "Input Enter to skip unnecessary parameters")])
            execute_result = _execute_cmd(ctx_cmd, command['command'], parameters, catch_exception=True)
            is_help_printed = False
            while execute_result != 0:
                if not ctx_cmd.cli_ctx.config.getboolean('search_scenario', 'print_help', fallback=False) \
                        and not is_help_printed:
                    _print_help_info(ctx_cmd, command["command"])
                    is_help_printed = True

                option_msg = [(Style.ACTION, " ? "),
                              (Style.PRIMARY, "Do you want to retry this step? 1. Run it 2. Skip it 3. Quit process "),
                              (Style.SECONDARY, "(Enter is to Run)"), (Style.PRIMARY, ": ")]
                run_option = get_int_option(option_msg, 1, 3, 1)
                if run_option == 1:
                    execute_result = _execute_cmd(ctx_cmd, command['command'], parameters, catch_exception=True)
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


def _style_highlight(highlight_content: str) -> list:
    styled_description = []
    remain = highlight_content
    in_highlight = False
    while remain:
        split_result = remain.split('<em>' if not in_highlight else "</em>", 1)
        content = split_result[0]
        try:
            remain = split_result[1]
        except IndexError:
            remain = None
        styled_description.append((Style.SECONDARY if not in_highlight else Style.WARNING, content))
        in_highlight = not in_highlight
    return styled_description


def _execute_cmd(ctx_cmd, command, params, catch_exception=False):
    args = []
    args.extend(command.split())
    if args[0] == "az":
        args.pop(0)
    params = [param for param in params if param and param != '']
    for param in params:
        store_true_params = ['-h', '--yes', '-y', '--no-wait', '--dry-run', '--no-log']
        if param in store_true_params:
            args.append(param)
        else:
            print_styled_text([(Style.ACTION, "Please input "), (Style.PRIMARY, param + ": ")], end='')
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

    output_format = ctx_cmd.cli_ctx.config.get('search_scenario', 'output', fallback='status')

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
        print()
        from .utils import print_successful_styled_text
        print_successful_styled_text('command completed\n')

    return exit_code


def _get_command_item_sample(command):
    if "example" in command and command["example"]:
        command_sample, _ = _parse_argument_value_sample(command["example"].replace(" $", " "))
        return command_sample

    from knack import help_files
    parameter = []
    if "arguments" in command and command["arguments"]:
        parameter = command["arguments"]
        sorted_param = sorted(parameter)
        cmd_help = help_files._load_help_file(command['command'])   # pylint: disable=protected-access
        if cmd_help and 'examples' in cmd_help and cmd_help['examples']:
            for cmd_example in cmd_help['examples']:
                command_sample, example_arguments = _parse_argument_value_sample(cmd_example['text'])
                if sorted(example_arguments) == sorted_param:
                    return command_sample

    command = command["command"] if command["command"].startswith("az ") else "az " + command["command"]
    command_sample = f"{command} {' '.join(parameter) if parameter else ''}"
    return [(Style.PRIMARY, command_sample)]


def _parse_argument_value_sample(command_sample):
    if not command_sample:
        return

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
            formatted_example.append((Style.WARNING, ' <' + ' '.join(argument_values[argument]) + '>'))

    return formatted_example, example_arguments


def send_feedback(scope, option, keyword, search_results=None, adoption=None):
    feedback = str(int(scope)) + "#" + str(option) + "#" + \
               keyword.replace("\\", "\\\\").replace("#", "\\sharp") + "#"
    if search_results and isinstance(search_results, list):
        feedback += " ".join(map(lambda r: str(r.get("source", 0)), search_results))
    else:
        feedback += " "
    feedback += "#"
    if adoption:
        feedback += str(adoption.get("source", " ")) + "#" + adoption.get("scenario", " ") + \
            "#" + adoption.get("description", " ").replace("\\",  "\\\\").replace("#", "\\sharp")
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
