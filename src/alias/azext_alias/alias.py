# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
import json
import shlex
import hashlib
from collections import defaultdict

from knack.log import get_logger

import azext_alias
from azext_alias import telemetry
from azext_alias._const import (
    GLOBAL_CONFIG_DIR,
    ALIAS_FILE_NAME,
    ALIAS_HASH_FILE_NAME,
    COLLIDED_ALIAS_FILE_NAME,
    CONFIG_PARSING_ERROR,
    DEBUG_MSG,
    COLLISION_CHECK_LEVEL_DEPTH,
    POS_ARG_DEBUG_MSG
)
from azext_alias.argument import build_pos_args_table, render_template
from azext_alias.util import (
    is_alias_create_command,
    cache_reserved_commands,
    get_config_parser,
    build_tab_completion_table
)


GLOBAL_ALIAS_PATH = os.path.join(GLOBAL_CONFIG_DIR, ALIAS_FILE_NAME)
GLOBAL_ALIAS_HASH_PATH = os.path.join(GLOBAL_CONFIG_DIR, ALIAS_HASH_FILE_NAME)
GLOBAL_COLLIDED_ALIAS_PATH = os.path.join(GLOBAL_CONFIG_DIR, COLLIDED_ALIAS_FILE_NAME)

logger = get_logger(__name__)


