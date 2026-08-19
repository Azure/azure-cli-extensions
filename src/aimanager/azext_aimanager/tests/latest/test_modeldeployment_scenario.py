# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest.mock import MagicMock, patch

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.testsdk import ScenarioTest
from azure.core.exceptions import ResourceNotFoundError

from azext_aimanager.vendored_sdks.v2026_05_02_preview import models


class ModelDeploymentScenarioTest(ScenarioTest):

    def test_modeldeployment_commands(self):
        model_resource_id = (
            '/subscriptions/00000000-0000-0000-0000-000000000000/providers/'
            'Microsoft.ContainerService/locations/eastus2/aiModels/phi-4')
        model_source_resource_id = (
            '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/'
            'providers/Microsoft.ContainerService/aiManagers/manager/modelSources/source')
        deployment = models.ModelDeployment({
            'name': 'deployment',
            'eTag': 'etag-value',
            'properties': {
                'modelResourceId': model_resource_id,
                'modelSourceResourceId': model_source_resource_id,
                'performanceMode': 'Balanced',
                'vmSize': 'Standard_NC24ads_A100_v4',
                'scale': {'manual': {'replicas': 0}},
                'overrides': {'values': {'engine': 'vllm'}},
            },
        })

        operations = MagicMock()
        operations.get.side_effect = [
            ResourceNotFoundError(),
            ResourceNotFoundError(),
            deployment,
            deployment,
            deployment,
            deployment,
        ]
        operations.list_by_ai_manager_namespace.return_value = [deployment]
        service_client = MagicMock()
        service_client.model_deployments = operations

        command_prefix = (
            'aimanager namespace modeldeployment {} -g rg '
            '--aimanager-name manager --namespace-name namespace')

        with patch('azext_aimanager._client_factory.get_aimanager_client',
                   return_value=service_client):
            with self.assertRaisesRegex(
                    InvalidArgumentValueError,
                    '--replicas cannot be combined with --min-replicas or --max-replicas'):
                self.cmd(
                    command_prefix.format('add') +
                    ' -n deployment --model-resource-id {} '
                    '--vm-size Standard_NC24ads_A100_v4 '
                    '--replicas 1 --min-replicas 1'.format(model_resource_id))

            self.cmd(
                command_prefix.format('add') +
                ' -n deployment --model-resource-id {} '
                '--source-id {} '
                '--vm-size Standard_NC24ads_A100_v4 --replicas 0 '
                '--performance-mode Balanced --overrides engine=vllm --no-wait'.format(
                    model_resource_id, model_source_resource_id),
                checks=[self.is_empty()])

            self.cmd(
                command_prefix.format('wait') +
                ' -n deployment --created --timeout 1',
                checks=[self.is_empty()])

            self.cmd(
                command_prefix.format('show') + ' -n deployment',
                checks=[
                    self.check('name', 'deployment'),
                    self.check('properties.modelResourceId', model_resource_id),
                    self.check('properties.modelSourceResourceId', model_source_resource_id),
                    self.check('properties.scale.manual.replicas', 0),
                ])

            self.cmd(
                command_prefix.format('list'),
                checks=[self.check("length([?name=='deployment'])", 1)])

            self.cmd(
                'aimanager namespace modeldeployment list -g rg '
                '-m manager --namespace-name namespace',
                checks=[self.check("length([?name=='deployment'])", 1)])

            self.cmd(
                command_prefix.format('update') +
                ' -n deployment --performance-mode Throughput --replicas 0 '
                '--overrides engine=vllm max-model-len=4096 --no-wait',
                checks=[self.is_empty()])

            self.cmd(
                command_prefix.format('delete') +
                ' -n deployment --yes --no-wait',
                checks=[self.is_empty()])

        self.assertEqual(operations.begin_create_or_update.call_count, 2)
        self.assertEqual(operations.list_by_ai_manager_namespace.call_count, 2)
        operations.list_by_ai_manager_namespace.assert_called_with(
            'rg', 'manager', 'namespace')
        operations.begin_delete.assert_called_once()
