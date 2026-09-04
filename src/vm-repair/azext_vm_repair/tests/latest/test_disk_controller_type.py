# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access
import unittest
from unittest import mock

from knack.util import CLIError

from azext_vm_repair._validators import validate_create
from azext_vm_repair.repair_utils import (
    _fetch_sku_disk_controller_types,
    _fetch_source_disk_controller_type,
    _select_repair_disk_controller_type,
)


class SelectRepairDiskControllerTypeTest(unittest.TestCase):

    def test_scsi_source_no_flag(self):
        controller, level, _ = _select_repair_disk_controller_type('SCSI', ['SCSI', 'NVMe'])
        self.assertIsNone(controller)
        self.assertEqual('debug', level)

    def test_nvme_source_pins_scsi(self):
        controller, level, message = _select_repair_disk_controller_type('NVMe', ['SCSI', 'NVMe'])
        self.assertEqual('SCSI', controller)
        self.assertEqual('info', level)
        self.assertIn('enumerate', message)

    def test_nvme_only_size_warns(self):
        controller, level, message = _select_repair_disk_controller_type('NVMe', ['NVMe'])
        self.assertIsNone(controller)
        self.assertEqual('warning', level)
        self.assertIn('only supports NVMe', message)

    def test_explicit_override_wins(self):
        controller, level, _ = _select_repair_disk_controller_type('SCSI', ['SCSI', 'NVMe'], 'NVMe')
        self.assertEqual('NVMe', controller)
        self.assertEqual('info', level)

    def test_unknown_capability_no_flag(self):
        controller, level, _ = _select_repair_disk_controller_type('NVMe', [])
        self.assertIsNone(controller)
        self.assertEqual('debug', level)


class FetchDiskControllerTypeTest(unittest.TestCase):

    def test_source_controller_uses_sdk_value(self):
        source_vm = mock.MagicMock()
        source_vm.storage_profile.disk_controller_type = 'NVMe'
        self.assertEqual('NVMe', _fetch_source_disk_controller_type(source_vm))

    @mock.patch('azext_vm_repair.repair_utils._call_az_command', return_value='SCSI\n')
    def test_source_controller_falls_back_to_cli(self, mock_call):
        source_vm = mock.MagicMock()
        source_vm.storage_profile = mock.MagicMock(spec=[])
        source_vm.id = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm'
        self.assertEqual('SCSI', _fetch_source_disk_controller_type(source_vm))
        self.assertIn('storageProfile.diskControllerType', mock_call.call_args[0][0])

    @mock.patch('azext_vm_repair.repair_utils._call_az_command', return_value='SCSI,NVMe\n')
    def test_sku_capabilities_are_parsed(self, _):
        self.assertEqual(['SCSI', 'NVMe'], _fetch_sku_disk_controller_types('Standard_E2bds_v5', 'westus2'))


class ValidateDiskControllerTypeTest(unittest.TestCase):

    def _validate(self, value):
        namespace = mock.MagicMock()
        namespace.disk_controller_type = value
        with mock.patch('azext_vm_repair._validators.check_extension_version', side_effect=RuntimeError):
            with self.assertRaises(RuntimeError):
                validate_create(mock.MagicMock(), namespace)
        return namespace.disk_controller_type

    def test_scsi_is_normalized(self):
        self.assertEqual('SCSI', self._validate(' scsi '))

    def test_nvme_is_normalized(self):
        self.assertEqual('NVMe', self._validate('nvme'))

    def test_invalid_value_is_rejected_before_network_call(self):
        namespace = mock.MagicMock(disk_controller_type='SCSI; rm -rf')
        with mock.patch('azext_vm_repair._validators.check_extension_version') as mock_version:
            with self.assertRaises(CLIError):
                validate_create(mock.MagicMock(), namespace)
        mock_version.assert_not_called()
