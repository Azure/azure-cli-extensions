# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import unittest
from unittest.mock import MagicMock, patch


def _make_cmd():
    cmd = MagicMock()
    cmd.cli_ctx = MagicMock()
    cmd.cli_ctx.cloud.endpoints.resource_manager = 'https://management.azure.com/'
    return cmd


def _make_response(payload):
    response = MagicMock()
    response.json.return_value = payload
    return response


class BillingConfigurationCustomTests(unittest.TestCase):

    @patch('azext_aldo_edge_operator.custom.get_subscription_id', return_value='12345678-1234-1234-1234-123456789012')
    @patch('azext_aldo_edge_operator.custom.send_raw_request')
    def test_show_billing_configuration(self, mock_send, _mock_sub_id):
        from azext_aldo_edge_operator.custom import show_billing_configuration

        mock_send.return_value = _make_response({'name': 'default'})

        result = show_billing_configuration(_make_cmd())

        self.assertEqual(result['name'], 'default')
        request_args = mock_send.call_args[0]
        self.assertEqual(request_args[1], 'GET')
        self.assertIn('/billingConfigurations/default?api-version=', request_args[2])

    @patch('azext_aldo_edge_operator.custom.get_subscription_id', return_value='12345678-1234-1234-1234-123456789012')
    @patch('azext_aldo_edge_operator.custom.send_raw_request')
    def test_create_or_update_billing_configuration(self, mock_send, _mock_sub_id):
        from azext_aldo_edge_operator.custom import create_or_update_billing_configuration

        mock_send.return_value = _make_response({'name': 'default'})

        result = create_or_update_billing_configuration(
            _make_cmd(),
            'subscriptions/123/providers/Microsoft.Edge/disconnectedOperations/demo-resource',
            'demo-resource',
            '12345678-FFFF-1234-1234-123456789012',
            'eastus',
            'Capacity',
            'Connected',
            'Enabled',
            'Enabled',
            12,
            'Trial',
            '2025-11-01',
            '2025-12-31',
            'Public',
            12,
            'Annual',
            '2026-01-01',
            None,
            'Enabled',
            5,
        )

        expected_payload = {
            'properties': {
                'resourceId': 'subscriptions/123/providers/Microsoft.Edge/disconnectedOperations/demo-resource',
                'resourceName': 'demo-resource',
                'stampId': '12345678-FFFF-1234-1234-123456789012',
                'location': 'eastus',
                'billingModel': 'Capacity',
                'connectionIntent': 'Connected',
                'cloud': 'Public',
                'billingConfiguration': {
                    'autoRenew': 'Enabled',
                    'billingStatus': 'Enabled',
                    'current': {
                        'cores': 12,
                        'pricingModel': 'Trial',
                        'startDate': '2025-11-01',
                        'endDate': '2025-12-31',
                    },
                    'upcoming': {
                        'cores': 12,
                        'pricingModel': 'Annual',
                        'startDate': '2026-01-01',
                    },
                },
                'benefitPlans': {
                    'azureHybridWindowsServerBenefit': 'Enabled',
                    'windowsServerVmCount': 5,
                },
            }
        }

        self.assertEqual(result['name'], 'default')
        request_args = mock_send.call_args[0]
        self.assertEqual(request_args[1], 'PUT')
        self.assertIn('/billingConfigurations/default?api-version=', request_args[2])
        self.assertEqual(json.loads(mock_send.call_args.kwargs['body']), expected_payload)

    @patch('azext_aldo_edge_operator.custom.get_subscription_id', return_value='12345678-1234-1234-1234-123456789012')
    @patch('azext_aldo_edge_operator.custom.send_raw_request')
    def test_create_or_update_billing_configuration_rejects_partial_upcoming(self, mock_send, _mock_sub_id):
        from azext_aldo_edge_operator.custom import create_or_update_billing_configuration

        with self.assertRaisesRegex(Exception, 'upcoming billing period'):
            create_or_update_billing_configuration(
                _make_cmd(),
                'subscriptions/123/providers/Microsoft.Edge/disconnectedOperations/demo-resource',
                'demo-resource',
                '12345678-FFFF-1234-1234-123456789012',
                'eastus',
                'Capacity',
                'Connected',
                'Enabled',
                'Enabled',
                12,
                'Trial',
                '2025-11-01',
                None,
                None,
                12,
                None,
                '2026-01-01',
            )

        mock_send.assert_not_called()

    @patch('azext_aldo_edge_operator.custom.get_subscription_id', return_value='12345678-1234-1234-1234-123456789012')
    @patch('azext_aldo_edge_operator.custom.send_raw_request')
    def test_list_billing_configuration_snapshots(self, mock_send, _mock_sub_id):
        from azext_aldo_edge_operator.custom import list_billing_configuration_snapshots

        mock_send.return_value = _make_response({'value': [{'name': 'abc123'}]})

        result = list_billing_configuration_snapshots(_make_cmd())

        self.assertEqual(result[0]['name'], 'abc123')
        request_args = mock_send.call_args[0]
        self.assertEqual(request_args[1], 'GET')
        self.assertIn('/billingConfigurations/default/snapshots?api-version=', request_args[2])