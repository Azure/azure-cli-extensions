# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from unittest import mock

from azext_vm_repair import custom
from azext_vm_repair.command_helper_class import command_helper
from azext_vm_repair.repair_utils import NVME_ONLY_REPAIR_VM_WARNING


class TestCommandHelper(command_helper):
    """Command helper without progress reporting or telemetry teardown."""

    instances = []

    def __init__(self, logger, cmd, command_name):
        self.logger = logger
        self.command_name = command_name
        self.message = ''
        self.error_message = ''
        self.error_stack_trace = ''
        self.status = ''
        self.return_dict = {}
        self.warnings = []
        self.warning_codes = []
        self.nested_script_failed = False
        self.nested_script_diagnostic = None
        TestCommandHelper.instances.append(self)

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
        returned = helper.init_return_dict()
        self.assertEqual(['The repair VM size only supports NVMe.'], returned['warnings'])
        self.assertNotIn('warning_codes', returned)

    def test_returned_warnings_are_a_copy(self):
        helper = self._helper()
        helper.warnings.append('first')
        returned = helper.init_return_dict()['warnings']
        returned.append('second')
        self.assertEqual(['first'], helper.warnings)


@mock.patch('azext_vm_repair.custom.command_helper', TestCommandHelper)
class CreateWarningsTest(unittest.TestCase):

    def test_nvme_warning_is_returned_by_create(self):
        source_vm = {
            'storageProfile': {'osDisk': {'name': 'source-osdisk'}},
            'hardwareProfile': {'vmSize': 'Standard_D2ds_v6'},
            'tags': {},
            'location': 'westus2'
        }
        warning = NVME_ONLY_REPAIR_VM_WARNING
        TestCommandHelper.instances = []

        with mock.patch('azext_vm_repair.custom.get_vm_by_aaz', side_effect=[source_vm, mock.MagicMock()]), \
                mock.patch('azext_vm_repair.custom._is_linux_os_aaz', return_value=False), \
                mock.patch('azext_vm_repair.custom._is_gen2', return_value=True), \
                mock.patch('azext_vm_repair.custom._fetch_source_disk_controller_type', return_value='NVMe'), \
                mock.patch('azext_vm_repair.custom._set_source_resource_context'), \
                mock.patch('azext_vm_repair.custom._uses_managed_disk', return_value=True), \
                mock.patch('azext_vm_repair.custom._fetch_architecture', return_value='x64'), \
                mock.patch('azext_vm_repair.custom._fetch_compatible_windows_os_urn', return_value='image'), \
                mock.patch('azext_vm_repair.custom._fetch_compatible_sku', return_value='Standard_D2ds_v6'), \
                mock.patch('azext_vm_repair.custom._fetch_sku_disk_controller_types', return_value=['NVMe']), \
                mock.patch('azext_vm_repair.custom._select_repair_disk_controller_type', return_value=(None, 'warning', warning)), \
                mock.patch('azext_vm_repair.custom._check_existing_rg', side_effect=RuntimeError('stop after warning')), \
                mock.patch('azext_vm_repair.custom._clean_up_resources'):
            result = custom.create(
                mock.MagicMock(), 'source-vm', 'source-rg',
                repair_username='repair-user', repair_password='repair-password',
                repair_vm_name='repair-vm', copy_disk_name='disk-copy',
                repair_group_name='repair-rg')

        self.assertEqual([warning], result['warnings'])
        self.assertNotIn('warning_codes', result)
        self.assertEqual(['REPAIR_VM_NVME_ONLY'], TestCommandHelper.instances[0].warning_codes)

    def test_yes_deprecation_warning_is_returned_by_create(self):
        TestCommandHelper.instances = []
        with mock.patch('azext_vm_repair.custom.get_vm_by_aaz', side_effect=RuntimeError('stop after warning')), \
                mock.patch('azext_vm_repair.custom._clean_up_resources'):
            result = custom.create(mock.MagicMock(), 'source-vm', 'source-rg', yes=True)

        self.assertEqual(1, len(result['warnings']))
        self.assertIn('--yes parameter is deprecated', result['warnings'][0])
        self.assertEqual(['YES_PARAMETER_DEPRECATED'], TestCommandHelper.instances[0].warning_codes)


