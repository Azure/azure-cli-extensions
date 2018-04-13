# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
import shlex

from knack.util import CLIError

import azext_alias
from azext_alias.argument import get_placeholders
from azext_alias.util import (
    get_config_parser,
    is_url,
    reduce_alias_table,
    filter_alias_create_namespace,
    retrieve_file_from_url
)
from azext_alias._const import (
    COLLISION_CHECK_LEVEL_DEPTH,
    INVALID_ALIAS_COMMAND_ERROR,
    EMPTY_ALIAS_ERROR,
    INVALID_STARTING_CHAR_ERROR,
    INCONSISTENT_ARG_ERROR,
    COMMAND_LVL_ERROR,
    CONFIG_PARSING_ERROR,
    ALIAS_FILE_NOT_FOUND_ERROR,
    ALIAS_FILE_DIR_ERROR,
    FILE_ALREADY_EXISTS_ERROR,
    ALIAS_FILE_NAME
)
from azext_alias.alias import AliasManager


def process_alias_create_namespace(namespace):
    """
    Validate input arguments when the user invokes 'az alias create'.

    Args:
        namespace: argparse namespace object.
    """
    namespace = filter_alias_create_namespace(namespace)
    _validate_alias_name(namespace.alias_name)
    _validate_alias_command(namespace.alias_command)
    _validate_alias_command_level(namespace.alias_name, namespace.alias_command)
    _validate_pos_args_syntax(namespace.alias_name, namespace.alias_command)


def process_alias_import_namespace(namespace):
    """
    Validate input arguments when the user invokes 'az alias import'.

    Args:
        namespace: argparse namespace object.
    """
    if is_url(namespace.alias_source):
        alias_source = retrieve_file_from_url(namespace.alias_source)

        _validate_alias_file_content(alias_source, url=namespace.alias_source)
    else:
        namespace.alias_source = os.path.abspath(namespace.alias_source)
        _validate_alias_file_path(namespace.alias_source)
        _validate_alias_file_content(namespace.alias_source)


def process_alias_export_namespace(namespace):
    """
    Validate input arguments when the user invokes 'az alias export'.

    Args:
        namespace: argparse namespace object.
    """
    namespace.export_path = os.path.abspath(namespace.export_path)
    if os.path.isfile(namespace.export_path):
        raise CLIError(FILE_ALREADY_EXISTS_ERROR.format(namespace.export_path))

    export_path_dir = os.path.dirname(namespace.export_path)
    if not os.path.isdir(export_path_dir):
        os.makedirs(export_path_dir)

    if os.path.isdir(namespace.export_path):
        namespace.export_path = os.path.join(namespace.export_path, ALIAS_FILE_NAME)


def _validate_alias_name(alias_name):
    """
    Check if the alias name is valid.

    Args:
        alias_name: The name of the alias to validate.
    """
    if not alias_name:
        raise CLIError(EMPTY_ALIAS_ERROR)

    if not re.match('^[a-zA-Z]', alias_name):
        raise CLIError(INVALID_STARTING_CHAR_ERROR.format(alias_name[0]))


def _validate_alias_command(alias_command):
    """
    Check if the alias command is valid.

    Args:
        alias_command: The command to validate.
    """
    if not alias_command:
        raise CLIError(EMPTY_ALIAS_ERROR)

    split_command = shlex.split(alias_command)
    boundary_index = len(split_command)
    for i, subcommand in enumerate(split_command):
        if not re.match('^[a-z]', subcommand.lower()) or i > COLLISION_CHECK_LEVEL_DEPTH:
            boundary_index = i
            break

    # Extract possible CLI commands and validate
    command_to_validate = ' '.join(split_command[:boundary_index]).lower()
    for command in azext_alias.cached_reserved_commands:
        if re.match(r'([a-z\-]*\s)*{}($|\s)'.format(command_to_validate), command):
            return

    _validate_positional_arguments(shlex.split(alias_command))


