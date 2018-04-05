# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import sys
import shlex
from six.moves import configparser

import azext_alias
from azext_alias._const import COLLISION_CHECK_LEVEL_DEPTH


def get_config_parser():
    """
    Disable configparser's interpolation function and return an instance of config parser.

    Returns:
        An instance of config parser with interpolation disabled.
    """
    if sys.version_info.major == 3:
        return configparser.ConfigParser(interpolation=None)  # pylint: disable=unexpected-keyword-arg
    return configparser.ConfigParser()  # pylint: disable=undefined-variable


def get_alias_table():
    """
    Get the current alias table.
    """
    try:
        alias_table = get_config_parser()
        alias_table.read(azext_alias.alias.GLOBAL_ALIAS_PATH)
        return alias_table
    except Exception:  # pylint: disable=broad-except
        return get_config_parser()


def is_alias_create_command(args):
    """
    Check if the user is invoking 'az alias create'.

    Returns:
        True if the user is invoking 'az alias create'.
    """
    return args and args[:2] == ['alias', 'create']


def cache_reserved_commands(load_cmd_tbl_func):
    """
    We don't have access to load_cmd_tbl_func in custom.py (need the entire command table
    for alias and command validation when the user invokes alias create).
    This cache saves the entire command table globally so custom.py can have access to it.
    Alter this cache through cache_reserved_commands(load_cmd_tbl_func) in util.py.
    """
    if not azext_alias.cached_reserved_commands:
        azext_alias.cached_reserved_commands = list(load_cmd_tbl_func([]).keys())


def remove_pos_arg_placeholders(alias_command):
    """
    Remove positional argument placeholders from alias_command.

    Args:
        alias_command: The alias command to remove from.
    """
    # Boundary index is the index at which named argument or positional argument starts
    split_command = shlex.split(alias_command)
    boundary_index = len(split_command)
    for i, subcommand in enumerate(split_command):
        if not re.match('^[a-z]', subcommand.lower()) or i > COLLISION_CHECK_LEVEL_DEPTH:
            boundary_index = i
            break

    return ' '.join(split_command[:boundary_index]).lower()
