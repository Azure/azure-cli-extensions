# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,import-error,no-self-use,deprecated-method,pointless-string-statement,relative-import,no-member,redefined-outer-name,too-many-return-statements

import sys
import os
import shlex
import unittest
from six.moves import configparser

from knack.util import CLIError

from azext_alias import alias
from azext_alias.tests._const import (DEFAULT_MOCK_ALIAS_STRING,
                                      COLLISION_MOCK_ALIAS_STRING,
                                      TEST_RESERVED_COMMANDS,
                                      DUP_SECTION_MOCK_ALIAS_STRING,
                                      DUP_OPTION_MOCK_ALIAS_STRING,
                                      MALFORMED_MOCK_ALIAS_STRING)

# Various test types
TEST_TRANSFORM_ALIAS = 'test_transform_alias'
TEST_TRANSFORM_COLLIDED_ALIAS = 'test_transform_collided_alias'
TEST_TRANSFORM_EMPTY_STRING = 'test_transform_empty_string'
TEST_POST_TRANSFORM_ENV_VAR = 'test_post_transform_env_var'
TEST_INCONSISTENT_PLACEHOLDER_INDEX = 'test_inconsistent_placeholder_index'
TEST_PARSE_ERROR_PYTHON_3 = 'test_parse_error_python_3'
TEST_PARSE_ERROR_PYTHON_2_3 = 'test_parse_error_python_2_3'

TEST_DATA = {
    TEST_TRANSFORM_ALIAS: [
        ('ac', 'account'),
        ('ls', 'list -otable'),
        ('ac ls', 'account list -otable'),
        ('mn diag', 'monitor diagnostic-settings create'),
        ('create-vm', 'vm create -g test-group -n test-vm'),
        ('ac-ls', 'ac ls'),
        ('-h', '-h'),
        ('storage-connect test1 test2', 'storage account connection-string -g test1 -n test2 -otsv'),
        ('', ''),
        ('test --json \'{"test": "arg"}\'', 'test --json \'{"test": "arg"}\''),
        ('ac set -s test', 'account set -s test'),
        ('vm ls -g test -otable', 'vm list -otable -g test -otable'),
        ('cp test1 test2', 'storage blob copy start-batch --source-uri test1 --destination-container test2'),
        ('pos-arg-1 test1 test2', 'iot test1test test2test'),
        ('pos-arg-2 test1 test2', 'sf test1 test1 test2 test2'),
        ('pos-arg-json \'{"test": "arg"}\'', 'test --json \'{"test": "arg"}\''),
        ('cp test1 test2 -o tsv', 'storage blob copy start-batch --source-uri test1 --destination-container test2 -o tsv'),
        ('create-vm --image ubtuntults --generate-ssh-key --no-wait', 'vm create -g test-group -n test-vm --image ubtuntults --generate-ssh-key --no-wait'),
        ('cp mn diag', 'storage blob copy start-batch --source-uri mn --destination-container diag'),
        ('storage-ls azurecliprod.blob.core.windows.net/cli-extensions', 'storage blob list --account-name azurecliprod --container-name cli-extensions'),
        ('storage-ls-2 https://azurecliprod.blob.core.windows.net/cli-extensions', 'storage blob list --account-name azurecliprod --container-name cli-extensions')
    ],
    TEST_TRANSFORM_COLLIDED_ALIAS: [
        ('account list -otable', 'account list -otable'),
        ('account list-locations', 'account list-locations'),
        ('list-locations', 'diagnostic-settings create'),
        ('dns', 'network dns'),
        ('network dns', 'network dns')
    ],
    TEST_TRANSFORM_EMPTY_STRING: [
        ('network vnet update -g test -n test --dns-servers ""', 'network vnet update -g test -n test --dns-servers'),
        ('test1 test2 --query ""', 'test1 test2 --query')
    ],
    TEST_POST_TRANSFORM_ENV_VAR: [
        ('group create -n test --tags tag1=$tag1 tag2=$tag2 tag3=$non-existing-env-var', 'group create -n test --tags tag1=test-env-var-1 tag2=test-env-var-2 tag3=$non-existing-env-var')
    ],
    TEST_INCONSISTENT_PLACEHOLDER_INDEX: [
        ['cp'],
        ['cp', 'test']
    ],
    TEST_PARSE_ERROR_PYTHON_3: [
        DUP_SECTION_MOCK_ALIAS_STRING,
        DUP_OPTION_MOCK_ALIAS_STRING
    ],
    TEST_PARSE_ERROR_PYTHON_2_3: [
        MALFORMED_MOCK_ALIAS_STRING,
        'Malformed alias config file string'
    ]
}


def test_transform_alias(self, test_case):
    self.assertAlias(test_case)


def test_transform_collided_alias(self, test_case):
    alias_manager = self.get_alias_manager(COLLISION_MOCK_ALIAS_STRING, TEST_RESERVED_COMMANDS)
    alias_manager.build_collision_table()
    self.assertEqual(shlex.split(test_case[1]), alias_manager.transform(shlex.split(test_case[0])))


