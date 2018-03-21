# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,no-self-use,protected-access

import unittest
from mock import Mock

from knack.util import CLIError

import azext_alias
from azext_alias.alias import get_config_parser
from azext_alias.tests._const import TEST_RESERVED_COMMANDS
from azext_alias.custom import (
    create_alias,
    list_alias,
    remove_alias,
)


class AliasCustomCommandTest(unittest.TestCase):

    @classmethod
    def setUp(cls):
        azext_alias.cached_reserved_commands = TEST_RESERVED_COMMANDS
        azext_alias.custom._commit_change = Mock()

    def test_create_alias(self):
        create_alias('ac', 'account')

    def test_create_alias_multiple_commands(self):
        create_alias('dns', 'network dns')

    def test_create_alias_pos_arg(self):
        create_alias('test {{ arg }}', 'account {{ arg }}')

    def test_create_alias_pos_arg_with_addtional_processing(self):
        create_alias('test {{ arg }}', 'account {{ arg.replace("https://", "") }}')

    def test_create_alias_pos_arg_with_filter(self):
        create_alias('test {{ arg }}', 'account {{ arg | upper }}')

    def test_create_alias_pos_arg_with_filter_and_addtional_processing(self):
        create_alias('test {{ arg }}', 'account {{ arg.replace("https://", "") | upper }}')

    def test_create_alias_non_existing_command(self):
        with self.assertRaises(CLIError):
            create_alias('test', 'non existing command')

    def test_create_alias_empty_alias_name(self):
        with self.assertRaises(CLIError):
            create_alias('', 'account')

    def test_create_alias_empty_alias_command(self):
        with self.assertRaises(CLIError):
            create_alias('ac', '')

    def test_create_alias_non_existing_commands_with_pos_arg(self):
        with self.assertRaises(CLIError):
            create_alias('test {{ arg }}', 'account list {{ arg }}')

    def test_create_alias_inconsistent_pos_arg_name(self):
        with self.assertRaises(CLIError):
            create_alias('test {{ arg }}', 'account {{ ar }}')

    def test_create_alias_pos_arg_only(self):
        with self.assertRaises(CLIError):
            create_alias('test {{ arg }}', '{{ arg }}')

    def test_create_alias_inconsistent_number_pos_arg(self):
        with self.assertRaises(CLIError):
            create_alias('test {{ arg_1 }} {{ arg_2 }}', 'account {{ arg_2 }}')

    def test_create_alias_lvl_error(self):
        with self.assertRaises(CLIError):
            create_alias('network', 'account list')

    def test_create_alias_lvl_error_with_pos_arg(self):
        with self.assertRaises(CLIError):
            create_alias('account {{ test }}', 'dns {{ test }}')

    def test_list_alias(self):
        mock_alias_table = get_config_parser()
        mock_alias_table.add_section('ac')
        mock_alias_table.set('ac', 'command', 'account')
        azext_alias.custom._get_alias_table = Mock(return_value=mock_alias_table)
        self.assertListEqual([{'alias': 'ac', 'command': 'account'}], list_alias())

    def test_list_alias_key_misspell(self):
        mock_alias_table = get_config_parser()
        mock_alias_table.add_section('ac')
        mock_alias_table.set('ac', 'cmmand', 'account')
        azext_alias.custom._get_alias_table = Mock(return_value=mock_alias_table)
        self.assertListEqual([], list_alias())

    def test_list_alias_multiple_alias(self):
        mock_alias_table = get_config_parser()
        mock_alias_table.add_section('ac')
        mock_alias_table.set('ac', 'command', 'account')
        mock_alias_table.add_section('dns')
        mock_alias_table.set('dns', 'command', 'network dns')
        azext_alias.custom._get_alias_table = Mock(return_value=mock_alias_table)
        self.assertListEqual([{'alias': 'ac', 'command': 'account'}, {'alias': 'dns', 'command': 'network dns'}], list_alias())

    def test_remove_alias_remove_non_existing_alias(self):
        mock_alias_table = get_config_parser()
        mock_alias_table.add_section('ac')
        mock_alias_table.set('ac', 'command', 'account')
        azext_alias.custom._get_alias_table = Mock(return_value=mock_alias_table)
        with self.assertRaises(CLIError):
            remove_alias('dns')


if __name__ == '__main__':
    unittest.main()