@mock.patch('azext_vm_repair.custom.command_helper', TestCommandHelper)
class NestedCommandWarningsTest(unittest.TestCase):

    def _run_nested_command(self, command, run_out=None, restore_out=None, create_warnings=None, **kwargs):
        TestCommandHelper.instances = []
        create_result = {
            'repair_vm_name': 'repair-vm',
            'copied_disk_name': 'disk-copy',
            'repair_resource_group': 'repair-rg',
            'warnings': ['create warning'] if create_warnings is None else create_warnings,
        }
        with mock.patch('azext_vm_repair.custom.get_vm_by_aaz', side_effect=RuntimeError('telemetry unavailable')), \
                mock.patch('azext_vm_repair.custom._check_existing_rg', return_value=False), \
                mock.patch('azext_vm_repair.custom.create', return_value=create_result), \
                mock.patch('azext_vm_repair.custom.run', return_value=run_out or {'script_status': 'SUCCESS'}), \
                mock.patch('azext_vm_repair.custom.restore', return_value=restore_out or {'status': 'SUCCESS'}), \
                mock.patch('azext_vm_repair.custom._clean_up_resources'), \
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

    def test_warning_codes_follow_warnings_through_nested_commands_without_being_returned(self):
        result = self._run_nested_command(
            custom.repair_button, button_command='fstab', yes=True,
            create_warnings=[NVME_ONLY_REPAIR_VM_WARNING, 'unclassified warning'])

        self.assertNotIn('warning_codes', result)
        self.assertEqual(
            ['YES_PARAMETER_DEPRECATED', 'REPAIR_VM_NVME_ONLY', 'ADVISORY_WARNING'],
            TestCommandHelper.instances[0].warning_codes)
        self.assertEqual(len(TestCommandHelper.instances[0].warnings),
                         len(TestCommandHelper.instances[0].warning_codes))

    def test_script_error_keeps_warnings_and_failure_details(self):
        for command, kwargs in ((custom.repair_and_restore, {}),
                                (custom.repair_button, {'button_command': 'fstab'})):
            with self.subTest(command=command.__name__):
                result = self._run_nested_command(
                    command, run_out={'script_status': 'ERROR', 'output': 'script failed'}, **kwargs)

                self.assertEqual('ERROR', result['status'])
                self.assertIn('script returned an error', result['error_message'])
                self.assertEqual(['create warning'], result['warnings'])

                helper = TestCommandHelper.instances[0]
                self.assertTrue(helper.nested_script_failed)
                self.assertEqual('script failed', helper.nested_script_diagnostic)

    def test_restore_error_keeps_warnings_and_failure_details(self):
        restore_out = {'status': 'ERROR', 'message': 'restore failed', 'error_message': 'detach failed'}
        for command, kwargs in ((custom.repair_and_restore, {}),
                                (custom.repair_button, {'button_command': 'fstab', 'yes': True})):
            with self.subTest(command=command.__name__):
                result = self._run_nested_command(command, restore_out=restore_out, **kwargs)

                self.assertEqual('ERROR', result['status'])
                self.assertEqual('restore failed', result['message'])
                self.assertEqual('detach failed', result['error_message'])
                self.assertIn('create warning', result['warnings'])
                self.assertFalse(TestCommandHelper.instances[0].nested_script_failed)

        # The child's own payload is not mutated.
        self.assertNotIn('warnings', restore_out)

    def test_run_exception_keeps_warnings(self):
        TestCommandHelper.instances = []
        create_result = {'repair_vm_name': 'repair-vm', 'copied_disk_name': 'disk-copy',
                         'repair_resource_group': 'repair-rg', 'warnings': ['create warning']}
        with mock.patch('azext_vm_repair.custom.get_vm_by_aaz', side_effect=RuntimeError('telemetry unavailable')), \
                mock.patch('azext_vm_repair.custom._check_existing_rg', return_value=False), \
                mock.patch('azext_vm_repair.custom.create', return_value=create_result), \
                mock.patch('azext_vm_repair.custom.run', side_effect=RuntimeError('run exploded')), \
                mock.patch('azext_vm_repair.custom._clean_up_resources'):
            result = custom.repair_and_restore(mock.MagicMock(), 'source-vm', 'source-rg')

        self.assertEqual('ERROR', result['status'])
        self.assertEqual(['create warning'], result['warnings'])


if __name__ == '__main__':
    unittest.main()
