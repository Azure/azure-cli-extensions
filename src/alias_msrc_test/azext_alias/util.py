# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order,import-error,relative-import

import re
import sys
import json
import shlex
from collections import defaultdict
from six.moves import configparser
from six.moves.urllib.parse import urlparse
from six.moves.urllib.request import urlretrieve

from knack.util import CLIError

import azext_alias
from azext_alias._const import COLLISION_CHECK_LEVEL_DEPTH, GLOBAL_ALIAS_TAB_COMP_TABLE_PATH, ALIAS_FILE_URL_ERROR


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


def is_alias_command(subcommands, args):
    """
    Check if the user is invoking one of the comments in 'subcommands' in the  from az alias .

    Args:
        subcommands: The list of subcommands to check through.
        args: The CLI arguments to process.

    Returns:
        True if the user is invoking 'az alias {command}'.
    """
    if not args:
        return False

    for subcommand in subcommands:
        if args[:2] == ['alias', subcommand]:
            return True

    return False


def cache_reserved_commands(load_cmd_tbl_func):
    """
    We don't have access to load_cmd_tbl_func in custom.py (need the entire command table
    for alias and command validation when the user invokes alias create).
    This cache saves the entire command table globally so custom.py can have access to it.
    Alter this cache through cache_reserved_commands(load_cmd_tbl_func) in util.py.

    Args:
        load_cmd_tbl_func: The function to load the entire command table.
    """
    if not azext_alias.cached_reserved_commands:
        azext_alias.cached_reserved_commands = list(load_cmd_tbl_func([]).keys())


def remove_pos_arg_placeholders(alias_command):
    """
    Remove positional argument placeholders from alias_command.

    Args:
        alias_command: The alias command to remove from.

    Returns:
        The alias command string without positional argument placeholder.
    """
    # Boundary index is the index at which named argument or positional argument starts
    split_command = shlex.split(alias_command)
    boundary_index = len(split_command)
    for i, subcommand in enumerate(split_command):
        if not re.match('^[a-z]', subcommand.lower()) or i > COLLISION_CHECK_LEVEL_DEPTH:
            boundary_index = i
            break

    return ' '.join(split_command[:boundary_index]).lower()


def filter_aliases(alias_table):
    """
    Filter aliases that does not have a command field in the configuration file.

    Args:
        alias_table: The alias table.

    Yield:
        A tuple with [0] being the first word of the alias and
        [1] being the command that the alias points to.
    """
    for alias in alias_table.sections():
        if alias_table.has_option(alias, 'command'):
            yield (alias.split()[0], remove_pos_arg_placeholders(alias_table.get(alias, 'command')))


def build_tab_completion_table(alias_table):
    """
    Build a dictionary where the keys are all the alias commands (without positional argument placeholders)
    and the values are all the parent commands of the keys. After that, write the table into a file.
    The purpose of the dictionary is to validate the alias tab completion state.

    For example:
    {
        "group": ["", "ad"],
        "dns": ["network"]
    }

    Args:
        alias_table: The alias table.

    Returns:
        The tab completion table.
    """
    alias_commands = [t[1] for t in filter_aliases(alias_table)]
    tab_completion_table = defaultdict(list)
    for alias_command in alias_commands:
        for reserved_command in azext_alias.cached_reserved_commands:
            # Check if alias_command has no parent command
            if reserved_command == alias_command or reserved_command.startswith(alias_command + ' ') \
                    and '' not in tab_completion_table[alias_command]:
                tab_completion_table[alias_command].append('')
            elif ' {} '.format(alias_command) in reserved_command or reserved_command.endswith(' ' + alias_command):
                # Extract parent commands
                index = reserved_command.index(alias_command)
                parent_command = reserved_command[:index - 1]
                if parent_command not in tab_completion_table[alias_command]:
                    tab_completion_table[alias_command].append(parent_command)

    with open(GLOBAL_ALIAS_TAB_COMP_TABLE_PATH, 'w') as f:
        f.write(json.dumps(tab_completion_table))

    return tab_completion_table


def is_url(s):
    """
    Check if the argument is an URL.

    Returns:
        True if the argument is an URL.
    """
    return urlparse(s).scheme in ('http', 'https')


def reduce_alias_table(alias_table):
    """
    Reduce the alias table to a tuple that contains the alias and the command that the alias points to.

    Args:
        The alias table to be reduced.

    Yields
        A tuple that contains the alias and the command that the alias points to.
    """
    for alias in alias_table.sections():
        if alias_table.has_option(alias, 'command'):
            yield (alias, alias_table.get(alias, 'command'))


def retrieve_file_from_url(url):
    """
    Retrieve a file from an URL

    Args:
        url: The URL to retrieve the file from.

    Returns:
        The absolute path of the downloaded file.
    """
    try:
        alias_source, _ = urlretrieve(url)
        # Check for HTTPError in Python 2.x
        with open(alias_source, 'r') as f:
            content = f.read()
            if content[:3].isdigit():
                raise CLIError(ALIAS_FILE_URL_ERROR.format(url, content.strip()))
    except Exception as exception:
        if isinstance(exception, CLIError):
            raise

        # Python 3.x
        raise CLIError(ALIAS_FILE_URL_ERROR.format(url, exception))

    return alias_source


def filter_alias_create_namespace(namespace):
    """
    Filter alias name and alias command inside alias create namespace to appropriate strings.

    Args
        namespace: The alias create namespace.

    Returns:
        Filtered namespace where excessive whitespaces are removed in strings.
    """
    def filter_string(s):
        return ' '.join(s.strip().split())

    namespace.alias_name = filter_string(namespace.alias_name)
    namespace.alias_command = filter_string(namespace.alias_command)
    return namespace
