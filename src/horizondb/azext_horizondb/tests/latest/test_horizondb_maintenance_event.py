# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest.mock import patch

from azure.cli.testsdk import ScenarioTest

from .constants import INDIASOUTHCENTRAL, CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH
from .recording_processors import ArmOperationResultsRecordingProcessor


class HorizonDBMaintenanceEventScenarioTest(ScenarioTest):

    def __init__(self, method_name):
        processor = ArmOperationResultsRecordingProcessor()
        super().__init__(
            method_name,
            recording_processors=[processor],
            replay_processors=[processor],
        )

    def test_horizondb_maintenance_event_list(self):
        self.kwargs.update({
            'rg': self.create_random_name('cli_test_horizondb_maintenance_', 64),
            'location': INDIASOUTHCENTRAL,
            'cluster': self.create_random_name(CLUSTER_NAME_PREFIX, CLUSTER_NAME_MAX_LENGTH),
            'pool': self.create_random_name('pool-', 24),
        })

        # Record the fixture lifecycle without provisioning any HorizonDB resources.
        self.addCleanup(self.cmd, 'group delete --name {rg} --yes')
        self.cmd(
            'group create --name {rg} --location {location} '
            '--tags product=azurecli module=horizondb',
            checks=[self.check('name', '{rg}')],
        )

        expected = (
            'Maintenance updates are managed by the system. '
            'Currently, HorizonDB supports System-Managed Maintenance Window.'
        )
        command = (
            'horizondb cluster pool maintenance-event list --resource-group {rg} '
            '--cluster-name {cluster} --pool-name {pool}'
        )
        with patch(
            'azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client',
            side_effect=AssertionError('Maintenance information must not create an HTTP client.'),
        ) as http_client, patch(
            'requests.sessions.Session.request',
            side_effect=AssertionError('Maintenance information must not send network requests.'),
        ) as request:
            for output_format in ['json', 'tsv']:
                with self.subTest(output_format=output_format):
                    result = self.cmd(command + ' --output ' + output_format)
                    value = result.get_output_in_json() if output_format == 'json' else result.output.strip()
                    self.assertEqual(value, expected)
            http_client.assert_not_called()
            request.assert_not_called()
