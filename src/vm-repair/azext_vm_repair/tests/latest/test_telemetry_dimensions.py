# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import gc
import unittest
from unittest.mock import Mock, patch

from azext_vm_repair import telemetry
from azext_vm_repair.command_helper_class import command_helper, script_data


RESOURCE_DIMENSIONS = {
    'os_family': 'windows',
    'vm_size': 'Standard_D2ds_v6',
    'disk_controller_type': 'NVMe',
    'repair_vm_disk_controller_type': 'SCSI',
    'hyperv_generation': 'V2'
}


class ResourceContextOnlyHelper(command_helper):
    def __del__(self):
        pass


class TelemetryDimensionTests(unittest.TestCase):

    def setUp(self):
        self.logger = Mock()

    def _track_generic(self, **resource_context):
        telemetry._track_command_telemetry(
            self.logger, 'vm repair create', {}, 'SUCCESS', '', '', '', 1.0,
            'subscription', {}, **resource_context)

    @patch.object(telemetry.tc, 'flush')
    @patch.object(telemetry.tc, 'track_event')
    def test_dimensions_present(self, track_event, _):
        self._track_generic(**RESOURCE_DIMENSIONS)

        properties = track_event.call_args.args[1]
        for name, value in RESOURCE_DIMENSIONS.items():
            self.assertEqual(value, properties[name])

    @patch.object(telemetry.tc, 'flush')
    @patch.object(telemetry.tc, 'track_event')
    def test_dimensions_default_none(self, track_event, _):
        self._track_generic()

        properties = track_event.call_args.args[1]
        for name in RESOURCE_DIMENSIONS:
            self.assertIn(name, properties)
            self.assertIsNone(properties[name])

    @patch.object(telemetry.tc, 'flush')
    @patch.object(telemetry.tc, 'track_event')
    def test_all_event_types_include_dimensions(self, track_event, _):
        telemetry._track_run_command_telemetry(
            self.logger, 'vm repair run', {}, 'SUCCESS', '', '', '', 1.0,
            'subscription', {}, 'run-id', 'SUCCESS', '', 0.5,
            **RESOURCE_DIMENSIONS)
        telemetry._track_command_telemetry_repair_and_restore(
            self.logger, 'vm repair repair-and-restore', 'SUCCESS', '', '', '',
            1.0, 'subscription', **RESOURCE_DIMENSIONS)

        self.assertEqual(2, track_event.call_count)
        for call in track_event.call_args_list:
            properties = call.args[1]
            for name, value in RESOURCE_DIMENSIONS.items():
                self.assertEqual(value, properties[name])

    @patch.object(telemetry.tc, 'flush')
    @patch.object(telemetry.tc, 'track_event')
    def test_no_customer_content(self, track_event, _):
        self._track_generic(**RESOURCE_DIMENSIONS)

        properties = track_event.call_args.args[1]
        resource_shape = {name: properties[name] for name in RESOURCE_DIMENSIONS}
        serialized_shape = str(resource_shape)
        self.assertNotIn('customer-vm-name', serialized_shape)
        self.assertNotIn('customer-resource-group', serialized_shape)
        self.assertNotIn('customer-disk-name', serialized_shape)

    def test_set_resource_context_preserves_existing_values(self):
        helper = ResourceContextOnlyHelper.__new__(ResourceContextOnlyHelper)
        helper.os_family = None
        helper.vm_size = None
        helper.disk_controller_type = None
        helper.repair_vm_disk_controller_type = None
        helper.hyperv_generation = None

        helper.set_resource_context(
            os_family='linux', vm_size='Standard_D2ds_v6',
            disk_controller_type='NVMe', hyperv_generation='V2')
        helper.set_resource_context(repair_vm_disk_controller_type='SCSI')

        self.assertEqual('linux', helper.os_family)
        self.assertEqual('Standard_D2ds_v6', helper.vm_size)
        self.assertEqual('NVMe', helper.disk_controller_type)
        self.assertEqual('SCSI', helper.repair_vm_disk_controller_type)
        self.assertEqual('V2', helper.hyperv_generation)

    @patch('azext_vm_repair.command_helper_class.get_subscription_id', return_value='subscription')
    @patch('azext_vm_repair.command_helper_class._track_command_telemetry_repair_and_restore')
    @patch('azext_vm_repair.command_helper_class._track_command_telemetry')
    @patch('azext_vm_repair.command_helper_class._track_run_command_telemetry')
    def test_run_command_emits_once(self, track_run, track_generic, track_repair_and_restore, _):
        helper = command_helper.__new__(command_helper)
        helper.start_time = 0
        helper.logger = self.logger
        helper.cmd = Mock()
        helper.command_name = 'vm repair run'
        helper.command_params = {'run_id': 'linux-alar2'}
        helper.status = 'SUCCESS'
        helper.message = ''
        helper.error_message = ''
        helper.error_stack_trace = ''
        helper.return_dict = {}
        helper.is_verbose = True
        helper.script = script_data()
        helper.os_family = 'linux'
        helper.vm_size = 'Standard_D2ds_v6'
        helper.disk_controller_type = 'NVMe'
        helper.repair_vm_disk_controller_type = 'SCSI'
        helper.hyperv_generation = 'V2'

        del helper
        gc.collect()

        track_run.assert_called_once()
        track_generic.assert_not_called()
        track_repair_and_restore.assert_not_called()


if __name__ == '__main__':
    unittest.main()
