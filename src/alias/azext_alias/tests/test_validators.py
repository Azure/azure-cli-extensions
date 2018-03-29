# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from knack.util import CLIError

from azext_alias._validators import process_alias_create_namespace


class TestValidators(unittest.TestCase):

    def test_process_alias_create_namespace_non_existing_command(self):
        with self.assertRaises(CLIError):
            process_alias_create_namespace(MockNamespace('test', 'non existing command'))

    def test_process_alias_create_namespace_empty_alias_name(self):
        with self.assertRaises(CLIError):
            process_alias_create_namespace(MockNamespace('', 'account'))

    def test_process_alias_create_namespace_empty_alias_command(self):
        with self.assertRaises(CLIError):
            process_alias_create_namespace(MockNamespace('ac', ''))

    def test_process_alias_create_namespace_non_existing_commands_with_pos_arg(self):
        with self.assertRaises(CLIError):
            process_alias_create_namespace(MockNamespace('test {{ arg }}', 'account list {{ arg }}'))

    def test_process_alias_create_namespace_inconsistent_pos_arg_name(self):
        with self.assertRaises(CLIError):
            process_alias_create_namespace(MockNamespace('test {{ arg }}', 'account {{ ar }}'))

    def test_process_alias_create_namespace_pos_arg_only(self):
        with self.assertRaises(CLIError):
            process_alias_create_namespace(MockNamespace('test {{ arg }}', '{{ arg }}'))

    def test_process_alias_create_namespace_inconsistent_number_pos_arg(self):
        with self.assertRaises(CLIError):
            process_alias_create_namespace(MockNamespace('test {{ arg_1 }} {{ arg_2 }}', 'account {{ arg_2 }}'))

    def test_process_alias_create_namespace_lvl_error(self):
        with self.assertRaises(CLIError):
            process_alias_create_namespace(MockNamespace('network', 'account list'))

    def test_process_alias_create_namespace_lvl_error_with_pos_arg(self):
        with self.assertRaises(CLIError):
            process_alias_create_namespace(MockNamespace('account {{ test }}', 'dns {{ test }}'))


class MockNamespace(object):  # pylint: disable=too-few-public-methods

    def __init__(self, alias_name, alias_command):
        self.alias_name = alias_name
        self.alias_command = alias_command


if __name__ == '__main__':
    unittest.main()
