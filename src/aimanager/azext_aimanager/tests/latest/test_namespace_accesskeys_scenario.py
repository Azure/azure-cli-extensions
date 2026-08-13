# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest.mock import MagicMock, patch

from azure.cli.testsdk import ScenarioTest

from azext_aimanager.vendored_sdks.v2026_05_02_preview import models


class NamespaceAccessKeysScenarioTest(ScenarioTest):

    def test_namespace_access_key_commands(self):
        current_access = models.NamespaceAccessInfo({
            'endpoint': 'https://namespace.example/v1',
            'primaryKey': 'primary-before',
            'secondaryKey': 'secondary-before',
        })
        rotated_access = models.NamespaceAccessInfo({
            'endpoint': 'https://namespace.example/v1',
            'primaryKey': 'primary-after',
            'secondaryKey': 'primary-before',
            'lastRotatedAt': '2026-08-12T00:00:00Z',
        })

        operations = MagicMock()
        operations.list_access_keys.return_value = current_access
        operations.rotate_keys.return_value = rotated_access
        service_client = MagicMock()
        service_client.ai_manager_namespaces = operations

        command_suffix = '-g rg -m manager -n namespace --aks-custom-headers test-header=value'
        with patch('azext_aimanager._client_factory.get_aimanager_client',
                   return_value=service_client):
            self.cmd(
                'aimanager namespace list-accesskeys ' + command_suffix,
                checks=[
                    self.check('endpoint', 'https://namespace.example/v1'),
                    self.check('primaryKey', 'primary-before'),
                    self.check('secondaryKey', 'secondary-before'),
                ])
            self.cmd(
                'aimanager namespace rotate-accesskeys ' + command_suffix + ' --yes',
                checks=[
                    self.check('primaryKey', 'primary-after'),
                    self.check('secondaryKey', 'primary-before'),
                    self.check('lastRotatedAt', '2026-08-12T00:00:00+00:00'),
                ])

        expected_headers = {'test-header': 'value'}
        operations.list_access_keys.assert_called_once_with(
            'rg', 'manager', 'namespace', headers=expected_headers)
        operations.rotate_keys.assert_called_once_with(
            'rg', 'manager', 'namespace', headers=expected_headers)
