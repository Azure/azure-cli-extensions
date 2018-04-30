# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,no-self-use,too-many-public-methods

import os
import sys
import tempfile
import unittest
from mock import patch

from knack.util import CLIError

from azext_alias._validators import process_alias_create_namespace, process_alias_import_namespace
from azext_alias.tests._const import TEST_RESERVED_COMMANDS


class TestValidators(unittest.TestCase):

    def setUp(self):
        self.patcher = patch('azext_alias.cached_reserved_commands', TEST_RESERVED_COMMANDS)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_process_alias_create_namespace_non_existing_command(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_create_namespace(MockAliasCreateNamespace('test', 'non existing command'))
        self.assertEqual(str(cm.exception), 'alias: Invalid Azure CLI command "non existing command"')

    def test_process_alias_create_namespace_empty_alias_name(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_create_namespace(MockAliasCreateNamespace('', 'account'))
        self.assertEqual(str(cm.exception), 'alias: Empty alias name or command is invalid')

    def test_process_alias_create_namespace_empty_alias_command(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_create_namespace(MockAliasCreateNamespace('ac', ''))
        self.assertEqual(str(cm.exception), 'alias: Empty alias name or command is invalid')

    def test_process_alias_create_namespace_non_existing_commands_with_pos_arg(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_create_namespace(MockAliasCreateNamespace('test {{ arg }}', 'account list {{ arg }}'))
        self.assertEqual(str(cm.exception), 'alias: Invalid Azure CLI command "account list {{ arg }}"')

    def test_process_alias_create_namespace_inconsistent_pos_arg_name(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_create_namespace(MockAliasCreateNamespace('test {{ arg }}', 'account {{ ar }}'))
        if sys.version_info.major == 2:
            self.assertTrue(str(cm.exception) in ['alias: Positional arguments set([\'ar\', \'arg\']) are not in both alias name and alias command', 'alias: Positional arguments set([\'arg\', \'ar\']) are not in both alias name and alias command'])
        else:
            self.assertTrue(str(cm.exception) in ['alias: Positional arguments {\'ar\', \'arg\'} are not in both alias name and alias command', 'alias: Positional arguments {\'arg\', \'ar\'} are not in both alias name and alias command'])

    def test_process_alias_create_namespace_pos_arg_only(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_create_namespace(MockAliasCreateNamespace('test {{ arg }}', '{{ arg }}'))
        self.assertEqual(str(cm.exception), 'alias: Invalid Azure CLI command "{{ arg }}"')

    def test_process_alias_create_namespace_inconsistent_number_pos_arg(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_create_namespace(MockAliasCreateNamespace('test {{ arg_1 }} {{ arg_2 }}', 'account {{ arg_2 }}'))
        if sys.version_info.major == 2:
            self.assertEqual(str(cm.exception), 'alias: Positional argument set([\'arg_1\']) is not in both alias name and alias command')
        else:
            self.assertEqual(str(cm.exception), 'alias: Positional argument {\'arg_1\'} is not in both alias name and alias command')

    def test_process_alias_create_namespace_lvl_error(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_create_namespace(MockAliasCreateNamespace('network', 'account list'))
        self.assertEqual(str(cm.exception), 'alias: Invalid Azure CLI command "account list"')

    def test_process_alias_create_namespace_lvl_error_with_pos_arg(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_create_namespace(MockAliasCreateNamespace('account {{ test }}', 'dns {{ test }}'))
        self.assertEqual(str(cm.exception), 'alias: "account {{ test }}" is a reserved command and cannot be used to represent "dns {{ test }}"')

    def test_process_alias_create_namespace_pos_arg_1(self):
        process_alias_create_namespace(MockAliasCreateNamespace('test', 'group delete resourceGroupName'))

    def test_process_alias_create_namespace_pos_arg_2(self):
        process_alias_create_namespace(MockAliasCreateNamespace('test', 'delete resourceGroupName'))

    def test_process_alias_create_namespace_pos_arg_3(self):
        process_alias_create_namespace(MockAliasCreateNamespace('test', 'group delete resourceGroupName -p param'))

    def test_process_alias_create_namespace_pos_arg_4(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_create_namespace(MockAliasCreateNamespace('test', 'group resourceGroupName'))
        self.assertEqual(str(cm.exception), 'alias: Invalid Azure CLI command "group resourceGroupName"')

    def test_process_alias_create_namespace_pos_arg_5(self):
        process_alias_create_namespace(MockAliasCreateNamespace('test', 'group delete -p param resourceGroupName'))

    def test_process_alias_import_namespace(self):
        process_alias_import_namespace(MockAliasImportNamespace('https://raw.githubusercontent.com/chewong/azure-cli-alias-extension/test/azext_alias/tests/alias'))

    def test_process_alias_import_namespace_invalid_url_python_2(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_import_namespace(MockAliasImportNamespace('https://raw.githubusercontent.com/chewong/azure-cli-alias-extension/test/azext_alias/tests/alia'))
        if sys.version_info.major == 2:
            self.assertEqual(str(cm.exception), 'alias: Encounted error when retrieving alias file from https://raw.githubusercontent.com/chewong/azure-cli-alias-extension/test/azext_alias/tests/alia. Error detail: 404: Not Found')
        else:
            self.assertEqual(str(cm.exception), 'alias: Encounted error when retrieving alias file from https://raw.githubusercontent.com/chewong/azure-cli-alias-extension/test/azext_alias/tests/alia. Error detail: HTTP Error 404: Not Found')

    def test_process_alias_import_namespace_invalid_content_from_url(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_import_namespace(MockAliasImportNamespace('https://raw.githubusercontent.com/chewong/azure-cli-alias-extension/test/azext_alias/tests/invalid_alias'))
        if sys.version_info.major == 2:
            self.assertEqual(str(cm.exception), 'alias: Please ensure you have a valid alias configuration file. Error detail: File contains no alias headers.file: https://raw.githubusercontent.com/chewong/azure-cli-alias-extension/test/azext_alias/tests/invalid_alias, line: 1\'[c\'')
        else:
            self.assertEqual(str(cm.exception), 'alias: Please ensure you have a valid alias configuration file. Error detail: File contains no alias headers.file: \'https://raw.githubusercontent.com/chewong/azure-cli-alias-extension/test/azext_alias/tests/invalid_alias\', line: 1\'[c\'')

    def test_process_alias_import_namespace_file(self):
        _, mock_alias_config_file = tempfile.mkstemp()
        process_alias_import_namespace(MockAliasImportNamespace(mock_alias_config_file))
        os.remove(mock_alias_config_file)

    def test_process_alias_import_namespace_invalid_content_in_file(self):
        _, mock_alias_config_file = tempfile.mkstemp()
        with open(mock_alias_config_file, 'w') as f:
            f.write('invalid alias config format')
        with self.assertRaises(CLIError) as cm:
            process_alias_import_namespace(MockAliasImportNamespace(mock_alias_config_file))
        if sys.version_info.major == 2:
            self.assertEqual(str(cm.exception), 'alias: Please ensure you have a valid alias configuration file. Error detail: File contains no alias headers.file: {}, line: 1\'invalid alias config format\''.format(mock_alias_config_file))
        else:
            self.assertEqual(str(cm.exception), 'alias: Please ensure you have a valid alias configuration file. Error detail: File contains no alias headers.file: \'{}\', line: 1\'invalid alias config format\''.format(mock_alias_config_file))
        os.remove(mock_alias_config_file)

    def test_process_alias_import_namespace_dir(self):
        with self.assertRaises(CLIError) as cm:
            process_alias_import_namespace(MockAliasImportNamespace(os.getcwd()))
        self.assertEqual(str(cm.exception), 'alias: {} is a directory'.format(os.getcwd()))


class MockAliasCreateNamespace(object):  # pylint: disable=too-few-public-methods

    def __init__(self, alias_name, alias_command):
        self.alias_name = alias_name
        self.alias_command = alias_command


class MockAliasImportNamespace(object):  # pylint: disable=too-few-public-methods

    def __init__(self, alias_source):
        self.alias_source = alias_source


if __name__ == '__main__':
    unittest.main()
