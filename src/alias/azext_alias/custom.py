# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import hashlib

from knack.util import CLIError
from knack.log import get_logger

from azext_alias._const import ALIAS_NOT_FOUND_ERROR, POST_EXPORT_ALIAS_MSG, ALIAS_FILE_NAME
from azext_alias.alias import GLOBAL_ALIAS_PATH, AliasManager
from azext_alias.util import (
    get_alias_table,
    is_url,
    build_tab_completion_table,
    get_config_parser,
    retrieve_file_from_url
)

logger = get_logger(__name__)


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


def export_aliases(export_path=os.path.abspath(ALIAS_FILE_NAME), exclusions=None):
    """
    Export all registered aliases to a given path, as an INI configuration file.

    Args:
        export_path: The path of the alias configuration file to export to.
        exclusions: Space-separated aliases excluded from export.
    """
    alias_table = get_alias_table()
    for exclusion in exclusions or []:
        if exclusion not in alias_table.sections():
            raise CLIError(ALIAS_NOT_FOUND_ERROR.format(exclusion))
        alias_table.remove_section(exclusion)

    _commit_change(alias_table, export_path=export_path, post_commit=False)
    logger.warning(POST_EXPORT_ALIAS_MSG, export_path)  # pylint: disable=superfluous-parens


def import_aliases(alias_source):
    """
    Import aliases from a file or an URL.

    Args:
        alias_source: The source of the alias. It can be a filepath or an URL.
    """
    alias_table = get_alias_table()
    if is_url(alias_source):
        alias_source = retrieve_file_from_url(alias_source)
        alias_table.read(alias_source)
        os.remove(alias_source)
    else:
        alias_table.read(alias_source)
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


def remove_alias(alias_names):
    """
    Remove an alias.

    Args:
        alias_name: The name of the alias to be removed.
    """
    alias_table = get_alias_table()
    for alias_name in alias_names:
        if alias_name not in alias_table.sections():
            raise CLIError(ALIAS_NOT_FOUND_ERROR.format(alias_name))
        alias_table.remove_section(alias_name)
    _commit_change(alias_table)


def remove_all_aliases():
    """
    Remove all registered aliases.
    """
    _commit_change(get_config_parser())


def _commit_change(alias_table, export_path=None, post_commit=True):
    """
    Record changes to the alias table.
    Also write new alias config hash and collided alias, if any.

    Args:
        alias_table: The alias table to commit.
        export_path: The path to export the aliases to. Default: GLOBAL_ALIAS_PATH.
        post_commit: True if we want to perform some extra actions after writing alias to file.
    """
    with open(export_path or GLOBAL_ALIAS_PATH, 'w+') as alias_config_file:
        alias_table.write(alias_config_file)
        if post_commit:
            alias_config_file.seek(0)
            alias_config_hash = hashlib.sha1(alias_config_file.read().encode('utf-8')).hexdigest()
            AliasManager.write_alias_config_hash(alias_config_hash)
            collided_alias = AliasManager.build_collision_table(alias_table.sections())
            AliasManager.write_collided_alias(collided_alias)
            build_tab_completion_table(alias_table)
