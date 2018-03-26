# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import shlex
import hashlib

from knack.util import CLIError

from azext_alias import AliasCache
from azext_alias.argument import get_placeholders
from azext_alias._const import (
    COLLISION_CHECK_LEVEL_DEPTH,
    ALIAS_NOT_FOUND_ERROR,
    INVALID_ALIAS_COMMAND_ERROR,
    EMPTY_ALIAS_ERROR,
    INVALID_STARTING_CHAR_ERROR,
    INCONSISTENT_ARG_ERROR,
    COMMAND_LVL_ERROR
)
from azext_alias.alias import (
    GLOBAL_ALIAS_PATH,
    get_config_parser,
    AliasManager
)


def create_alias(alias_name, alias_command):
    """
    Create an alias.

    Args:
        alias_name: The name of the alias.
        alias_command: The command that the alias points to.
    """
    alias_name, alias_command = alias_name.strip(), alias_command.strip()
    _validate_alias_name(alias_name)
    _validate_alias_command(alias_command)
    _validate_alias_command_level(alias_name, alias_command)
    _validate_pos_args_syntax(alias_name, alias_command)

    alias_table = _get_alias_table()
    if alias_name not in alias_table.sections():
        alias_table.add_section(alias_name)
    alias_table.set(alias_name, 'command', alias_command)
    _commit_change(alias_table)


def list_alias():
    """
    List all registered aliases.

    Returns:
        An array of  dictionary containing the alias and the command that it points to.
    """
    alias_table = _get_alias_table()
    output = []
    for alias in alias_table.sections():
        if alias_table.has_option(alias, 'command'):
            output.append({
                'alias': alias,
                # Remove unnecessary whitespaces
                'command': ' '.join(alias_table.get(alias, 'command').split())
            })

    return output


def remove_alias(alias_name):
    """
    Remove an alias.

    Args:
        alias_name: The name of the alias to be removed.
    """
    alias_table = _get_alias_table()
    if alias_name not in alias_table.sections():
        raise CLIError(ALIAS_NOT_FOUND_ERROR.format(alias_name))
    alias_table.remove_section(alias_name)
    _commit_change(alias_table)


def _get_alias_table():
    """
    Get the current alias table.
    """
    try:
        alias_table = get_config_parser()
        alias_table.read(GLOBAL_ALIAS_PATH)
        return alias_table
    except Exception:  # pylint: disable=broad-except
        # Exception is being handled by self.load_alias_table in alias.py
        # so simply raise an empty CLIError to terminate all actions
        raise CLIError()


def _commit_change(alias_table):
    """
    Record changes to the alias table.
    Also write new alias config hash and collided alias, if any.

    Args:
        alias_table: The alias table to commit.
    """
    with open(GLOBAL_ALIAS_PATH, 'w+') as alias_config_file:
        alias_table.write(alias_config_file)
        alias_config_file.seek(0)
        alias_config_hash = hashlib.sha1(alias_config_file.read().encode('utf-8')).hexdigest()
        AliasManager.write_alias_config_hash(alias_config_hash)

    collided_alias = AliasManager.build_collision_table(alias_table.sections(), AliasCache.reserved_commands)
    AliasManager.write_collided_alias(collided_alias)


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

    # Boundary index is the index at which named argument or positional argument starts
    split_command = shlex.split(alias_command)
    boundary_index = len(split_command)
    for i, subcommand in enumerate(split_command):
        if not re.match('^[a-z]', subcommand.lower()) or i > COLLISION_CHECK_LEVEL_DEPTH:
            boundary_index = i
            break

    # Extract possible CLI commands and validate
    command_to_validate = ' '.join(split_command[:boundary_index]).lower()
    for command in AliasCache.reserved_commands:
        if re.match(r'([a-z\-]*\s)*{}($|\s)'.format(command_to_validate), command):
            return

    raise CLIError(INVALID_ALIAS_COMMAND_ERROR.format(command_to_validate if command_to_validate else alias_command))


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
    alias_collision_table = AliasManager.build_collision_table([alias], AliasCache.reserved_commands)

    # Alias is not a reserved command, so it can point to any command
    if not alias_collision_table:
        return

    command_collision_table = AliasManager.build_collision_table([command], AliasCache.reserved_commands)
    alias_collision_levels = alias_collision_table.get(alias.split()[0], [])
    command_collision_levels = command_collision_table.get(command.split()[0], [])

    # Check if there is a command level conflict
    if set(alias_collision_levels) & set(command_collision_levels):
        raise CLIError(COMMAND_LVL_ERROR.format(alias, command))
