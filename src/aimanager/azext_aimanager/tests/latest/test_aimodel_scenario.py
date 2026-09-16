# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest.mock import MagicMock, patch

from azure.cli.testsdk import ScenarioTest

from azext_aimanager.vendored_sdks.v2026_05_02_preview import models


class AIModelScenarioTest(ScenarioTest):

    def test_aimodel_commands(self):
        ai_model = models.AIModel({
            'name': '9806f0c862fdd920',
            'properties': {
                'modelId': 'microsoft/Phi-4-mini-instruct',
                'description': 'A small language model.',
                'spec': {'contextLength': 131072},
            },
        })
        calculate_cost_response = models.CalculateCostResponse({
            'currency': 'USD',
            'plans': [
                {
                    'vmSize': 'Standard_NC24ads_A100_v4',
                    'quantization': 'fp8',
                    'vmsPerReplica': 1,
                    'maxAvailableReplicas': 4,
                    'vmHourlyPrice': 3.67,
                    'totalHourlyPrice': 3.67,
                    'feasible': True,
                },
                {
                    'vmSize': 'Standard_ND96isr_H100_v5',
                    'vmsPerReplica': 1,
                    'maxAvailableReplicas': 0,
                    'vmHourlyPrice': 98.32,
                    'feasible': False,
                    'infeasibilityReason': {'code': 'InsufficientQuota'},
                },
            ],
        })

        operations = MagicMock()
        operations.get.return_value = ai_model
        operations.list.return_value = [ai_model]
        operations.calculate_cost.return_value = calculate_cost_response
        service_client = MagicMock()
        service_client.ai_models = operations

        with patch('azext_aimanager._client_factory.get_aimanager_client',
                   return_value=service_client):
            self.cmd(
                'aimanager model show -l eastus2 -n 9806f0c862fdd920',
                checks=[
                    self.check('name', '9806f0c862fdd920'),
                    self.check('properties.modelId', 'microsoft/Phi-4-mini-instruct'),
                ])

            self.cmd(
                'aimanager model list -l eastus2',
                checks=[self.check("length([?name=='9806f0c862fdd920'])", 1)])

            self.cmd(
                'aimanager model calculate-cost -l eastus2 -n 9806f0c862fdd920',
                checks=[
                    self.check('currency', 'USD'),
                    self.check('length(plans)', 2),
                    self.check('plans[0].vmSize', 'Standard_NC24ads_A100_v4'),
                    self.check('plans[0].feasible', True),
                    self.check('plans[0].totalHourlyPrice', 3.67),
                    self.check('plans[1].feasible', False),
                    self.check('plans[1].infeasibilityReason.code', 'InsufficientQuota'),
                ])

        operations.get.assert_called_once_with('eastus2', '9806f0c862fdd920')
        operations.list.assert_called_once_with('eastus2')
        operations.calculate_cost.assert_called_once()
        self.assertEqual(
            operations.calculate_cost.call_args[0][:2], ('eastus2', '9806f0c862fdd920'))
