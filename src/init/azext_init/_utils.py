# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.style import print_styled_text, Style


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
    print_styled_text([(Style.ACTION, ' ? '), (Style.PRIMARY, option_description)], end='')
    option = input()
    yes_options = ["y", "yes", "Y", "Yes", "YES"]
    no_options = ["n", "no", "N", "No", "NO"]
    while (option not in yes_options) and (option not in no_options):
        option = input("This option can only be Yes or No, please input again: ")
    return option in yes_options


def get_int_option(option_description, min_option, max_option, default_option):
    print_styled_text([(Style.ACTION, ' ? '), (Style.PRIMARY, option_description)], end='')
    option = read_int(default_option)
    while option < min_option or option > max_option:
        print_styled_text([Style.PRIMARY, "Please enter a valid option ({}-{}): ".format(min_option, max_option)],
                          end='')
        option = read_int(default_option)
    return option


def print_successful_styled_text(message):
    from azure.cli.core.style import is_modern_terminal

    prefix_text = '\nDone: '
    if is_modern_terminal():
        prefix_text = '\n(✓ )Done: '
    print_styled_text([(Style.SUCCESS, prefix_text), (Style.PRIMARY, message)])


def prompt_option_list(option_list):

    if not option_list or not isinstance(option_list, list):
        return

    for index, choice_item in enumerate(option_list):
        if 'name' not in choice_item or not choice_item['name']:
            continue
        print_styled_text([(Style.ACTION, "[" + str(index) + "] "), (Style.PRIMARY, choice_item['name'])])

        if 'secondary' in choice_item and choice_item['secondary']:
            print_styled_text([(Style.PRIMARY, '    '), (Style.SECONDARY, choice_item['secondary'])])

        print()
