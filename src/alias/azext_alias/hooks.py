# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import timeit

from knack.log import get_logger

from azure.cli.command_modules.interactive.azclishell.command_tree import CommandBranch
from azext_alias import telemetry
from azext_alias.alias import AliasManager
from azext_alias.util import (
    is_alias_create_command,
    cache_reserved_commands,
    get_alias_table,
    remove_pos_arg_placeholders
)
from azext_alias._const import DEBUG_MSG_WITH_TIMING

logger = get_logger(__name__)


def alias_event_handler(_, **kwargs):
    """
    An event handler for alias transformation when EVENT_INVOKER_PRE_TRUNCATE_CMD_TBL event is invoked.
    """
    try:
        telemetry.start()

        start_time = timeit.default_timer()
        args = kwargs.get('args')
        alias_manager = AliasManager(**kwargs)

        # [:] will keep the reference of the original args
        args[:] = alias_manager.transform(args)

        if is_alias_create_command(args):
            load_cmd_tbl_func = kwargs.get('load_cmd_tbl_func', lambda _: {})
            cache_reserved_commands(load_cmd_tbl_func)

        elapsed_time = (timeit.default_timer() - start_time) * 1000
        logger.debug(DEBUG_MSG_WITH_TIMING, args, elapsed_time)

        telemetry.set_execution_time(round(elapsed_time, 2))
    except Exception as client_exception:  # pylint: disable=broad-except
        telemetry.set_exception(client_exception)
        raise
    finally:
        telemetry.conclude()


def enable_aliases_autocomplete(_, **kwargs):
    """
    Enable aliases autocomplete by injecting aliases into Azure CLI tab completion list.
    """
    parser = kwargs.get('parser', None)
    if not parser:
        return

    external_completions = kwargs.get('external_completions', [])
    prefix = kwargs.get('cword_prefix', [])
    cur_commands = kwargs.get('comp_words', [])
    alias_table = get_alias_table()
    # Transform aliases if they are in current commands,
    # so parser can get the correct subparser when chaining aliases
    _transform_cur_commands(cur_commands, alias_table=alias_table)

    for alias, alias_command in _filter_aliases(alias_table):
        if alias.startswith(prefix) and alias.strip() != prefix and \
            _is_autocomplete_valid(parser, cur_commands, alias_command):
            # Only autocomplete the first word because alias is space-delimited
            external_completions.append(alias)

    # Append spaces if necessary (https://github.com/kislyuk/argcomplete/blob/master/argcomplete/__init__.py#L552-L559)
    prequote = kwargs.get('cword_prequote', '')
    continuation_chars = "=/:"
    if len(external_completions) == 1 and external_completions[0][-1] not in continuation_chars and not prequote:
        external_completions[0] += ' '


def transform_cur_commands_interactive(_, **kwargs):
    """
    Transform any aliases in current commands in interactive into their respective commands.
    """
    event_payload = kwargs.get('event_payload', {})
    # text_split = current commands typed in the interactive shell without any unfinished word
    # text = current commands typed in the interactive shell
    cur_commands = event_payload.get('text', '').split(' ')
    _transform_cur_commands(cur_commands)

    event_payload.update({
        'text': ' '.join(cur_commands)
    })


def enable_aliases_autocomplete_interactive(_, **kwargs):
    """
    Enable aliases autocomplete on interactive mode by injecting aliases in the command tree.
    """
    subtree = kwargs.get('subtree', None)
    if not subtree or not hasattr(subtree, 'children'):
        return

    for alias, alias_command in _filter_aliases(get_alias_table()):
        # Only autocomplete the first word because alias is space-delimited
        if subtree.in_tree(alias_command.split()):
            subtree.add_child(CommandBranch(alias))


def _is_autocomplete_valid(parser, cur_commands, alias_command):
    """
    Determine whether autocomplete can be performed at the current state.

    Args:
        parser: The current CLI parser.
        cur_commands: The current commands typed in the console.
        alias_command: The alias command.

    Returns:
        True if autocomplete can be performed.
    """
    # Remove the first word because comp_words always start with 'az'
    cur_command_tuple = tuple(cur_commands[1:])

    if cur_command_tuple not in parser.subparsers:
        return False
    elif cur_command_tuple == ():
        # Autocomplete is always valid for first-level command
        # because there is no need to check its subparser
        return True

    subparser = parser.subparsers[cur_command_tuple]
    # Check if alias_command is a valid command under the subparser
    # Only check the first word due to limitations of subparser
    return alias_command.split()[0] in subparser.choices


def _transform_cur_commands(cur_commands, alias_table=None):
    """
    Transform any aliases in cur_commands into their respective commands.

    Args:
        alias_table: The alias table.
        cur_commands: current commands typed in the console.
    """
    transformed = []
    alias_table = alias_table if alias_table else get_alias_table()
    for cmd in cur_commands:
        if cmd in alias_table.sections() and alias_table.has_option(cmd, 'command'):
            transformed += alias_table.get(cmd, 'command').split()
        else:
            transformed.append(cmd)
    cur_commands[:] = transformed


def _filter_aliases(alias_table):
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
