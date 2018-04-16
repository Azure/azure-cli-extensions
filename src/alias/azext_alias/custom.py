# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import hashlib

from knack.util import CLIError

from azext_alias._const import ALIAS_NOT_FOUND_ERROR
from azext_alias.alias import GLOBAL_ALIAS_PATH, AliasManager
from azext_alias.util import get_alias_table, build_tab_completion_table


def create_alias(alias_name, alias_command):
    """
    Create an alias.

    Args:
        alias_name: The name of the alias.
        alias_command: The command that the alias points to.
    """
    alias_name, alias_command = alias_name.strip(), alias_command.strip()
    alias_table = get_alias_table()
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
    alias_table = get_alias_table()
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
    alias_table = get_alias_table()
    if alias_name not in alias_table.sections():
        raise CLIError(ALIAS_NOT_FOUND_ERROR.format(alias_name))
    alias_table.remove_section(alias_name)
    _commit_change(alias_table)


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

    collided_alias = AliasManager.build_collision_table(alias_table.sections())
    AliasManager.write_collided_alias(collided_alias)
    build_tab_completion_table(alias_table)