def _validate_pos_args_syntax(alias_name, alias_command):
    """
    Check if the positional argument syntax is valid in alias name and alias command.

    Args:
        alias_name: The name of the alias to validate.
        alias_command: The command to validate.
    """
    pos_args_from_alias = get_placeholders(alias_name)
    # Split by '|' to extract positional argument name from Jinja filter (e.g. {{ arg_name | upper }})
    # Split by '.' to extract positional argument name from function call (e.g. {{ arg_name.split()[0] }})
    pos_args_from_command = [x.split('|')[0].split('.')[0].strip() for x in get_placeholders(alias_command)]

    if set(pos_args_from_alias) != set(pos_args_from_command):
        arg_diff = set(pos_args_from_alias) ^ set(pos_args_from_command)
        raise CLIError(INCONSISTENT_ARG_ERROR.format('' if len(arg_diff) == 1 else 's',
                                                     arg_diff,
                                                     'is' if len(arg_diff) == 1 else 'are'))


def _validate_alias_command_level(alias, command):
    """
    Make sure that if the alias is a reserved command, the command that the alias points to
    in the command tree does not conflict in levels.

    e.g. 'dns' -> 'network dns' is valid because dns is a level 2 command and network dns starts at level 1.
    However, 'list' -> 'show' is not valid because list and show are both reserved commands at level 2.

    Args:
        alias: The name of the alias.
        command: The command that the alias points to.
    """
    alias_collision_table = AliasManager.build_collision_table([alias])

    # Alias is not a reserved command, so it can point to any command
    if not alias_collision_table:
        return

    command_collision_table = AliasManager.build_collision_table([command])
    alias_collision_levels = alias_collision_table.get(alias.split()[0], [])
    command_collision_levels = command_collision_table.get(command.split()[0], [])

    # Check if there is a command level conflict
    if set(alias_collision_levels) & set(command_collision_levels):
        raise CLIError(COMMAND_LVL_ERROR.format(alias, command))


def _validate_alias_file_path(alias_file_path):
    """
    Make sure the alias file path is neither non-existant nor a directory

    Args:
        The alias file path to import aliases from.
    """
    if not os.path.exists(alias_file_path):
        raise CLIError(ALIAS_FILE_NOT_FOUND_ERROR)

    if os.path.isdir(alias_file_path):
        raise CLIError(ALIAS_FILE_DIR_ERROR.format(alias_file_path))


def _validate_alias_file_content(alias_file_path, url=''):
    """
    Make sure the alias name and alias command in the alias file is in valid format.

    Args:
        The alias file path to import aliases from.
    """
    alias_table = get_config_parser()
    try:
        alias_table.read(alias_file_path)
        for alias_name, alias_command in reduce_alias_table(alias_table):
            _validate_alias_name(alias_name)
            _validate_alias_command(alias_command)
            _validate_alias_command_level(alias_name, alias_command)
            _validate_pos_args_syntax(alias_name, alias_command)
    except Exception as exception:  # pylint: disable=broad-except
        error_msg = CONFIG_PARSING_ERROR % AliasManager.process_exception_message(exception)
        error_msg = error_msg.replace(alias_file_path, url or alias_file_path)
        raise CLIError(error_msg)


def _validate_positional_arguments(args):
    """
    To validate the positional argument feature - https://github.com/Azure/azure-cli/pull/6055.
    Assuming that unknown commands are positional arguments immediately
    led by words that only appear at the end of the commands

    Slight modification of
    https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/commands/__init__.py#L356-L373

    Args:
        args: The arguments that the user inputs in the terminal.

    Returns:
        Rudimentary parsed arguments.
    """
    nouns = []
    for arg in args:
        if not arg.startswith('-') or not arg.startswith('{{'):
            nouns.append(arg)
        else:
            break

    while nouns:
        search = ' '.join(nouns)
        # Since the command name may be immediately followed by a positional arg, strip those off
        if not next((x for x in azext_alias.cached_reserved_commands if x.endswith(search)), False):
            del nouns[-1]
        else:
            return

    raise CLIError(INVALID_ALIAS_COMMAND_ERROR.format(' '.join(args)))
