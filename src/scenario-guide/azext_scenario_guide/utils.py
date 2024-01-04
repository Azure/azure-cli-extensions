# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.style import print_styled_text, Style, is_modern_terminal


def input_int(default_value=0):
    """Read an int from `stdin`. Retry if input is not a number"""
    ret = input()
    if ret == '' or ret is None:
        return default_value
    while not ret.isnumeric():
        ret = input("Please input a valid number: ")
        if ret == '' or ret is None:
            return default_value
    return int(ret)


def select_option(option_msg, min_option, max_option, default_option):
    """Read an option from `stdin` ranging from `min_option` to `max_option`.
    Retry if input is out of range.
    """
    print_styled_text(option_msg, end='')
    option = input_int(default_option)
    while option < min_option or option > max_option:
        print_styled_text([(Style.PRIMARY, f"Please enter a valid option ({min_option}-{max_option}): ")],
                          end='')
        option = input_int(default_option)
    return option


def print_successful_styled_text(message):
    prefix_text = 'Done: '
    if is_modern_terminal():
        prefix_text = '(✓) Done: '
    print_styled_text([(Style.SUCCESS, prefix_text), (Style.PRIMARY, message)])
