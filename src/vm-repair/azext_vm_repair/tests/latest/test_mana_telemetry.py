# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import gc
import json
import unittest
from unittest.mock import Mock, patch

from azext_vm_repair import custom, telemetry


RESET_NIC_DIMENSIONS = {
    'sourceAN': 'unknown',
    'sourceVfVendor': 'unknown',
    'guestManaPresent': 'unknown',
    'resetNicMode': 'legacy',
    'postResetHealthy': 'unknown'
}


class ResetNicTelemetryTests(unittest.TestCase):

    @patch.object(telemetry.tc, 'flush')
    @patch.object(telemetry.tc, 'track_event')
    def test_markers_are_unmeasured_on_success_and_failure(self, track_event, flush):
        for status in ('SUCCESS', 'ERROR'):
            with self.subTest(status=status):
                telemetry._track_command_telemetry(
                    Mock(), 'vm repair reset-nic', {}, status, '', '', '', 1.0,
                    'subscription', {})
                properties = track_event.call_args.args[1]
                self.assertEqual(status, properties['command_status'])
                for name, value in RESET_NIC_DIMENSIONS.items():
                    self.assertEqual(value, properties[name])
                self.assertEqual({'command_duration': 1.0}, track_event.call_args.args[2])
        self.assertEqual(2, track_event.call_count)
        self.assertEqual(2, flush.call_count)

    @patch.object(telemetry.tc, 'flush')
    @patch.object(telemetry.tc, 'track_event')
    def test_other_commands_do_not_gain_reset_markers(self, track_event, _):
        telemetry._track_command_telemetry(
            Mock(), 'vm repair create', {}, 'SUCCESS', '', '', '', 1.0,
            'subscription', {})
        telemetry._track_run_command_telemetry(
            Mock(), 'vm repair run', {}, 'SUCCESS', '', '', '', 1.0,
            'subscription', {}, 'run-id', 'SUCCESS', '', 0.5)
        telemetry._track_command_telemetry_repair_and_restore(
            Mock(), 'vm repair repair-and-restore', 'SUCCESS', '', '', '',
            1.0, 'subscription')
        for call in track_event.call_args_list:
            self.assertTrue(RESET_NIC_DIMENSIONS.keys().isdisjoint(call.args[1]))

    @patch.object(telemetry.tc, 'flush')
    @patch.object(telemetry.tc, 'track_event')
    @patch('azext_vm_repair.command_helper_class.get_subscription_id', return_value='subscription')
    @patch('azext_vm_repair.command_helper_class._get_function_param_dict', return_value={})
    @patch('azext_vm_repair.custom.get_vm_by_aaz', side_effect=custom.AzCommandError('VM unavailable'))
    @patch('azext_vm_repair.custom._call_az_command')
    def test_failure_emits_markers_without_network_mutation(
            self, call_az, get_vm, get_params, get_subscription, track_event, flush):
        result = custom.reset_nic(Mock(), 'test-vm', 'test-group', yes=True)
        # Release mock-held frames so the real helper's telemetry teardown can run.
        get_params.reset_mock()
        get_vm.side_effect.__traceback__ = None
        get_vm.side_effect = None
        gc.collect()
        self.assertEqual('ERROR', result['status'])
        call_az.assert_not_called()
        track_event.assert_called_once()
        flush.assert_called_once()
        properties = track_event.call_args.args[1]
        for name, value in RESET_NIC_DIMENSIONS.items():
            self.assertEqual(value, properties[name])

    @patch.object(telemetry.tc, 'flush')
    @patch.object(telemetry.tc, 'track_event')
    @patch('azext_vm_repair.command_helper_class.get_subscription_id', return_value='subscription')
    @patch('azext_vm_repair.command_helper_class._get_function_param_dict', return_value={})
    @patch('azext_vm_repair.custom.get_vm_by_aaz')
    @patch('azext_vm_repair.custom._check_n_start_vm', return_value=True)
    @patch('azext_vm_repair.custom._call_az_command')
    def test_success_preserves_legacy_calls_without_claiming_health(
            self, call_az, start_vm, get_vm, get_params, get_subscription, track_event, flush):
        call_az.side_effect = [
            '/subscriptions/s/resourceGroups/test-group/providers/Microsoft.Network/networkInterfaces/nic',
            json.dumps({
                'name': 'ipconfig',
                'subnet': {
                    'id': '/subscriptions/s/resourceGroups/test-group/providers/'
                          'Microsoft.Network/virtualNetworks/vnet/subnets/subnet'
                },
                'privateIPAddress': '192.0.2.10',
                'privateIPAllocationMethod': 'Static'
            }),
            '192.0.2.11', '', '', ''
        ]
        result = custom.reset_nic(Mock(), 'test-vm', 'test-group', yes=True)
        get_params.reset_mock()
        gc.collect()
        self.assertEqual('SUCCESS', result['status'])
        self.assertEqual(6, call_az.call_count)
        self.assertIn('192.0.2.10', call_az.call_args.args[0])
        track_event.assert_called_once()
        flush.assert_called_once()
        properties = track_event.call_args.args[1]
        for name, value in RESET_NIC_DIMENSIONS.items():
            self.assertEqual(value, properties[name])


if __name__ == '__main__':
    unittest.main()
