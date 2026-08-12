# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest.mock import MagicMock, patch

from azure.cli.testsdk import ScenarioTest

from azext_aimanager.vendored_sdks.v2026_05_02_preview import models


class AIModelScenarioTest(ScenarioTest):

    def test_aimanager_model_commands(self):
        model = models.AIModel({
            'name': 'phi-4',
            'properties': {
                'modelId': 'microsoft/phi-4',
                'description': 'Phi-4',
                'spec': {
                    'license': 'mit',
                    'isRestricted': False,
                    'maxContextLength': 16384,
                },
            },
        })

        operations = MagicMock()
        operations.get.return_value = model
        operations.list.return_value = [model]
        service_client = MagicMock()
        service_client.ai_models = operations

        with patch('azext_aimanager._client_factory.get_aimanager_client',
                   return_value=service_client):
            self.cmd(
                'aimanager model show -l eastus2 -n phi-4',
                checks=[
                    self.check('name', 'phi-4'),
                    self.check('properties.modelId', 'microsoft/phi-4'),
                ])

            self.cmd(
                'aimanager model list -l eastus2',
                checks=[self.check("length([?name=='phi-4'])", 1)])

        operations.get.assert_called_once_with('eastus2', 'phi-4')
        operations.list.assert_called_once_with('eastus2')
