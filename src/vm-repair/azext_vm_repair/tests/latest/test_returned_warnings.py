# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest import mock

from azext_vm_repair import custom
from azext_vm_repair.command_helper_class import command_helper


class TestCommandHelper(command_helper):
    """Command helper without progress reporting or telemetry teardown."""

    def __init__(self, logger, cmd, command_name):
        self.logger = logger
        self.command_name = command_name
        self.message = ''
        self.error_message = ''
        self.error_stack_trace = ''
        self.status = ''
        self.return_dict = {}
        self.warnings = []

    def __del__(self):
        pass

    def set_resource_context(self, **kwargs):
        pass


class ReturnedWarningsTest(unittest.TestCase):

    # The NVMe-only repair VM warning reached the operator on stderr but never entered the returned
    # JSON, so an automated caller could not tell that the repair VM it just created is one several
    # repair scripts cannot find a disk on.
    def _helper(self):
        helper = TestCommandHelper(mock.MagicMock(), None, 'vm repair create')
        helper.status = 'SUCCESS'
        helper.message = 'done'
        return helper

    def test_no_warnings_key_when_nothing_was_raised(self):
        helper = self._helper()
        self.assertNotIn('warnings', helper.init_return_dict())

    def test_warnings_are_returned_when_raised(self):
        helper = self._helper()
        helper.warnings.append('The repair VM size only supports NVMe.')
        self.assertEqual(['The repair VM size only supports NVMe.'], helper.init_return_dict()['warnings'])

    def test_returned_warnings_are_a_copy(self):
        helper = self._helper()
        helper.warnings.append('first')
        returned = helper.init_return_dict()['warnings']
        returned.append('second')
        self.assertEqual(['first'], helper.warnings)


@mock.patch('azext_vm_repair.custom.command_helper', TestCommandHelper)
class CreateWarningsTest(unittest.TestCase):

    def test_nvme_warning_is_returned_by_create(self):
        source_vm = mock.MagicMock()
        source_vm.storage_profile.os_disk.name = 'source-osdisk'
        source_vm.tags = {}
        source_vm.location = 'westus2'

        class StopAfterControllerSelection:
            def __bool__(self):
                raise RuntimeError('stop after controller selection')

        source_vm.zones = StopAfterControllerSelection()
        warning = 'The repair VM size only supports NVMe.'

        with mock.patch('azext_vm_repair.custom.get_vm', side_effect=[source_vm, mock.MagicMock()]), \
                mock.patch('azext_vm_repair.custom._is_linux_os', return_value=False), \
                mock.patch('azext_vm_repair.custom._is_gen2', return_value=True), \
                mock.patch('azext_vm_repair.custom._fetch_source_disk_controller_type', return_value='NVMe'), \
                mock.patch('azext_vm_repair.custom._set_source_resource_context'), \
                mock.patch('azext_vm_repair.custom._uses_managed_disk', return_value=True), \
                mock.patch('azext_vm_repair.custom._fetch_architecture', return_value='x64'), \
                mock.patch('azext_vm_repair.custom._fetch_compatible_windows_os_urn', return_value='image'), \
                mock.patch('azext_vm_repair.custom._fetch_compatible_sku', return_value='Standard_D2ds_v6'), \
                mock.patch('azext_vm_repair.custom._fetch_sku_disk_controller_types', return_value=['NVMe']), \
                mock.patch('azext_vm_repair.custom._select_repair_disk_controller_type', return_value=(None, 'warning', warning)), \
                mock.patch('azext_vm_repair.custom._clean_up_resources'):
            result = custom.create(mock.MagicMock(), 'source-vm', 'source-rg')

        self.assertEqual([warning], result['warnings'])

    def test_yes_deprecation_warning_is_returned_by_create(self):
        with mock.patch('azext_vm_repair.custom.get_vm', side_effect=RuntimeError('stop after warning')), \
                mock.patch('azext_vm_repair.custom._clean_up_resources'):
            result = custom.create(mock.MagicMock(), 'source-vm', 'source-rg', yes=True)

        self.assertEqual(1, len(result['warnings']))
        self.assertIn('--yes parameter is deprecated', result['warnings'][0])


@mock.patch('azext_vm_repair.custom.command_helper', TestCommandHelper)
class NestedCommandWarningsTest(unittest.TestCase):

    def _run_nested_command(self, command, **kwargs):
        create_result = {
            'repair_vm_name': 'repair-vm',
            'copied_disk_name': 'disk-copy',
            'repair_resource_group': 'repair-rg',
            'warnings': ['create warning'],
        }
        with mock.patch('azext_vm_repair.custom.get_vm', side_effect=RuntimeError('telemetry unavailable')), \
                mock.patch('azext_vm_repair.custom._check_existing_rg', return_value=False), \
                mock.patch('azext_vm_repair.custom.create', return_value=create_result), \
                mock.patch('azext_vm_repair.custom.run', return_value={'script_status': 'SUCCESS'}), \
                mock.patch('azext_vm_repair.custom.restore'), \
                mock.patch('azext_vm_repair.custom._call_az_command', return_value='repair-vm-id'):
            return command(mock.MagicMock(), 'source-vm', 'source-rg', **kwargs)

    def test_repair_and_restore_propagates_create_warnings(self):
        result = self._run_nested_command(custom.repair_and_restore)
        self.assertEqual(['create warning'], result['warnings'])

    def test_repair_button_propagates_create_and_deprecation_warnings(self):
        result = self._run_nested_command(custom.repair_button, button_command='fstab', yes=True)
        self.assertEqual(2, len(result['warnings']))
        self.assertIn('create warning', result['warnings'])
        self.assertTrue(any('--yes parameter is deprecated' in warning for warning in result['warnings']))


if __name__ == '__main__':
    unittest.main()