def test_transform_empty_string(self, test_case):
    alias_manager = self.get_alias_manager()
    transformed_args = alias_manager.transform(shlex.split(test_case[0]))
    expected_args = shlex.split(test_case[1])
    self.assertEqual(expected_args, transformed_args[:-1])
    self.assertEqual('', transformed_args[-1])


def test_post_transform_env_var(self, test_case):
    os.environ['tag1'] = 'test-env-var-1'
    os.environ['tag2'] = 'test-env-var-2'
    self.assertPostTransform(test_case)


def test_inconsistent_placeholder_index(self, test_case):
    alias_manager = self.get_alias_manager()
    with self.assertRaises(CLIError):
        alias_manager.transform(test_case)


def test_parse_error_python_3(self, test_case):
    if sys.version_info.major == 3:
        alias_manager = self.get_alias_manager(test_case)
        self.assertTrue(alias_manager.parse_error())


def test_parse_error_python_2_3(self, test_case):
    alias_manager = self.get_alias_manager(test_case)
    self.assertTrue(alias_manager.parse_error())


def generate_test(test_type, test_case):
    def test(self):
        TEST_FN[test_type](self, test_case)
    return test


TEST_FN = {
    TEST_TRANSFORM_ALIAS: test_transform_alias,
    TEST_TRANSFORM_COLLIDED_ALIAS: test_transform_collided_alias,
    TEST_TRANSFORM_EMPTY_STRING: test_transform_empty_string,
    TEST_POST_TRANSFORM_ENV_VAR: test_post_transform_env_var,
    TEST_INCONSISTENT_PLACEHOLDER_INDEX: test_inconsistent_placeholder_index,
    TEST_PARSE_ERROR_PYTHON_3: test_parse_error_python_3,
    TEST_PARSE_ERROR_PYTHON_2_3: test_parse_error_python_2_3
}


class TestAlias(unittest.TestCase):

    def test_build_empty_collision_table(self):
        alias_manager = self.get_alias_manager(DEFAULT_MOCK_ALIAS_STRING, TEST_RESERVED_COMMANDS)
        self.assertDictEqual(dict(), alias_manager.collided_alias)

    def test_build_non_empty_collision_table(self):
        alias_manager = self.get_alias_manager(COLLISION_MOCK_ALIAS_STRING, TEST_RESERVED_COMMANDS)
        alias_manager.build_collision_table(levels=2)
        self.assertDictEqual({'account': [1, 2], 'dns': [2], 'list-locations': [2]}, alias_manager.collided_alias)

    def test_non_parse_error(self):
        alias_manager = self.get_alias_manager()
        self.assertFalse(alias_manager.parse_error())

    def test_detect_alias_config_change(self):
        alias_manager = self.get_alias_manager()
        alias.alias_config_str = DEFAULT_MOCK_ALIAS_STRING
        self.assertFalse(alias_manager.detect_alias_config_change())

        alias_manager = self.get_alias_manager()
        # Load a new alias file (an empty string in this case)
        alias_manager.alias_config_str = ''
        self.assertTrue(alias_manager.detect_alias_config_change())

    """
    Helper functions
    """
    def get_alias_manager(self, mock_alias_str=DEFAULT_MOCK_ALIAS_STRING, reserved_commands=None):
        alias_manager = MockAliasManager(mock_alias_str=mock_alias_str)
        alias_manager.reserved_commands = reserved_commands if reserved_commands else []
        return alias_manager

    def assertAlias(self, value):
        """ Assert the alias with the default alias config file """
        alias_manager = self.get_alias_manager()
        self.assertEqual(shlex.split(value[1]), alias_manager.transform(shlex.split(value[0])))

    def assertPostTransform(self, value, mock_alias_str=DEFAULT_MOCK_ALIAS_STRING):
        alias_manager = self.get_alias_manager(mock_alias_str=mock_alias_str)
        self.assertEqual(shlex.split(value[1]), alias_manager.post_transform(shlex.split(value[0])))


class MockAliasManager(alias.AliasManager):

    def load_alias_table(self):

        self.alias_config_str = self.kwargs.get('mock_alias_str', '')
        try:
            if sys.version_info.major == 3:
                # Python 3.x implementation
                self.alias_table.read_string(self.alias_config_str)
            else:
                # Python 2.x implementation
                from StringIO import StringIO
                self.alias_table.readfp(StringIO(self.alias_config_str))
        except Exception:  # pylint: disable=broad-except
            self.alias_table = configparser.ConfigParser()

    def load_alias_hash(self):
        import hashlib
        self.alias_config_hash = hashlib.sha1(self.alias_config_str.encode('utf-8')).hexdigest()

    def load_collided_alias(self):
        pass

    def write_alias_config_hash(self, empty_hash=False):
        pass

    def write_collided_alias(self):
        pass


# Inject data-driven tests into TestAlias class
for test_type, test_cases in TEST_DATA.items():
    for test_index, test_case in enumerate(test_cases, 1):
        setattr(TestAlias, '{}_{}'.format(test_type, test_index), generate_test(test_type, test_case))


if __name__ == '__main__':
    unittest.main()
