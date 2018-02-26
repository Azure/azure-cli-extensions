# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
import hashlib
import json
from six.moves import configparser

from knack.log import get_logger
from knack.util import CLIError

from azext_alias import telemetry
from azext_alias._const import (
    GLOBAL_CONFIG_DIR,
    ALIAS_FILE_NAME,
    ALIAS_HASH_FILE_NAME,
    COLLIDED_ALIAS_FILE_NAME,
    PLACEHOLDER_REGEX,
    INCONSISTENT_INDEXING_ERROR,
    CONFIG_PARSING_ERROR,
    INSUFFICIENT_POS_ARG_ERROR,
    DEBUG_MSG,
    POS_ARG_DEBUG_MSG,
    COLLISION_CHECK_LEVEL_DEPTH
)

GLOBAL_ALIAS_PATH = os.path.join(GLOBAL_CONFIG_DIR, ALIAS_FILE_NAME)
GLOBAL_ALIAS_HASH_PATH = os.path.join(GLOBAL_CONFIG_DIR, ALIAS_HASH_FILE_NAME)
GLOBAL_COLLIDED_ALIAS_PATH = os.path.join(GLOBAL_CONFIG_DIR, COLLIDED_ALIAS_FILE_NAME)

logger = get_logger(__name__)


class AliasManager(object):

    def __init__(self, **kwargs):
        self.alias_table = configparser.ConfigParser()
        self.kwargs = kwargs
        self.collided_alias = dict()
        self.reserved_commands = []
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
            self.alias_table = configparser.ConfigParser()
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
            except Exception:   # pylint: disable=broad-except
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
            self.write_alias_config_hash(True)
            return args

        # Only load the entire command table if it detects changes in the alias config
        if self.detect_alias_config_change():
            self.load_full_command_table()
            self.build_collision_table()
        else:
            self.load_collided_alias()

        transformed_commands = []
        alias_iter = enumerate(args, 1)

        for alias_index, alias in alias_iter:
            # Directly append invalid alias or collided alias
            if not alias or alias[0] == '-' or (alias in self.collided_alias and
                                                alias_index in self.collided_alias[alias]):
                transformed_commands.append(alias)
                continue

            full_alias = self.get_full_alias(alias)
            num_pos_args = AliasManager.count_positional_args(full_alias)

            if self.alias_table.has_option(full_alias, 'command'):
                cmd_derived_from_alias = self.alias_table.get(full_alias, 'command')
                if not num_pos_args:
                    logger.debug(DEBUG_MSG, alias, cmd_derived_from_alias)
                telemetry.set_alias_hit(full_alias)
            else:
                transformed_commands.append(alias)
                continue

            if num_pos_args:
                # Take arguments indexed from alias_index to alias_index + num_pos_args and inject
                # them as positional arguments into the command
                pos_args_iter = AliasManager.pos_args_iter(alias, args, alias_index, num_pos_args)
                pos_arg_debug_msg = POS_ARG_DEBUG_MSG.format(alias, cmd_derived_from_alias)
                for placeholder, pos_arg in pos_args_iter:
                    if placeholder not in full_alias:
                        raise CLIError(INCONSISTENT_INDEXING_ERROR.format(placeholder, full_alias))

                    cmd_derived_from_alias = cmd_derived_from_alias.replace(placeholder, pos_arg)
                    pos_arg_debug_msg += "({}: {}) ".format(placeholder, pos_arg)
                    # Skip the next arg because it has been already consumed as a positional argument above
                    next(alias_iter)
                logger.debug(pos_arg_debug_msg)

            # Invoke split() because the command derived from the alias might contain spaces
            transformed_commands += cmd_derived_from_alias.split()

        return self.post_transform(transformed_commands)

    def build_collision_table(self, levels=COLLISION_CHECK_LEVEL_DEPTH):
        """
        Build the collision table according to the alias configuration file against the entire command table.

        if the word collided with a reserved command. self.collided_alias is structured as:
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
        for alias in self.alias_table.sections():
            # Only care about the first word in the alias because alias
            # cannot have spaces (unless they have positional arguments)
            word = alias.split()[0]
            for level in range(1, levels + 1):
                collision_regex = r'^{}{}($|\s)'.format(r'([a-z\-]*\s)' * (level - 1), word.lower())
                if list(filter(re.compile(collision_regex).match, self.reserved_commands)):
                    if word not in self.collided_alias:
                        self.collided_alias[word] = []
                    self.collided_alias[word].append(level)
        telemetry.set_collided_aliases(list(self.collided_alias.keys()))

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
        load_cmd_tbl_func = self.kwargs.get('load_cmd_tbl_func', None)
        if load_cmd_tbl_func:
            self.reserved_commands = list(load_cmd_tbl_func([]).keys())
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
        for arg in args:
            # Trim leading and trailing quotes
            if arg and arg[0] == arg[-1] and arg[0] in '\'"':
                arg = arg[1:-1]
            post_transform_commands.append(os.path.expandvars(arg))

        self.write_alias_config_hash()
        self.write_collided_alias()

        return post_transform_commands

    def write_alias_config_hash(self, empty_hash=False):
        """
        Write self.alias_config_hash to the alias hash file.

        Args:
            empty_hash: True if we want to write an empty string into the file. Empty string in the alias hash file
                means that we have to perform a full load of the command table in the next run.
        """
        with open(GLOBAL_ALIAS_HASH_PATH, 'w') as alias_config_hash_file:
            alias_config_hash_file.write('' if empty_hash else self.alias_config_hash)

    def write_collided_alias(self):
        """
        Write the collided aliases string into the collided alias file.
        """
        # w+ creates the alias config file if it does not exist
        open_mode = 'r+' if os.path.exists(GLOBAL_COLLIDED_ALIAS_PATH) else 'w+'
        with open(GLOBAL_COLLIDED_ALIAS_PATH, open_mode) as collided_alias_file:
            collided_alias_file.truncate()
            collided_alias_file.write(json.dumps(self.collided_alias))

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

    @staticmethod
    def pos_args_iter(alias, args, start_index, num_pos_args):
        """
        Generate an tuple iterator ([0], [1]) where the [0] is the positional argument
        placeholder and [1] is the argument value. e.g. ('{0}', pos_arg_1) -> ('{1}', pos_arg_2) -> ...

        Args:
            alias: The current alias we are processing.
            args: The list of input commands.
            start_index: The index where we start selecting the positional arguments
                (one-index instead of zero-index).
            num_pos_args: The number of positional arguments that this alias has.
        """
        pos_args = args[start_index: start_index + num_pos_args]
        if len(pos_args) != num_pos_args:
            raise CLIError(INSUFFICIENT_POS_ARG_ERROR.format(alias, num_pos_args, len(pos_args)))

        for i, pos_arg in enumerate(pos_args):
            yield ('{{{}}}'.format(i), pos_arg)

    @staticmethod
    def count_positional_args(arg):
        """
        Count how many positional arguments ({0}, {1} ...) there are.

        Args:
            arg: The word which this function performs counting on.

        Returns:
            The number of placeholders in arg.
        """
        return len(re.findall(PLACEHOLDER_REGEX, arg))
