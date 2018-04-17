# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,no-self-use,protected-access

import unittest
from mock import Mock, patch

from knack.util import CLIError

import azext_alias
from azext_alias.util import get_config_parser
from azext_alias.tests._const import TEST_RESERVED_COMMANDS
from azext_alias.custom import (
    create_alias,
    list_alias,
    remove_alias,
)


class AliasCustomCommandTest(unittest.TestCase):

    def setUp(self):
        self.patcher = patch('azext_alias.cached_reserved_commands', TEST_RESERVED_COMMANDS)
        self.patcher.start()
        azext_alias.custom._commit_change = Mock()

    def tearDown(self):
        self.patcher.stop()

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

    def test_list_alias(self):
        mock_alias_table = get_config_parser()
        mock_alias_table.add_section('ac')
        mock_alias_table.set('ac', 'command', 'account')
        azext_alias.custom.get_alias_table = Mock(return_value=mock_alias_table)
        self.assertListEqual([{'alias': 'ac', 'command': 'account'}], list_alias())

    def test_list_alias_key_misspell(self):
        mock_alias_table = get_config_parser()
        mock_alias_table.add_section('ac')
        mock_alias_table.set('ac', 'cmmand', 'account')
        azext_alias.custom.get_alias_table = Mock(return_value=mock_alias_table)
        self.assertListEqual([], list_alias())

    def test_list_alias_multiple_alias(self):
        mock_alias_table = get_config_parser()
        mock_alias_table.add_section('ac')
        mock_alias_table.set('ac', 'command', 'account')
        mock_alias_table.add_section('dns')
        mock_alias_table.set('dns', 'command', 'network dns')
        azext_alias.custom.get_alias_table = Mock(return_value=mock_alias_table)
        self.assertListEqual([{'alias': 'ac', 'command': 'account'}, {'alias': 'dns', 'command': 'network dns'}], list_alias())

    def test_remove_alias_remove_non_existing_alias(self):
        mock_alias_table = get_config_parser()
        mock_alias_table.add_section('ac')
        mock_alias_table.set('ac', 'command', 'account')
        azext_alias.custom.get_alias_table = Mock(return_value=mock_alias_table)
        with self.assertRaises(CLIError) as cm:
            remove_alias(['dns'])
        self.assertEqual(str(cm.exception), 'alias: "dns" alias not found')


if __name__ == '__main__':
    unittest.main()