class AliasManager(object):

    def __init__(self, **kwargs):
        self.alias_table = get_config_parser()
        self.kwargs = kwargs
        self.collided_alias = defaultdict(list)
        self.alias_config_str = ''
        self.alias_config_hash = ''
        self.load_alias_table()
        self.load_alias_hash()

    def load_alias_table(self):
        """
        Load (create, if not exist) the alias config file.
        """
        try:
            # w+ creates the alias config file if it does not exist
            open_mode = 'r+' if os.path.exists(GLOBAL_ALIAS_PATH) else 'w+'
            with open(GLOBAL_ALIAS_PATH, open_mode) as alias_config_file:
                self.alias_config_str = alias_config_file.read()
            self.alias_table.read(GLOBAL_ALIAS_PATH)
            telemetry.set_number_of_aliases_registered(len(self.alias_table.sections()))
        except Exception as exception:  # pylint: disable=broad-except
            logger.warning(CONFIG_PARSING_ERROR, AliasManager.process_exception_message(exception))
            self.alias_table = get_config_parser()
            telemetry.set_exception(exception)

    def load_alias_hash(self):
        """
        Load (create, if not exist) the alias hash file.
        """
        # w+ creates the alias hash file if it does not exist
        open_mode = 'r+' if os.path.exists(GLOBAL_ALIAS_HASH_PATH) else 'w+'
        with open(GLOBAL_ALIAS_HASH_PATH, open_mode) as alias_config_hash_file:
            self.alias_config_hash = alias_config_hash_file.read()

    def load_collided_alias(self):
        """
        Load (create, if not exist) the collided alias file.
        """
        # w+ creates the alias config file if it does not exist
        open_mode = 'r+' if os.path.exists(GLOBAL_COLLIDED_ALIAS_PATH) else 'w+'
        with open(GLOBAL_COLLIDED_ALIAS_PATH, open_mode) as collided_alias_file:
            collided_alias_str = collided_alias_file.read()
            try:
                self.collided_alias = json.loads(collided_alias_str if collided_alias_str else '{}')
            except Exception:  # pylint: disable=broad-except
                self.collided_alias = {}

    def detect_alias_config_change(self):
        """
        Change if the alias configuration has changed since the last run.

        Returns:
            False if the alias configuration file has not been changed since the last run.
            Otherwise, return True.
        """
        # Do not load the entire command table if there is a parse error
        if self.parse_error():
            return False

        alias_config_sha1 = hashlib.sha1(self.alias_config_str.encode('utf-8')).hexdigest()
        if alias_config_sha1 != self.alias_config_hash:
            # Overwrite the old hash with the new one
            self.alias_config_hash = alias_config_sha1
            return True
        return False

    def transform(self, args):
        """
        Transform any aliases in args to their respective commands.

        Args:
            args: A list of space-delimited command input extracted directly from the console.

        Returns:
            A list of transformed commands according to the alias configuration file.
        """
        if self.parse_error():
            # Write an empty hash so next run will check the config file against the entire command table again
            AliasManager.write_alias_config_hash(empty_hash=True)
            return args

        # Only load the entire command table if it detects changes in the alias config
        if self.detect_alias_config_change():
            self.load_full_command_table()
            self.collided_alias = AliasManager.build_collision_table(self.alias_table.sections())
            build_tab_completion_table(self.alias_table)
        else:
            self.load_collided_alias()

        transformed_commands = []
        alias_iter = enumerate(args, 1)
        for alias_index, alias in alias_iter:
            is_collided_alias = alias in self.collided_alias and alias_index in self.collided_alias[alias]
            # Check if the current alias is a named argument
            # index - 2 because alias_iter starts counting at index 1
            is_named_arg = alias_index > 1 and args[alias_index - 2].startswith('-')
            is_named_arg_flag = alias.startswith('-')
            if not alias or is_collided_alias or is_named_arg or is_named_arg_flag:
                transformed_commands.append(alias)
                continue

            full_alias = self.get_full_alias(alias)

            if self.alias_table.has_option(full_alias, 'command'):
                cmd_derived_from_alias = self.alias_table.get(full_alias, 'command')
                telemetry.set_alias_hit(full_alias)
            else:
                transformed_commands.append(alias)
                continue

            pos_args_table = build_pos_args_table(full_alias, args, alias_index)
            if pos_args_table:
                logger.debug(POS_ARG_DEBUG_MSG, full_alias, cmd_derived_from_alias, pos_args_table)
                transformed_commands += render_template(cmd_derived_from_alias, pos_args_table)

                # Skip the next arg(s) because they have been already consumed as a positional argument above
                for pos_arg in pos_args_table:  # pylint: disable=unused-variable
                    next(alias_iter)
            else:
                logger.debug(DEBUG_MSG, full_alias, cmd_derived_from_alias)
                transformed_commands += shlex.split(cmd_derived_from_alias)

        return self.post_transform(transformed_commands)

    def get_full_alias(self, query):
        """
        Get the full alias given a search query.

        Args:
            query: The query this function performs searching on.

        Returns:
            The full alias (with the placeholders, if any).
        """
        if query in self.alias_table.sections():
            return query

        return next((section for section in self.alias_table.sections() if section.split()[0] == query), '')

    def load_full_command_table(self):
        """
        Perform a full load of the command table to get all the reserved command words.
        """
        load_cmd_tbl_func = self.kwargs.get('load_cmd_tbl_func', lambda _: {})
        cache_reserved_commands(load_cmd_tbl_func)
        telemetry.set_full_command_table_loaded()

    def post_transform(self, args):
        """
        Inject environment variables, and write hash to alias hash file after transforming alias to commands.

        Args:
            args: A list of args to post-transform.
        """
        # Ignore 'az' if it is the first command
        args = args[1:] if args and args[0] == 'az' else args

        post_transform_commands = []
        for i, arg in enumerate(args):
            # Do not translate environment variables for command argument
            if is_alias_create_command(args) and i > 0 and args[i - 1] in ['-c', '--command']:
                post_transform_commands.append(arg)
            else:
                post_transform_commands.append(os.path.expandvars(arg))

        AliasManager.write_alias_config_hash(self.alias_config_hash)
        AliasManager.write_collided_alias(self.collided_alias)

        return post_transform_commands

    def parse_error(self):
        """
        Check if there is a configuration parsing error.

        A parsing error has occurred if there are strings inside the alias config file
        but there is no alias loaded in self.alias_table.

        Returns:
            True if there is an error parsing the alias configuration file. Otherwises, false.
        """
        return not self.alias_table.sections() and self.alias_config_str

    @staticmethod
    def build_collision_table(aliases, levels=COLLISION_CHECK_LEVEL_DEPTH):
        """
        Build the collision table according to the alias configuration file against the entire command table.

        self.collided_alias is structured as:
        {
            'collided_alias': [the command level at which collision happens]
        }
        For example:
        {
            'account': [1, 2]
        }
        This means that 'account' is a reserved command in level 1 and level 2 of the command tree because
        (az account ...) and (az storage account ...)
             lvl 1                        lvl 2

        Args:
            levels: the amount of levels we tranverse through the command table tree.
        """
        collided_alias = defaultdict(list)
        for alias in aliases:
            # Only care about the first word in the alias because alias
            # cannot have spaces (unless they have positional arguments)
            word = alias.split()[0]
            for level in range(1, levels + 1):
                collision_regex = r'^{}{}($|\s)'.format(r'([a-z\-]*\s)' * (level - 1), word.lower())
                if list(filter(re.compile(collision_regex).match, azext_alias.cached_reserved_commands)) \
                        and level not in collided_alias[word]:
                    collided_alias[word].append(level)

        telemetry.set_collided_aliases(list(collided_alias.keys()))
        return collided_alias

    @staticmethod
    def write_alias_config_hash(alias_config_hash='', empty_hash=False):
        """
        Write self.alias_config_hash to the alias hash file.

        Args:
            empty_hash: True if we want to write an empty string into the file. Empty string in the alias hash file
                means that we have to perform a full load of the command table in the next run.
        """
        with open(GLOBAL_ALIAS_HASH_PATH, 'w') as alias_config_hash_file:
            alias_config_hash_file.write('' if empty_hash else alias_config_hash)

    @staticmethod
    def write_collided_alias(collided_alias_dict):
        """
        Write the collided aliases string into the collided alias file.
        """
        # w+ creates the alias config file if it does not exist
        open_mode = 'r+' if os.path.exists(GLOBAL_COLLIDED_ALIAS_PATH) else 'w+'
        with open(GLOBAL_COLLIDED_ALIAS_PATH, open_mode) as collided_alias_file:
            collided_alias_file.truncate()
            collided_alias_file.write(json.dumps(collided_alias_dict))

    @staticmethod
    def process_exception_message(exception):
        """
        Process an exception message.

        Args:
            exception: The exception to process.

        Returns:
            A filtered string summarizing the exception.
        """
        exception_message = str(exception)
        for replace_char in ['\t', '\n', '\\n']:
            exception_message = exception_message.replace(replace_char, '' if replace_char != '\t' else ' ')
        return exception_message.replace('section', 'alias')
