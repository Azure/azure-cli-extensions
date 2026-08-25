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
        model_source = models.ModelSource({
            'name': 'hf',
            'properties': {
                'sourceType': 'HuggingFace',
                'description': 'Hugging Face registry',
                'provisioningState': 'Succeeded',
            },
        })

        operations = MagicMock()
        operations.get.side_effect = [
            # add -> not found, then show / update / delete each read the resource once
            ResourceNotFoundError(),
            model_source,
            model_source,
            model_source,
        ]
        operations.list.return_value = [model_source]
        service_client = MagicMock()
        service_client.model_sources = operations

        command_prefix = 'aimanager modelsource {} -g rg --aimanager-name manager'

        with patch('azext_aimanager._client_factory.get_aimanager_client',
                   return_value=service_client):
            self.cmd(
                command_prefix.format('add') +
                ' -n hf -s HuggingFace --token hf_xxx --description "Hugging Face registry" --no-wait',
                checks=[self.is_empty()])

            self.cmd(
                command_prefix.format('show') + ' -n hf',
                checks=[
                    self.check('name', 'hf'),
                    self.check('properties.sourceType', 'HuggingFace'),
                    self.check('properties.description', 'Hugging Face registry'),
                ])

            self.cmd(
                command_prefix.format('list'),
                checks=[self.check("length([?name=='hf'])", 1)])

            self.cmd(
                'aimanager modelsource list -g rg --manager manager',
                checks=[self.check("length([?name=='hf'])", 1)])

            self.cmd(
                command_prefix.format('update') + ' -n hf --token hf_yyy --no-wait',
                checks=[self.is_empty()])

            self.cmd(
                command_prefix.format('delete') + ' -n hf --yes --no-wait',
                checks=[self.is_empty()])

        self.assertEqual(operations.get.call_count, 4)
        self.assertEqual(operations.begin_create_or_update.call_count, 2)
        self.assertEqual(operations.list.call_count, 2)
        operations.list.assert_called_with('rg', 'manager')
        operations.begin_delete.assert_called_once()

        # the source type is immutable and must be carried over on update
        update_payload = operations.begin_create_or_update.call_args_list[1][0][3]
        self.assertEqual(update_payload.properties.source_type, 'HuggingFace')
        self.assertEqual(update_payload.properties.credential.inline.value, 'hf_yyy')
