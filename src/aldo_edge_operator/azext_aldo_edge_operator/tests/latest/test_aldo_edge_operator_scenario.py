# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import ScenarioTest


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AldoEdgeOperatorScenarioTest(ScenarioTest):
    def _service_test_enabled(self):
        if self.is_live:
            return True
        recording = os.path.join(TEST_DIR, 'recordings', '{}.yaml'.format(self._testMethodName))
        return os.path.exists(recording)

    def _live_setting(self, env_name, default=None, required=False):
        value = os.environ.get(env_name, default)
        if self.is_live and required and not value:
            raise AssertionError(
                'Missing required live test environment variable: {}. '
                'Set it before running with --live.'.format(env_name)
            )
        return value

    def _set_billing_kwargs(self):
        self.kwargs.update({
            'resource_id': self._live_setting(
                'ALDO_EDGE_RESOURCE_ID',
                'subscriptions/123/providers/Microsoft.Edge/disconnectedOperations/demo-resource',
                required=True,
            ),
            'resource_name': self._live_setting('ALDO_EDGE_RESOURCE_NAME', 'demo-resource', required=True),
            'stamp_id': self._live_setting('ALDO_EDGE_STAMP_ID', '12345678-FFFF-1234-1234-123456789012', required=True),
            'location': self._live_setting('ALDO_EDGE_LOCATION', 'eastus', required=True),
            'billing_model': self._live_setting('ALDO_EDGE_BILLING_MODEL', 'Capacity'),
            'connection_intent': self._live_setting('ALDO_EDGE_CONNECTION_INTENT', 'Connected'),
            'auto_renew': self._live_setting('ALDO_EDGE_AUTO_RENEW', 'Enabled'),
            'billing_status': self._live_setting('ALDO_EDGE_BILLING_STATUS', 'Enabled'),
            'current_cores': int(self._live_setting('ALDO_EDGE_CURRENT_CORES', '12')),
            'current_pricing_model': self._live_setting('ALDO_EDGE_CURRENT_PRICING_MODEL', 'Trial'),
            'current_start_date': self._live_setting('ALDO_EDGE_CURRENT_START_DATE', '2025-11-01'),
            'current_end_date': self._live_setting('ALDO_EDGE_CURRENT_END_DATE', '2025-12-31'),
            'cloud': self._live_setting('ALDO_EDGE_CLOUD', 'Public'),
            'upcoming_cores': int(self._live_setting('ALDO_EDGE_UPCOMING_CORES', '12')),
            'upcoming_pricing_model': self._live_setting('ALDO_EDGE_UPCOMING_PRICING_MODEL', 'Annual'),
            'upcoming_start_date': self._live_setting('ALDO_EDGE_UPCOMING_START_DATE', '2026-01-01'),
            'azure_hybrid_windows_server_benefit': self._live_setting(
                'ALDO_EDGE_AHWS_BENEFIT',
                'Enabled',
            ),
            'windows_server_vm_count': int(self._live_setting('ALDO_EDGE_WINDOWS_SERVER_VM_COUNT', '5')),
        })

    def test_billing_configuration_create_show_list_live_recorded(self):
        if not self._service_test_enabled():
            self.skipTest('Live service or recordings are required for this integration scenario.')

        self._set_billing_kwargs()

        create_result = self.cmd(
            'aldo-edge-operator billing-configuration create-or-update '
            '--resource-id {resource_id} '
            '--resource-name {resource_name} '
            '--stamp-id {stamp_id} '
            '--location {location} '
            '--billing-model {billing_model} '
            '--connection-intent {connection_intent} '
            '--auto-renew {auto_renew} '
            '--billing-status {billing_status} '
            '--current-cores {current_cores} '
            '--current-pricing-model {current_pricing_model} '
            '--current-start-date {current_start_date} '
            '--current-end-date {current_end_date} '
            '--cloud {cloud} '
            '--upcoming-cores {upcoming_cores} '
            '--upcoming-pricing-model {upcoming_pricing_model} '
            '--upcoming-start-date {upcoming_start_date} '
            '--azure-hybrid-windows-server-benefit {azure_hybrid_windows_server_benefit} '
            '--windows-server-vm-count {windows_server_vm_count}'
        ).get_output_in_json()

        self.assertEqual(create_result['name'], 'default')
        self.assertEqual(create_result['properties']['resourceName'], self.kwargs['resource_name'])

        show_result = self.cmd('aldo-edge-operator billing-configuration show').get_output_in_json()
        self.assertEqual(show_result['name'], 'default')
        self.assertEqual(show_result['properties']['resourceName'], self.kwargs['resource_name'])

        list_result = self.cmd('aldo-edge-operator billing-configuration list').get_output_in_json()
        self.assertTrue(any(item.get('name') == 'default' for item in list_result))

    def test_billing_configuration_snapshot_list_show_live_recorded(self):
        if not self._service_test_enabled():
            self.skipTest('Live service or recordings are required for this integration scenario.')

        snapshots = self.cmd('aldo-edge-operator billing-configuration snapshot list').get_output_in_json()
        self.assertIsInstance(snapshots, list)

        snapshot_name = self._live_setting('ALDO_EDGE_SNAPSHOT_NAME')
        if not snapshot_name and snapshots:
            snapshot_name = snapshots[0].get('name')

        if not snapshot_name:
            self.skipTest('No snapshot available. Set ALDO_EDGE_SNAPSHOT_NAME or create a snapshot in the test subscription.')

        self.kwargs.update({'snapshot_name': snapshot_name})
        snapshot = self.cmd(
            'aldo-edge-operator billing-configuration snapshot show --snapshot-name {snapshot_name}'
        ).get_output_in_json()
        self.assertEqual(snapshot['name'], snapshot_name)

    def test_billing_configuration_create_or_update_missing_required_arg_fails(self):
        with self.assertRaises(SystemExit):
            self.cmd(
                'aldo-edge-operator billing-configuration create-or-update '
                '--resource-id subscriptions/123/providers/Microsoft.Edge/disconnectedOperations/demo-resource '
                '--resource-name demo-resource '
                '--location eastus '
                '--billing-model Capacity '
                '--connection-intent Connected '
                '--auto-renew Enabled '
                '--billing-status Enabled '
                '--current-cores 12 '
                '--current-pricing-model Trial '
                '--current-start-date 2025-11-01',
                expect_failure=True,
            )

    def test_billing_configuration_create_or_update_partial_upcoming_fails(self):
        self.cmd(
            'aldo-edge-operator billing-configuration create-or-update '
            '--resource-id subscriptions/123/providers/Microsoft.Edge/disconnectedOperations/demo-resource '
            '--resource-name demo-resource '
            '--stamp-id 12345678-FFFF-1234-1234-123456789012 '
            '--location eastus '
            '--billing-model Capacity '
            '--connection-intent Connected '
            '--auto-renew Enabled '
            '--billing-status Enabled '
            '--current-cores 12 '
            '--current-pricing-model Trial '
            '--current-start-date 2025-11-01 '
            '--upcoming-cores 12',
            expect_failure=True,
        )

    def test_billing_configuration_snapshot_show_missing_snapshot_name_fails(self):
        with self.assertRaises(SystemExit):
            self.cmd('aldo-edge-operator billing-configuration snapshot show', expect_failure=True)
