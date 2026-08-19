# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest.mock import MagicMock, patch

from azure.cli.testsdk import ScenarioTest

from azext_aimanager.vendored_sdks.v2026_05_02_preview import models


class NamespaceAccessKeysScenarioTest(ScenarioTest):

    def test_namespace_accesskeys_commands(self):
        access_info = models.NamespaceAccessInfo({
            'endpoint': 'https://team-alpha.example.eastus2.aksapp.io/v1',
            'primaryKey': 'primary-key-value',
            'secondaryKey': 'secondary-key-value',
        })
        rotated_info = models.NamespaceAccessInfo({
            'endpoint': 'https://team-alpha.example.eastus2.aksapp.io/v1',
            'primaryKey': 'new-primary-key-value',
            'secondaryKey': 'primary-key-value',
            'lastRotatedAt': '2026-08-14T00:00:00Z',
        })

        operations = MagicMock()
        operations.list_access_keys.return_value = access_info
        operations.rotate_keys.return_value = rotated_info
        service_client = MagicMock()
        service_client.ai_manager_namespaces = operations

        command_prefix = 'aimanager namespace {} -g rg --aimanager-name manager -n namespace'

        with patch('azext_aimanager._client_factory.get_aimanager_client',
                   return_value=service_client):
            self.cmd(
                command_prefix.format('list-accesskeys'),
                checks=[
                    self.check('endpoint', 'https://team-alpha.example.eastus2.aksapp.io/v1'),
                    self.check('primaryKey', 'primary-key-value'),
                    self.check('secondaryKey', 'secondary-key-value'),
                ])

            # the previous primary key is demoted to the secondary key on rotation
            self.cmd(
                command_prefix.format('rotate-accesskeys') + ' --yes',
                checks=[
                    self.check('primaryKey', 'new-primary-key-value'),
                    self.check('secondaryKey', 'primary-key-value'),
                ])

            # -m/--manager remains accepted for backwards compatibility
            self.cmd(
                'aimanager namespace list-accesskeys -g rg -m manager -n namespace',
                checks=[self.check('primaryKey', 'primary-key-value')])

            operations.list_access_keys.assert_called_with(
                'rg', 'manager', 'namespace', headers={})

            # --aks-custom-headers is parsed and forwarded to the request
            self.cmd(
                command_prefix.format('list-accesskeys') + ' --aks-custom-headers a=1,b=2',
                checks=[self.check('primaryKey', 'primary-key-value')])

        operations.list_access_keys.assert_called_with(
            'rg', 'manager', 'namespace', headers={'a': '1', 'b': '2'})
        operations.rotate_keys.assert_called_once_with('rg', 'manager', 'namespace', headers={})
