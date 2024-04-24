# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import sys
import struct
import platform

from knack.log import get_logger
from azure.cli.core.style import print_styled_text, Style

logger = get_logger(__name__)


def get_window_dim():
    """ gets the dimensions depending on python version and os"""
    version = sys.version_info

    if version >= (3, 3):
        return _size_36()
    if platform.system() == 'Windows':
        return _size_windows()
    return _size_27()


def _size_27():
    """ works for python """
    from subprocess import check_output
    lines = check_output(['tput', 'lines'])
    cols = check_output(['tput', 'cols'])
    return lines, cols


def _size_36():
    """ returns the rows, columns of terminal """
    from shutil import get_terminal_size
    dim = get_terminal_size()
    if isinstance(dim, list):
        return dim[0], dim[1]
    return dim.lines, dim.columns


def _size_windows():
    from ctypes import windll, create_string_buffer
    # stdin handle is -10
    # stdout handle is -11
    # stderr handle is -12
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    (_, _, _, _, _, left, top, right, bottom, _, _) = struct.unpack("hhhhHhhhhhh", csbi.raw)
    columns = right - left + 1
    lines = bottom - top + 1
    return lines, columns


def parse_quotes(cmd, quotes=True, string=True):
    """ parses quotes """
    import shlex

    try:
        args = shlex.split(cmd) if quotes else cmd.split()
    except ValueError as exception:
        logger.error(exception)
        return []

    return [str(arg) for arg in args] if string else args


def get_os_clear_screen_word():
    """ keyword to clear the screen """
    if platform.system() == 'Windows':
        return 'cls'
    return 'clear'


# funtion to get yes/no option, same as az next
def get_yes_or_no_option(option_msg):
    print_styled_text(option_msg, end='')
    option = input()
    yes_options = ["y", "yes", "Y", "Yes", "YES"]
    no_options = ["n", "no", "N", "No", "NO"]
    while (option not in yes_options) and (option not in no_options):
        option = input("This option can only be Yes or No, please input again: ")
    return option in yes_options


# same with scenario guide
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


# same with scenario guide
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
