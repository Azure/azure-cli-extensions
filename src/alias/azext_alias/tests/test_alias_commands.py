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

from azure.cli.testsdk import ScenarioTest
from azext_alias import alias
from azext_alias._const import (
    ALIAS_FILE_NAME,
    ALIAS_HASH_FILE_NAME,
    COLLIDED_ALIAS_FILE_NAME,
    ALIAS_TAB_COMP_TABLE_FILE_NAME
)


class AliasTests(ScenarioTest):

    def setUp(self):
        self.mock_config_dir = tempfile.mkdtemp()
        self.patchers = []
        self.patchers.append(mock.patch('azext_alias.alias.GLOBAL_CONFIG_DIR', self.mock_config_dir))
        self.patchers.append(mock.patch('azext_alias.alias.GLOBAL_ALIAS_PATH', os.path.join(self.mock_config_dir, ALIAS_FILE_NAME)))
        self.patchers.append(mock.patch('azext_alias.alias.GLOBAL_ALIAS_HASH_PATH', os.path.join(self.mock_config_dir, ALIAS_HASH_FILE_NAME)))
        self.patchers.append(mock.patch('azext_alias.alias.GLOBAL_COLLIDED_ALIAS_PATH', os.path.join(self.mock_config_dir, COLLIDED_ALIAS_FILE_NAME)))
        self.patchers.append(mock.patch('azext_alias.util.GLOBAL_ALIAS_TAB_COMP_TABLE_PATH', os.path.join(self.mock_config_dir, ALIAS_TAB_COMP_TABLE_FILE_NAME)))
        self.patchers.append(mock.patch('azext_alias.custom.GLOBAL_ALIAS_PATH', os.path.join(self.mock_config_dir, ALIAS_FILE_NAME)))
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self):
        for patcher in self.patchers:
            patcher.stop()
        shutil.rmtree(self.mock_config_dir)

    def test_create_and_list_alias(self):
        self.kwargs.update({
            'alias_name': 'c',
            'alias_command': 'create'
        })
        self.cmd('az alias create -n "{alias_name}" -c "{alias_command}"')
        self.cmd('az alias list', checks=[
            self.check('[0].alias', '{alias_name}'),
            self.check('[0].command', '{alias_command}'),
            self.check('length(@)', 1)
        ])

    def test_create_alias_error(self):
        self.kwargs.update({
            'alias_name': 'c',
            'alias_command': 'will_fail'
        })
        self.cmd('az alias create -n "{alias_name}" -c "{alias_command}"', expect_failure=True)
        self.cmd('az alias list', checks=[
            self.check('length(@)', 0)
        ])

    def test_remove_alias(self):
        self.kwargs.update({
            'alias_name': 'c',
            'alias_command': 'create'
        })
        self.cmd('az alias create -n "{alias_name}" -c "{alias_command}"')
        self.cmd('az alias list', checks=[
            self.check('[0].alias', '{alias_name}'),
            self.check('[0].command', '{alias_command}'),
            self.check('length(@)', 1)
        ])
        self.cmd('az alias remove -n "{alias_name}"')
        self.cmd('az alias list', checks=[
            self.check('length(@)', 0)
        ])

    def test_remove_alias_non_existing(self):
        self.kwargs.update({
            'alias_name': 'c',
        })
        self.cmd('az alias list', checks=[
            self.check('length(@)', 0)
        ])
        self.cmd('az alias remove -n "{alias_name}"', expect_failure=True)

    def test_alias_file_and_hash_create(self):
        self.kwargs.update({
            'alias_name': 'c',
            'alias_command': 'create'
        })
        self.cmd('az alias create -n "{alias_name}" -c "{alias_command}"')
        expected_alias_string = '''[c]
command = create

'''
        with open(alias.GLOBAL_ALIAS_PATH) as alias_config_file:
            assert alias_config_file.read() == expected_alias_string

    def test_alias_file_and_hash_remove(self):
        self.kwargs.update({
            'alias_name': 'c',
            'alias_command': 'create'
        })
        self.cmd('az alias create -n "{alias_name}" -c "{alias_command}"')
        self.cmd('az alias list', checks=[
            self.check('[0].alias', '{alias_name}'),
            self.check('[0].command', '{alias_command}'),
            self.check('length(@)', 1)
        ])
        self.cmd('az alias remove -n "{alias_name}"')

        with open(alias.GLOBAL_ALIAS_PATH) as alias_config_file:
            assert not alias_config_file.read()


if __name__ == '__main__':
    unittest.main()
