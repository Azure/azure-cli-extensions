# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest.mock import MagicMock, patch

from azure.cli.testsdk import ScenarioTest
from azure.core.exceptions import ResourceNotFoundError

from azext_aimanager.vendored_sdks.v2026_05_02_preview import models


class ModelSourceScenarioTest(ScenarioTest):

    def test_modelsource_commands(self):
        source = models.ModelSource({
            'name': 'hf',
            'eTag': 'etag-value',
            'properties': {
                'provisioningState': 'Succeeded',
                'sourceType': 'HuggingFace',
                'description': 'Team catalog',
            },
        })

        operations = MagicMock()
        operations.get.side_effect = [
            ResourceNotFoundError(),
            source,
            source,
            source,
            source,
        ]
        operations.list.return_value = [source]
        service_client = MagicMock()
        service_client.model_sources = operations

        command_prefix = 'aimanager modelsource {} -g rg --aimanager-name manager'

        with patch('azext_aimanager._client_factory.get_aimanager_client',
                   return_value=service_client):
            self.cmd(
                command_prefix.format('add') +
                ' -n hf -s HuggingFace --credential hf_token '
                '--description "Team catalog" --no-wait',
                checks=[self.is_empty()])

            self.cmd(
                command_prefix.format('wait') +
                ' -n hf --created --timeout 1',
                checks=[self.is_empty()])

            self.cmd(
                command_prefix.format('show') + ' -n hf',
                checks=[
                    self.check('name', 'hf'),
                    self.check('properties.sourceType', 'HuggingFace'),
                    self.check('properties.description', 'Team catalog'),
                ])

            self.cmd(
                command_prefix.format('list'),
                checks=[self.check("length([?name=='hf'])", 1)])

            self.cmd(
                command_prefix.format('update') +
                ' -n hf --description "Updated catalog" --no-wait',
                checks=[self.is_empty()])

            self.cmd(
                command_prefix.format('delete') + ' -n hf --yes --no-wait',
                checks=[self.is_empty()])

        self.assertEqual(operations.begin_create_or_update.call_count, 2)
        self.assertEqual(operations.get.call_count, 5)
        operations.list.assert_called_once_with('rg', 'manager')
        operations.begin_delete.assert_called_once()
