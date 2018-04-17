# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,too-many-public-methods

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
        os.makedirs(os.path.join(self.mock_config_dir, 'export'))
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

    def test_remove_multiple_aliases(self):
        self.kwargs.update({
            'alias_name': 'c',
            'alias_command': 'create'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.kwargs.update({
            'alias_name': 'storage-ls {{ url }}',
            'alias_command': 'storage blob list --account-name {{ url.replace("https://", "").split(".")[0] }} --container-name {{ url.replace("https://", "").split("/")[1] }}'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.cmd('az alias list', checks=[
            self.check('length(@)', 2)
        ])
        self.cmd('az alias remove -n \'storage-ls {{{{ url }}}}\' c')
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

    def test_alias_file_remove(self):
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

    def test_create_and_import_file(self):
        _, mock_alias_config_file = tempfile.mkstemp()
        with open(mock_alias_config_file, 'w') as f:
            f.write('[c]\ncommand = create\n[grp]\ncommand = group')

        self.kwargs.update({
            'alias_source': mock_alias_config_file
        })
        self.cmd('az alias import -s {alias_source}')
        self.cmd('az alias list', checks=[
            self.check('[0].alias', 'c'),
            self.check('[0].command', 'create'),
            self.check('[1].alias', 'grp'),
            self.check('[1].command', 'group'),
            self.check('length(@)', 2)
        ])
        os.remove(mock_alias_config_file)

    def test_create_and_import_url(self):
        self.kwargs.update({
            'alias_source': 'https://raw.githubusercontent.com/chewong/azure-cli-alias-extension/test/azext_alias/tests/alias'
        })
        self.cmd('az alias import -s {alias_source}')
        self.cmd('az alias list', checks=[
            self.check('[0].alias', 'c'),
            self.check('[0].command', 'create'),
            self.check('[1].alias', 'grp'),
            self.check('[1].command', 'group'),
            self.check('length(@)', 2)
        ])

    def test_create_and_import_collide(self):
        self.kwargs.update({
            'alias_name': 'c',
            'alias_command': 'vm'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.cmd('az alias list', checks=[
            self.check('[0].alias', '{alias_name}'),
            self.check('[0].command', '{alias_command}'),
            self.check('length(@)', 1)
        ])
        self.kwargs.update({
            'alias_source': 'https://raw.githubusercontent.com/chewong/azure-cli-alias-extension/test/azext_alias/tests/alias'
        })
        self.cmd('az alias import -s {alias_source}')
        self.cmd('az alias list', checks=[
            self.check('[0].alias', 'c'),
            self.check('[0].command', 'create'),
            self.check('[1].alias', 'grp'),
            self.check('[1].command', 'group'),
            self.check('length(@)', 2)
        ])

    def test_import_invalid_content_from_url(self):
        self.kwargs.update({
            'alias_source': 'https://raw.githubusercontent.com/chewong/azure-cli-alias-extension/test/azext_alias/tests/invalid_alias'
        })
        self.cmd('az alias import -s {alias_source}', expect_failure=True)
        self.cmd('az alias list', checks=[
            self.check('length(@)', 0)
        ])

    def test_remove_all_aliases(self):
        self.kwargs.update({
            'alias_name': 'list-vm {{ resource_group }}',
            'alias_command': 'vm list --resource-group {{ resource_group }}'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.kwargs.update({
            'alias_name': 'storage-ls {{ url }}',
            'alias_command': 'storage blob list --account-name {{ url.replace("https://", "").split(".")[0] }} --container-name {{ url.replace("https://", "").split("/")[1] }}'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.cmd('az alias list', checks=[
            self.check('length(@)', 2)
        ])
        self.cmd('az alias remove-all --yes')
        self.cmd('az alias list', checks=[
            self.check('length(@)', 0)
        ])

    def test_excessive_whitespaces_in_alias_command(self):
        self.kwargs.update({
            'alias_name': ' list-vm      \n{{                   resource_group              }}       ',
            'alias_command': '    vm \n list       --resource-group {{      resource_group   }}     '
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.cmd('az alias list', checks=[
            self.check('[0].alias', 'list-vm {{{{ resource_group }}}}'),
            self.check('[0].command', 'vm list --resource-group {{{{ resource_group }}}}'),
            self.check('length(@)', 1)
        ])

    @mock.patch('os.getcwd')
    def test_export_file_name_only(self, mock_os_getcwd):
        mock_os_getcwd.return_value = os.path.join(self.mock_config_dir, 'export')
        self._pre_test_export()
        self.cmd('az alias export -p alias')
        self._post_test_export(os.path.join(self.mock_config_dir, 'export', 'alias'))

    @mock.patch('os.getcwd')
    def test_export_existing_file(self, mock_os_getcwd):
        mock_os_getcwd.return_value = os.path.join(self.mock_config_dir, 'export')
        self._pre_test_export()
        self.cmd('az alias export -p alias')
        self.cmd('az alias export -p alias', expect_failure=True)

    @mock.patch('os.getcwd')
    def test_export_path_relative_path(self, mock_os_getcwd):
        mock_os_getcwd.return_value = os.path.join(self.mock_config_dir, 'export')
        self._pre_test_export()
        self.cmd('az alias export -p test1/test2/alias')
        self._post_test_export(os.path.join(self.mock_config_dir, 'export', 'test1', 'test2', 'alias'))

    @mock.patch('os.getcwd')
    def test_export_path_dir_only(self, mock_os_getcwd):
        mock_os_getcwd.return_value = os.path.join(self.mock_config_dir, 'export')
        self._pre_test_export()
        self.cmd('az alias export -p {}'.format(os.path.join(self.mock_config_dir, 'export')))
        self._post_test_export(os.path.join(self.mock_config_dir, 'export', 'alias'))

    @mock.patch('os.getcwd')
    def test_export_path_absolute_path(self, mock_os_getcwd):
        mock_os_getcwd.return_value = os.path.join(self.mock_config_dir, 'export')
        self._pre_test_export()
        self.cmd('az alias export -p {}'.format(os.path.join(self.mock_config_dir, 'export', 'alias12345')))
        self._post_test_export(os.path.join(self.mock_config_dir, 'export', 'alias12345'))

    @mock.patch('os.getcwd')
    def test_export_path_exclusion(self, mock_os_getcwd):
        mock_os_getcwd.return_value = os.path.join(self.mock_config_dir, 'export')
        self._pre_test_export()
        self.cmd('az alias export -p {} -e \'{}\''.format('alias', 'storage-ls {{{{ url }}}}'))
        self._post_test_export(os.path.join(self.mock_config_dir, 'export', 'alias'), test_exclusion=True)

    @mock.patch('os.getcwd')
    def test_export_path_exclusion_error(self, mock_os_getcwd):
        mock_os_getcwd.return_value = os.path.join(self.mock_config_dir, 'export')
        self._pre_test_export()
        self.cmd('az alias export -p {} -e {}'.format('alias', 'invalid_alias'), expect_failure=True)

    def _pre_test_export(self):
        self.kwargs.update({
            'alias_name': 'c',
            'alias_command': 'create'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.kwargs.update({
            'alias_name': 'storage-ls {{ url }}',
            'alias_command': 'storage blob list --account-name {{ url.replace("https://", "").split(".")[0] }} --container-name {{ url.replace("https://", "").split("/")[1] }}'
        })
        self.cmd('az alias create -n \'{alias_name}\' -c \'{alias_command}\'')
        self.cmd('az alias list', checks=[
            self.check('length(@)', 2)
        ])

    def _post_test_export(self, export_path, test_exclusion=False):  # pylint: disable=no-self-use
        with open(export_path, 'r') as f:
            expected = '''[c]
command = create

[storage-ls {{ url }}]
command = storage blob list --account-name {{ url.replace("https://", "").split(".")[0] }} --container-name {{ url.replace("https://", "").split("/")[1] }}

''' if not test_exclusion else '''[c]
command = create

'''
            assert f.read() == expected


if __name__ == '__main__':
    unittest.main()
