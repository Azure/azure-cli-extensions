# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

import os
import shutil
import tempfile
import unittest
import mock

from azext_alias.util import remove_pos_arg_placeholders, build_tab_completion_table, get_config_parser
from azext_alias._const import ALIAS_TAB_COMP_TABLE_FILE_NAME
from azext_alias.tests._const import TEST_RESERVED_COMMANDS


class TestUtil(unittest.TestCase):

    def setUp(self):
        self.mock_config_dir = tempfile.mkdtemp()
        self.patchers = []
        self.patchers.append(mock.patch('azext_alias.util.GLOBAL_ALIAS_TAB_COMP_TABLE_PATH', os.path.join(self.mock_config_dir, ALIAS_TAB_COMP_TABLE_FILE_NAME)))
        self.patchers.append(mock.patch('azext_alias.cached_reserved_commands', TEST_RESERVED_COMMANDS))
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()
        shutil.rmtree(self.mock_config_dir)

    def test_remove_pos_arg_placeholders(self):
        self.assertEqual('webapp create', remove_pos_arg_placeholders('webapp create'))

    def test_remove_pos_arg_placeholders_with_pos_arg(self):
        self.assertEqual('network dns', remove_pos_arg_placeholders('network dns {{ arg_1 }}'))

    def test_remove_pos_arg_placeholders_with_args(self):
        self.assertEqual('vm create', remove_pos_arg_placeholders('vm create -g test -n test'))

    def test_remove_pos_arg_placeholders_with_query(self):
        self.assertEqual('group list', remove_pos_arg_placeholders('group list --query "[].{Name:name, Location:location}" --output table'))

    def test_build_tab_completion_table(self):
        mock_alias_table = get_config_parser()
        mock_alias_table.add_section('ac')
        mock_alias_table.set('ac', 'command', 'account')
        mock_alias_table.add_section('ll')
        mock_alias_table.set('ll', 'command', 'list-locations')
        mock_alias_table.add_section('n')
        mock_alias_table.set('n', 'command', 'network')
        mock_alias_table.add_section('al')
        mock_alias_table.set('al', 'command', 'account list-locations')
        tab_completion_table = build_tab_completion_table(mock_alias_table)
        self.assertDictEqual({
            'account': ['', 'storage'],
            'list-locations': ['account'],
            'network': [''],
            'account list-locations': ['']
        }, tab_completion_table)


if __name__ == '__main__':
    unittest.main()
