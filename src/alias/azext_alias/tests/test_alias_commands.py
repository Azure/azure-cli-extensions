# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,anomalous-backslash-in-string

import os
import shutil
import tempfile
import unittest

from azure.cli.testsdk import ScenarioTest
from azext_alias import (
    alias,
    custom
)
from azext_alias._const import (
    ALIAS_FILE_NAME,
    ALIAS_HASH_FILE_NAME,
    COLLIDED_ALIAS_FILE_NAME
)


class AliasTests(ScenarioTest):

    def setUp(self):
        self.mock_config_dir = tempfile.mkdtemp()
        alias.GLOBAL_CONFIG_DIR = self.mock_config_dir
        alias.GLOBAL_ALIAS_PATH = os.path.join(self.mock_config_dir, ALIAS_FILE_NAME)
        alias.GLOBAL_ALIAS_HASH_PATH = os.path.join(self.mock_config_dir, ALIAS_HASH_FILE_NAME)
        alias.GLOBAL_COLLIDED_ALIAS_PATH = os.path.join(self.mock_config_dir, COLLIDED_ALIAS_FILE_NAME)
        custom.GLOBAL_ALIAS_PATH = os.path.join(self.mock_config_dir, ALIAS_FILE_NAME)

    def tearDown(self):
        shutil.rmtree(self.mock_config_dir)

    def test_create_and_list_alias(self):
        self.kwargs.update({
            'alias_name': 'c',
            'alias_command': 'create'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.cmd('az alias list', checks=[
            self.check('[0].alias', '{alias_name}'),
            self.check('[0].command', '{alias_command}'),
            self.check('length(@)', 1)
        ])

    def test_create_and_list_alias_env_var(self):
        self.kwargs.update({
            'alias_name': 'mkrgrp',
            'alias_command': 'group create -n test --tags owner=\$USER'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.cmd('az alias list', checks=[
            self.check('[0].alias', '{alias_name}'),
            self.check('[0].command', '{alias_command}'),
            self.check('length(@)', 1)
        ])
        alias_command = self.cmd('az alias list').get_output_in_json()[0]['command']
        assert '\\$USER' in alias_command

    def test_create_and_list_alias_with_pos_arg(self):
        self.kwargs.update({
            'alias_name': 'list-vm {{ resource_group }}',
            'alias_command': 'vm list - -resource-group {{ resource_group }}'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.cmd('az alias list', checks=[
            self.check('[0].alias', '{alias_name}'),
            self.check('[0].command', '{alias_command}'),
            self.check('length(@)', 1)
        ])
        self.kwargs.update({
            'alias_name': 'storage-ls {{ url }}',
            'alias_command': 'storage blob list --account-name {{ url.replace("https://", "").split(".")[0] }} --container-name {{ url.replace("https://", "").split("/")[1] }}'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.cmd('az alias list', checks=[
            self.check('[1].alias', '{alias_name}'),
            self.check('[1].command', '{alias_command}'),
            self.check('length(@)', 2)
        ])

    def test_create_alias_error(self):
        self.kwargs.update({
            'alias_name': 'c',
            'alias_command': 'will_fail'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'', expect_failure=True)
        self.cmd('az alias list', checks=[
            self.check('length(@)', 0)
        ])

    def test_remove_alias(self):
        self.kwargs.update({
            'alias_name': 'c',
            'alias_command': 'create'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
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
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
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
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
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
